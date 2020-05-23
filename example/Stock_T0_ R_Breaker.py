import pandas as pd
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


"""
R-Breaker是一种短线日内交易策略
根据前一个交易日的收盘价、最高价和最低价数据通过一定方式计算出六个价位，从大到小依次为：
突破买入价、观察卖出价、反转卖出价、反转买入、观察买入价、突破卖出价。以此来形成当前交易
日盘中交易的触发条件。
追踪盘中价格走势，实时判断触发条件。具体条件如下：
突破
在空仓条件下，如果盘中价格超过突破买入价，则采取趋势策略，即在该点位开仓做多。
在空仓条件下，如果盘中价格跌破突破卖出价，则采取趋势策略，即在该点位开仓做空。
反转
持多单，当日内最高价超过观察卖出价后，盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，采取反转策略，即在该点位反手做空。
持空单，当日内最低价低于观察买入价后，盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，采取反转策略，即在该点位反手做多。
设定止损条件。当亏损达到设定值后，平仓。
选用了SHFE的rb2010 在2019-10-1 15:00:00 到 2020-04-16 15:00:00 进行回测。
注意： 
1：为回测方便，本策略使用了on_bar的一分钟来计算，实盘中可能需要使用on_tick。
2：实盘中，如果在收盘的那一根bar或tick触发交易信号，需要自行处理，实盘可能不会成交。
3：本策略使用在15点收盘时全平的方式来处理不持有隔夜单的情况，实际使用中15点是无法平仓的。
"""
class RBreakerStrategy(QAStrategyStockBase):
    #

    def handle_bar_(self, bar):
        code = bar.name[1]
        if(bar['close'] > self.day_high):
            self.day_high = bar['close']
        if (bar['close'] < self.day_low):
            self.day_low = bar['close']

        # 获取止损价
        STOP_LOSS_PRICE = self.stopLossPrice
        bBreak = self.bBreak
        sSetup = self.sSetup
        sEnter = self.sEnter
        bEnter = self.bEnter
        bSetup = self.bSetup
        sBreak = self.sBreak
        data = bar

        # 当日最多可买入？
        # 高开要保护？ 前15分钟高开回落?
        # 突破: 如果今天没有买入？
        unit = 500
        print(bar.close,bBreak,sBreak)
        if bar.close > bBreak:
            # 在空仓的情况下，如果盘中价格超过突破买入价，
            # 则采取趋势策略，即在该点位开仓做多
            print("空仓,盘中价格超过突破买入价: 开仓做多")
            # if (self.positions.moneypreset > 0):
            if self.positions.volume_long_today == 0:  # 今天没有买过?
                self.do_buy(code, bar['close'])
            else:
                # 止盈...
                pass
        elif bar.close < sBreak:
            # 在空仓的情况下，如果盘中价格跌破突破卖出价，
            # 则采取趋势策略，即在该点位开仓做空
            print("空仓,盘中价格跌破突破卖出价: 开仓做空")
            # self.volume_long_his >= amount
            if self.positions.volume_long_his > 0:  # 今天没有卖过？
                self.do_sell(code, price=bar['close'])
            else:
                # 达到价差，买回...
                pass

        # 止盈止损...
        if self.positions.volume_long_his > 0 :
            if(self.positions.position_price_long / bar.close < 0.04):
                print(bar,'止损')
                self.do_sell(code, bar['close'])
            elif(self.positions.position_price_long / bar.close > 1.08):
                print(bar,'止盈')
                self.do_sell(code, bar['close'])

        # 反转:
        if self.positions.volume_long_his > 0:  # 多头持仓
            # 当日最高价?
            if self.day_high > sSetup and bar.close < sEnter:
                # 多头持仓,当日内最高价超过观察卖出价后，
                # 盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，
                # 采取反转策略，即在该点位反手做空
                print(bar,"多头持仓,当日内最高价超过观察卖出价后跌破反转卖出价: 反手做空")
                self.do_sell(code, price=bar['close'])
        elif self.positions.volume_long_today == 0:  # 空头持仓
            if self.day_low < bSetup and bar.close > bEnter:
                # 空头持仓，当日内最低价低于观察买入价后，
                # 盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，
                # 采取反转策略，即在该点位反手做多
                print(bar,"空头持仓,当日最低价低于观察买入价后超过反转买入价: 反手做多")
                self.do_buy(code, price=bar['close'])

        # 15点收盘全部平仓。
        # if context.now.hour == 15:
        #     print(context.now)
        #     print('close all')
        #     order_close_all()
    def do_sell(self,code,price):
        self.send_order('SELL', 'CLOSE', code=code, price=price, volume=1)

    def do_buy(self,code,price):
        self.send_order('BUY', 'OPEN', code=code, price=price, volume=1)

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

    # def on_1min_bar(self):
    #     print(self.get_positions('000001'))
    #     print(self.market_data)
    #     pass

    def on_tick(self, tick):
        print(self.market_data)
        pass

    def on_dailyopen(self):
        #根据前一日的价格计算...
        today = QA.QA_util_get_next_day(str(self.running_time)[0:10]) if self.running_time !="" else self.start
        last_day = QA.QA_util_get_last_day(today)
        data = QA.QA_fetch_stock_day_adv(self.code, last_day, last_day).to_qfq()
        high = data.high.iloc[0]  # 前一日的最高价
        low = data.low.iloc[0]  # 前一日的最低价
        close = data.close.iloc[0]  # 前一日的收盘价
        pivot = (high + low + close) / 3  # 枢轴点
        self.bBreak = high + 2 * (pivot - low)  # 突破买入价
        self.sSetup = pivot + (high - low)  # 观察卖出价
        self.sEnter = 2 * pivot - low  # 反转卖出价
        self.bEnter = 2 * pivot - high  # 反转买入价
        self.bSetup = pivot - (high - low)  # 观察买入价
        self.sBreak = low - 2 * (high - pivot)  # 突破卖出价

        self.position_buy = 0;
        self.position_sell = 0;

        self.day_high = 0
        self.day_low = 99999999

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
    end_min = '2020-05-21'
    s = RBreakerStrategy(code='300142', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()
    s.perf()

