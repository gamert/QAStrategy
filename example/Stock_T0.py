import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


class MStockStrategy(QAStrategyStockBase):
    #

    # 如果使用简单的基于macd的金叉死叉买入
    # debug是截断到100的数据
    #
    def handle_bar_macd(self,data):
        # 全部重算? 还是累积计算?
        #print(self.get_positions('000002'))
        res = QA.QA_indicator_MACD(self.market_data)
        print(res.iloc[-1])
        #
        if res.DIF[-1] > res.DEA[-1]:
            print('LONG')

        else:
            print('SHORT')

    def risk_check(self):
        pass

    def on_bar(self, data):
        code = data.name[1]
        # print(data)
        # print(self.get_positions('000001'))
        # print(self.market_data)
        #
        # print('---------------under is 当前全市场的market_data --------------')
        #
        # print(self.get_current_marketdata())
        # print('---------------under is 当前品种的market_data --------------')
        # print(self.get_code_marketdata(code))
        # print(code)
        # print(self.running_time)
        self.handle_bar_macd(data)

        #

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
        pass

    def on_dailyclose(self):
        pass

if __name__ == '__main__':

    start_min = '2019-07-05'
    end_min = '2019-07-10'
    # 使用t0模式进行回测,使用strategy_id='x_t0'
    # s = MStockStrategy(code='000002', frequence='5min', start=start_min, end=end_min, strategy_id='x_t0')
    # s.debug_t0()

    s = MStockStrategy(code='000002', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    # 回测(不存储账户数据的模式)
    s.debug()

    # 回测(存储账户数据的模式)
    # s.run_backtest()

    # s.run() # 空执行...

    # 模拟盘数据需要使用分钟数据
    # 1. 首先从库中取得起始min到最近的min1数据
    # 2. 订阅数据更新
    # 实时模拟(阻塞形式不能同时多开很多个)
    s = MStockStrategy(code='000002', frequence='5min', start=start_min, end=end_min, strategy_id='x_sim')
    s.run_sim()

    # 实时模拟(非阻塞模式可以同时开很多个)
    s.debug_sim()