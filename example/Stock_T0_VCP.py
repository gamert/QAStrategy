import pandas as pd
import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


"""
VCP是一种长期跟踪并在某日放量突破时的进场模式:
类型：日内趋势追踪+反转策略
周期：20天
交易规则：

"""
class VCPStrategy(QAStrategyStockBase):
    #

    def handle_bar_(self, bar):
        code = bar.name[1]
        if(bar['close'] > self.day_high):
            self.day_high = bar['close']
        if (bar['close'] < self.day_low):
            self.day_low = bar['close']

        N = 20
        # 14 * 5 = 70
        if len(self._market_data) < (N+1):
            return
        data = bar
        #TR = Max(H−L, H−P, P−L )  ，其中H为当日日内最高价，L为当日日内最低价，P为前一日收盘价。
        atr = self.ATR['ATR'][-1]
        if ( pd.np.isnan(atr)):
            return
        #
        #其中value * 1 % 即为总资产的1 %，考虑到国内最小变化量是0.01元，1手是100股，所以1ATR即为持1股股票的资产最大变动，那么买入
        # 1Unit单位的股票，使得总资产当天震幅不超过1 %

        price = bar['close']
        # 取整到100股
        value = self.init_cash
        Unit = (value * 0.01) / atr
        volume = int(Unit / price / 100 + 0.5) * 100;
        order_last = self.get_last_order()

        # 系统一：
        # I 、若当前价格高于过去20日的最高价，则买入一个Unit
        # II 、加仓：若股价在上一次买入的基础上上涨了0.5ATR，则加仓一个 Unit 。
        if(price > self.hhv20[-1]):
            if(order_last == None or (order_last.price + 0.5*atr) < price):
                print(self.running_time, bar.close, self.day_low)
                self.do_buy(code, price=price, volume=volume)
            pass

        # 系统二：
        # I 、若当前价格高于过去 55 日的最高价，则买入一个Unit
        # II 、加仓：若股价在上一次买入的基础上上涨了0.5N ，则加仓一个 Unit 。
        if(price > self.hhv55[-1]):
            if(order_last == None or (order_last.price + 0.5*atr) < price):
                print(self.running_time, bar.close, self.day_low)
                self.do_buy(code, price=price, volume=volume)
            pass

        # 卖出...

        # 若某只股票 A 的ATR 为 1，20  日最高价为40 。
        # 则当股价突破40 时买入一个Unit ，当股价突破40+0.5×1=40.5 时加仓一个 Unit 。
        # 当股价突破40.5+0.5×1=41 时加仓一个 Unit 。
        self.P = bar['close']

    def do_sell(self,code,price,volume=1000):
        self.send_order('SELL', 'CLOSE', code=code, price=price, volume=volume)

    def do_buy(self,code,price,volume=1000):
        self.send_order('BUY', 'OPEN', code=code, price=price, volume=volume)

    def get_last_order(self):
        orders = self.acc.get_orders()
        order_last = orders[-1] if len(orders) > 0 else None
        return order_last

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
        dataN = QA.QA_fetch_stock_day_adv(self.code, last_day20, last_day).to_qfq()
        # high = dataN.high.iloc[-1]  # 前一日的最高价
        # low = dataN.low.iloc[-1]  # 前一日的最低价
        close = dataN.close.iloc[-1]  # 前一日的收盘价

        # 计算过去20天的最高值...
        self.hhv20 = QA.HHV(dataN['high'], N)
        self.ATR = QA.QA_indicator_ATR(dataN, N)

        N = 55
        last_day55 = QA.QA_util_get_last_day(today, n=N+1)
        data55 = QA.QA_fetch_stock_day_adv(self.code, last_day55, last_day).to_qfq()
        self.hhv55 = QA.HHV(data55['high'], N)


        self.P = close  #
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
        #  从start开始

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

    start_min = '2020-02-11'
    end_min = '2020-05-22'
    s = VCPStrategy(code='300142', frequence='1min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()
    s.perf()

