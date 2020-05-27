import pandas as pd
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


"""
ADX指标由Welles Wilder在《New Concepts in Technical Trading Systems》中提出。
Average Directional Index(ADX):用于判定价格出现强烈趋势
ADX计算基于给定时间内的价格范围扩展的移动平均。默认14bars，当然其他周期也是可以的。ADX可以用于各类交易品种：股票、共同基金、ETF(Exchange Traded Funds)、期货。
ADX可画成一条介于0和100的单线。ADX本身五防线，它指明价格上下的趋势强度。ADX指标常与两条DMI(Directional Movement Indicator)线在同一个窗口展示。

"""
class ADXStrategy(QAStrategyStockBase):
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

        adx = QA.talib.ADX(high, low, close, timeperiod=self.adx_period)
        plus_di = QA.talib.PLUS_DI(high, low, close, timeperiod=self.dmi_period)
        minus_di = QA.talib.MINUS_DI(high, low, close, timeperiod=self.dmi_period)
        short_ma = QA.talib.SMA(close, timeperiod=self.ma_short_period)
        long_ma = QA.talib.SMA(close, timeperiod=self.ma_long_period)

        # 仓位管理和控制？ kelly?
        #
        if pos is None and symbol not in self.dict_open_cum_days \
                and (short_ma[-1] > long_ma[-1] and short_ma[-2] < long_ma[-2] \
                     and adx[-1] > adx[-2] and plus_di[-1] > minus_di[-1]):
            pass
        # 有开仓机会则设置已开仓的交易天数
        self.P = bar['close']

    def do_sell(self,code,price,volume=1000):
        self.send_order('SELL', 'CLOSE', code=code, price=price, volume=volume)

    def do_buy(self,code,price,volume=1000):
        self.send_order('BUY', 'OPEN', code=code, price=price, volume=volume)


    def fixation_stop_profit_loss(self, bar):
        """
        功能：固定止盈、止损,盈利或亏损超过了设置的比率则执行止盈、止损
        """
        if self.is_fixation_stop == 0:
            return

        symbol = bar.exchange + '.' + bar.sec_id
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
        symbol = bar.exchange + '.' + bar.sec_id

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

        # ;ADX、DMI指标数据周期
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
    s = ADXStrategy(code='300142', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()
    s.perf()

