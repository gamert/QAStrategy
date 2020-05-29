import logging
import logging.config
import configparser
import csv
import datetime

import arrow
import pandas as pd
import numpy as np
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase

'''
##简单的基于ta-lib的ATR标策略示例
真实波幅（ATR average true range）主要应用于了解股价的震荡幅度和节奏，在窄幅整理行情中用于寻找突破时机。
通常情况下股价的波动幅度会保持在一定常态下，但是如果有主力资金 进出时，股价波幅往往会加剧。另外，在股价 横盘整理、
波幅减少到极点时，也往往会产生变盘行情。真实波幅（ATR）正是基于这种原理而设计的指标。
计算方法：
1.TR= ∣最高价-最低价∣和∣最高价-昨收∣ 和 ∣昨收-最低价∣ 三者中的最大值
2.真实波幅（ATR）= TR的N日简单移动平均
3.参数N设置为14日
使用方法： 如果当前价格比之前的价格高一个ATR的涨幅，买入股票 如果之前的价格比当前价格高一个ATR的涨幅，卖出股票

'''
EPS = 1e-6
INIT_LOW_PRICE = 10000000
INIT_HIGH_PRICE = -1
INIT_CLOSE_PRICE = 0

class ATRStrategy(QAStrategyStockBase):

    @classmethod
    def read_ini(cls, ini_name):
        """
        功能：读取策略配置文件
        """
        cls.cls_config = configparser.ConfigParser()
        cls.cls_config.read(ini_name)

    @classmethod
    def get_stock_pool(cls, csv_file):
        """
        功能：获取股票池中的代码
        """
        csvfile = open(csv_file, 'r')
        reader = csv.reader(csvfile)
        for line in reader:
            cls.cls_stock_pool.append(line[0])

        return

    def utc_strtime(self, utc_time):
        """
        功能：utc转字符串时间
        """
        str_time = '%s' % arrow.get(utc_time).to('local')
        str_time.replace('T', ' ')
        str_time = str_time.replace('T', ' ')
        return str_time[:19]

    def get_para_conf(self):
        """
        功能：读取策略配置文件para(自定义参数)段落的值
        """
        if self.cls_config is None:
            return

        self.atr_period = self.cls_config.getint('para', 'atr_period')
        self.buy_multi_atr = self.cls_config.getfloat('para', 'buy_multi_atr')
        self.sell_multi_atr = self.cls_config.getfloat('para', 'sell_multi_atr')

        self.hist_size = self.cls_config.getint('para', 'hist_size')
        self.open_vol = self.cls_config.getint('para', 'open_vol')

        self.open_max_days = self.cls_config.getint('para', 'open_max_days')

        self.is_fixation_stop = self.cls_config.getint('para', 'is_fixation_stop')
        self.is_movement_stop = self.cls_config.getint('para', 'is_movement_stop')

        self.stop_fixation_profit = self.cls_config.getfloat('para', 'stop_fixation_profit')
        self.stop_fixation_loss = self.cls_config.getfloat('para', 'stop_fixation_loss')

        self.stop_movement_profit = self.cls_config.getfloat('para', 'stop_movement_profit')

        return

    def init_strategy(self):
        """
        功能：策略启动初始化操作
        """
        if self.cls_mode == gm.MD_MODE_PLAYBACK:
            self.cur_date = self.cls_backtest_start
            self.end_date = self.cls_backtest_end
        else:
            self.cur_date = datetime.date.today().strftime('%Y-%m-%d') + ' 08:00:00'
            self.end_date = datetime.date.today().strftime('%Y-%m-%d') + ' 16:00:00'

        self.dict_open_close_signal = {}
        self.dict_entry_high_low = {}
        self.get_last_factor()
        self.init_data()
        self.init_entry_high_low()
        return

    def init_data(self):
        """
        功能：获取订阅代码的初始化数据
        """
        for ticker in self.cls_stock_pool:
            # 初始化开仓操作信号字典
            self.dict_open_close_signal.setdefault(ticker, False)
            self.dict_prev_close.setdefault(ticker, None)

            daily_bars = self.get_last_n_dailybars(ticker, self.hist_size - 1, self.cur_date)
            if len(daily_bars) <= 0:
                continue

            end_daily_bars = self.get_last_n_dailybars(ticker, 1, self.end_date)
            if len(end_daily_bars) <= 0:
                continue

            if ticker not in self.dict_last_factor:
                continue

            end_adj_factor = self.dict_last_factor[ticker]
            high_ls = [data.high * data.adj_factor / end_adj_factor for data in daily_bars]
            high_ls.reverse()
            low_ls = [data.low * data.adj_factor / end_adj_factor for data in daily_bars]
            low_ls.reverse()
            cp_ls = [data.close * data.adj_factor / end_adj_factor for data in daily_bars]
            cp_ls.reverse()

            # 留出一个空位存储当天的一笔数据
            high_ls.append(INIT_HIGH_PRICE)
            high = np.asarray(high_ls, dtype=np.float)
            low_ls.append(INIT_LOW_PRICE)
            low = np.asarray(low_ls, dtype=np.float)
            cp_ls.append(INIT_CLOSE_PRICE)
            close = np.asarray(cp_ls, dtype=np.float)

            # 存储历史的high low close
            self.dict_price.setdefault(ticker, [high, low, close])

    def init_data_newday(self):
        """
        功能：新的一天初始化数据
        """
        # 新的一天，去掉第一笔数据,并留出一个空位存储当天的一笔数据
        for key in self.dict_price:
            if len(self.dict_price[key][0]) >= self.hist_size and self.dict_price[key][0][-1] > INIT_HIGH_PRICE:
                self.dict_price[key][0] = np.append(self.dict_price[key][0][1:], INIT_HIGH_PRICE)
            elif len(self.dict_price[key][0]) < self.hist_size and self.dict_price[key][0][-1] > INIT_HIGH_PRICE:
                # 未取足指标所需全部历史数据时回测过程中补充数据
                self.dict_price[key][0] = np.append(self.dict_price[key][0][:], INIT_HIGH_PRICE)

            if len(self.dict_price[key][1]) >= self.hist_size and self.dict_price[key][1][-1] < INIT_LOW_PRICE:
                self.dict_price[key][1] = np.append(self.dict_price[key][1][1:], INIT_LOW_PRICE)
            elif len(self.dict_price[key][1]) < self.hist_size and self.dict_price[key][1][-1] < INIT_LOW_PRICE:
                self.dict_price[key][1] = np.append(self.dict_price[key][1][:], INIT_LOW_PRICE)

            if len(self.dict_price[key][2]) >= self.hist_size and abs(
                            self.dict_price[key][2][-1] - INIT_CLOSE_PRICE) > EPS:
                self.dict_price[key][2] = np.append(self.dict_price[key][2][1:], INIT_CLOSE_PRICE)
            elif len(self.dict_price[key][2]) < self.hist_size and abs(
                            self.dict_price[key][2][-1] - INIT_CLOSE_PRICE) > EPS:
                self.dict_price[key][2] = np.append(self.dict_price[key][2][:], INIT_CLOSE_PRICE)

        # 初始化开仓操作信号字典
        for key in self.dict_open_close_signal:
            self.dict_open_close_signal[key] = False

        # 初始化前一笔价格
        for key in self.dict_prev_close:
            self.dict_prev_close[key] = None

        # 开仓后到当前的交易日天数
        keys = list(self.dict_open_cum_days.keys())
        for key in keys:
            if self.dict_open_cum_days[key] >= self.open_max_days:
                del self.dict_open_cum_days[key]
            else:
                self.dict_open_cum_days[key] += 1

    def init_entry_high_low(self):
        """
        功能：获取进场后的最高价和最低价,仿真或实盘交易启动时加载
        """
        pos_list = self.get_positions()
        high_list = []
        low_list = []
        for pos in pos_list:
            symbol = pos.exchange + '.' + pos.sec_id
            init_time = self.utc_strtime(pos.init_time)

            cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            daily_bars = self.get_dailybars(symbol, init_time, cur_time)

            high_list = [bar.high for bar in daily_bars]
            low_list = [bar.low for bar in daily_bars]

            if len(high_list) > 0:
                highest = np.max(high_list)
            else:
                highest = pos.vwap

            if len(low_list) > 0:
                lowest = np.min(low_list)
            else:
                lowest = pos.vwap

            self.dict_entry_high_low.setdefault(symbol, [highest, lowest])


    #
    def handle_bar_(self, bar):
        code = bar.name[1]
        if(bar['close'] > self.day_high):
            self.day_high = bar['close']
        if (bar['close'] < self.day_low):
            self.day_low = bar['close']

        self.movement_stop_profit_loss(bar)
        self.fixation_stop_profit_loss(bar)

        N = 20
        # 14 * 5 = 70
        if len(self._market_data) < (N+1):
            return
        data = bar

        # 取得市场数据...
        md = self.market_data();

        high = md['high'].values
        low = md['low'].values
        close = md['close'].values

        symbol = code

        if symbol in self.dict_prev_close and self.dict_prev_close[symbol] is None:
            self.dict_prev_close[symbol] = bar.open

        self.movement_stop_profit_loss(bar)
        self.fixation_stop_profit_loss(bar)

        pos = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)

        # 补充当天价格
        if symbol in self.dict_price:
            if self.dict_price[symbol][0][-1] < bar.high:
                self.dict_price[symbol][0][-1] = bar.high

            if self.dict_price[symbol][1][-1] > bar.low:
                self.dict_price[symbol][1][-1] = bar.low

            self.dict_price[symbol][2][-1] = bar.close

        if self.dict_open_close_signal[symbol] is False:
            # 当天未有对该代码开、平仓
            if symbol in self.dict_price:

                atr_index = talib.ATR(high=self.dict_price[symbol][0],
                                      low=self.dict_price[symbol][1],
                                      close=self.dict_price[symbol][2],
                                      timeperiod=self.atr_period)

                if pos is None and symbol not in self.dict_open_cum_days \
                        and (bar.close > self.dict_prev_close[symbol] + atr_index[-1] * self.buy_multi_atr):
                    # 有开仓机会则设置已开仓的交易天数
                    self.dict_open_cum_days[symbol] = 0

                    cash = self.get_cash()
                    cur_open_vol = self.open_vol
                    if cash.available / bar.close > self.open_vol:
                        cur_open_vol = self.open_vol
                    else:
                        cur_open_vol = int(cash.available / bar.close / 100) * 100

                    if cur_open_vol == 0:
                        print('no available cash to buy, available cash: %.2f' % cash.available)
                    else:
                        self.open_long(bar.exchange, bar.sec_id, bar.close, cur_open_vol)
                        self.dict_open_close_signal[symbol] = True
                        logging.info('open long, symbol:%s, time:%s, price:%.2f' % (symbol, bar.strtime, bar.close))
                elif pos is not None and (
                    bar.close < self.dict_prev_close[symbol] - atr_index[-1] * self.buy_multi_atr):
                    vol = pos.volume - pos.volume_today
                    if vol > 0:
                        self.close_long(bar.exchange, bar.sec_id, bar.close, vol)
                        self.dict_open_close_signal[symbol] = True
                        logging.info('close long, symbol:%s, time:%s, price:%.2f' % (symbol, bar.strtime, bar.close))

        if symbol in self.dict_prev_close:
            self.dict_prev_close[symbol] = bar.close

    def do_sell(self,code,price,volume=1000):
        self.send_order('SELL', 'CLOSE', code=code, price=price, volume=volume)

    def do_buy(self,code,price,volume=1000):
        self.send_order('BUY', 'OPEN', code=code, price=price, volume=volume)

    #
    def on_order_filled(self, order):
        symbol = order.name
        pos = self.get_position(symbol, order.side)
        if pos is None and self.is_movement_stop == 1:
            self.dict_entry_high_low.pop(symbol)

    def fixation_stop_profit_loss(self, bar):
        """
        功能：固定止盈、止损,盈利或亏损超过了设置的比率则执行止盈、止损
        """
        if self.is_fixation_stop == 0:
            return

        symbol = bar.name[1]
        pos = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        if pos is not None:
            if pos.fpnl > 0 and pos.fpnl / pos.cost >= self.stop_fixation_profit:
                self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)

                self.dict_open_close_signal[symbol] = True
                print(
                    'fixnation stop profit: close long, symbol:%s, time:%s, price:%.2f, vwap: %s, volume:%s' % (symbol,
                                                                                                                pos.vwap,
                                                                                                                pos.volume))
            elif pos.fpnl < 0 and pos.fpnl / pos.cost <= -1 * self.stop_fixation_loss:
                self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)
                self.dict_open_close_signal[symbol] = True
                print(
                    'fixnation stop loss: close long, symbol:%s, time:%s, price:%.2f, vwap:%s, volume:%s' % (symbol,


    def movement_stop_profit_loss(self, bar):
        """
        功能：移动止盈, 移动止盈止损按进场后的最高价乘以设置的比率与当前价格相比，
              并且盈利比率达到设定的盈亏比率时，执行止盈
        """
        if self.is_movement_stop == 0:
            return

        entry_high = None
        entry_low = None
        pos = self.get_position(bar.exchange, bar.sec_id, OrderSide_Bid)
        symbol = bar.name[1]

        is_stop_profit = True

        if pos is not None and pos.volume > 0:
            if symbol in self.dict_entry_high_low:
                if self.dict_entry_high_low[symbol][0] < bar.close:
                    self.dict_entry_high_low[symbol][0] = bar.close
                    is_stop_profit = False
                if self.dict_entry_high_low[symbol][1] > bar.close:
                    self.dict_entry_high_low[symbol][1] = bar.close
                [entry_high, entry_low] = self.dict_entry_high_low[symbol]

            else:
                self.dict_entry_high_low.setdefault(symbol, [bar.close, bar.close])
                [entry_high, entry_low] = self.dict_entry_high_low[symbol]
                is_stop_profit = False

            if is_stop_profit:
                # 移动止盈
                if bar.close <= (
                        1 - self.stop_movement_profit) * entry_high and pos.fpnl / pos.cost >= self.stop_fixation_profit:
                    if pos.volume - pos.volume_today > 0:
                        self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)
                        self.dict_open_close_signal[symbol] = True
                        print(
                            'movement stop profit: close long, symbol:%s, time:%s, price:%.2f, vwap:%.2f, volume:%s' % (
                                symbol,
                                bar.strtime, bar.close, pos.vwap, pos.volume))

            # 止损
            if pos.fpnl < 0 and pos.fpnl / pos.cost <= -1 * self.stop_fixation_loss:
                self.close_long(bar.exchange, bar.sec_id, 0, pos.volume - pos.volume_today)
                self.dict_open_close_signal[symbol] = True
                print(
                    'movement stop loss: close long, symbol:%s, time:%s, price:%.2f, vwap:%.2f, volume:%s' % (symbol,

    def risk_check(self):
        pass

    def on_bar(self, data):
        code = data.name[1]
        self.handle_bar_(data)
        # input()

    def on_5min_bar(self):
        print(self.get_positions('000001'))
        print(self.market_data)
        pass

    def on_tick(self, tick):
        print(self.market_data)
        pass

    def on_dailyopen(self):
        #根据前一日的价格计算...
        today = QA.QA_util_get_next_day(str(self.running_time)[0:10]) if self.running_time !="" else self.start
        last_day = QA.QA_util_get_last_day(today)

        N = 20
        last_day20 = QA.QA_util_get_last_day(today, n=N+1)

        # 取得过去20日
        self.dataN = QA.QA_fetch_stock_day_adv(self.code, last_day20, last_day).to_qfq()
        high = self.dataN.high.iloc[-1]  # 前一日的最高价
        low = self.dataN.low.iloc[-1]  # 前一日的最低价
        close = self.dataN.close.iloc[-1]  # 前一日的收盘价

        # 计算过去20天的最高值...
        self.hhv20 = QA.HHV(self.dataN['high'], N)
        self.ATR = QA.QA_indicator_ATR(self.dataN, N)

        self.P = close  #
        self.position_buy = 0;
        self.position_sell = 0;

        self.day_high = 0
        self.day_low = 99999999

        # ;ATR、DMI指标数据周期
        self.adx_period = 14
        self.dmi_period = 14
        self.ma_short_period = 5
        self.ma_long_period = 20

        self.is_fixation_stop = 0
        self.is_movement_stop = 1
        #移动盈利开始比率及固定盈利比率
        self.stop_fixation_profit = 0.35
        #亏损比率
        self.stop_fixation_loss = 0.068
        #移动止盈比率
        self.stop_movement_profit = 0.068
        # ;累计开仓距离当前的最大交易日
        # ;若开仓距今超过这个日期，则认为未开过仓
        self.open_max_days = 22
        # 历史数据长度
        self.hist_size = 30
        #开仓量
        self.open_vol = 5000
        pass

    def on_dailyclose(self):
        pass
    def user_init(self):
        """
        用户自定义的init过程
        """
        # 设置止损点数
        self.stopLossPrice = 50
        pass


    def perf(self):
        risk = QA.QA_Risk(self.account, benchmark_code='000300',
                       benchmark_type=QA.MARKET_TYPE.INDEX_CN)

        print(risk().T)
        self.account.save()
        risk.save()
        risk.plot_assets_curve()
        print(risk.profit_construct)


if __name__ == '__main__':

    start_min = '2020-05-11'
    end_min = '2020-05-22'
    s = ATRStrategy(code='300142', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()
    s.perf()

