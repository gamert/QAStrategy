import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase


class strategy(QAStrategyStockBase):
    def on_bar(self, data):
        print(data)
        print(self.get_positions('000001'))
        print(self.market_data)

        code = data.name[1]
        print('---------------under is 当前全市场的market_data --------------')

        print(self.get_current_marketdata())
        print('---------------under is 当前品种的market_data --------------')
        print(self.get_code_marketdata(code))
        print(code)
        # print(self.running_time)
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

if __name__ == '__main__':

    start_min = '2019-07-05'
    end_min = '2019-07-10'
    s = strategy(code='000002', frequence='5min', start=start_min, end=end_min, strategy_id='x')
    s.debug()
    # s.run_backtest()

    # s.run() # 空执行...

    # 模拟盘数据需要使用分钟数据
    # 1. 首先从库中取得起始min到最近的min1数据
    # 2. 订阅数据更新
    s.run_sim()

    # 使用t0模式进行回测
    # self.debug_t0()
    #
    # 回测(不存储账户数据的模式)
    # self.debug()
    #
    # 回测(存储账户数据的模式)
    # self.run_backtest()
    #
    # 实时模拟(阻塞形式
    # 不能同时多开很多个) self.run_sim()
    #
    # 实时模拟(非阻塞模式
    # 可以同时开很多个) self.debug_sim()