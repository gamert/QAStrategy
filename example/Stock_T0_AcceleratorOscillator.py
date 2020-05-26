import pandas as pd
import numpy as np
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


"""
AcceleratorOscillator是一种短线日内交易策略

"""
class AcceleratorOscillatorStrategy(QAStrategyStockBase):
    #
    def handle_bar_(self, bar):
        code = bar.name[1]
        if(bar['close'] > self.day_high):
            self.day_high = bar['close']
        if (bar['close'] < self.day_low):
            self.day_low = bar['close']

        shares = self.portfolio.available_cash #取得当前资金
        curPosition = 	self.portfolio.positions[code].amount#获取持股数量
        # AC值自下而上穿越零轴时全仓买进
        if self.AC[-1]>0 and self.AC[-2]<0:
            self.do_buy(code, shares)
        # AC值自上而下下穿零轴时清仓
        if self.AC[-1]<0 and self.AC[-2]>0 and curPosition>0:
            self.do_sell(code, 0)
        self.P = bar['close']

    def do_sell(self,code,price,volume=1000):
        self.send_order('SELL', 'CLOSE', code=code, price=price, volume=volume)

    def do_buy(self,code,price,volume=1000):
        self.send_order('BUY', 'OPEN', code=code, price=price, volume=volume)

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

        N = 30
        last_dayN = QA.QA_util_get_last_day(today, n=N+1)

        # 取得过去20日
        dataN = QA.QA_fetch_stock_day_adv(self.code, last_dayN, last_day).to_qfq()
        # high = dataN.high.iloc[-1]  # 前一日的最高价
        # low = dataN.low.iloc[-1]  # 前一日的最低价
        # close = dataN.close.iloc[-1]  # 前一日的收盘价
        high = self.dataN['high'] #获取最高价数据
        low = self.dataN['low'] #获取最低价数据
        MP = (high + low)/2 #计算MP = (high + low)/2

        # AO — AO动能指数。
        # AO = SMA (子午价，5)-SMA（子午价，34） AC = AO-SMA(AO, 5)
        AO = QA.MA(MP, self.nday) - QA.MA(MP, self.mday)
        self.AC = AO - QA.MA(AO, self.nday)

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

        self.nday = 5  # 短期值
        self.mday = 20  # 长期值
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
    s = AcceleratorOscillatorStrategy(code='300142', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()
    s.perf()

