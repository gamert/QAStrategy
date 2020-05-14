import QUANTAXIS as QA
from QAStrategy.qastockbase import QAStrategyStockBase



class Stock_MACD(QAStrategyStockBase):
    def on_bar(self, bar):
        # print(data)
        print(self.get_positions('000001'))
        # print(self.market_data)
        #
        # code = data.name[1]
        # print('---------------under is 当前全市场的market_data --------------')
        #
        # print(self.get_current_marketdata())
        # print('---------------under is 当前品种的market_data --------------')
        # print(self.get_code_marketdata(code))
        # print(code)
        # #print(self.running_time)
        # input()
        self.on_bar_macd(bar)


    def on_bar_macd(self, bar):
        res = self.macd()
        print(res.iloc[-1])
        if res.DIF[-1] > res.DEA[-1]:
            print('LONG')
            if self.positions.volume_long == 0:
                self.send_order('BUY', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_short > 0:
                self.send_order('SELL', 'CLOSE', price=bar['close'], volume=1)
        else:
            print('SHORT')
            if self.positions.volume_short == 0:
                self.send_order('SELL', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_long > 0:
                self.send_order('BUY', 'CLOSE', price=bar['close'], volume=1)

    def macd(self,):
        return QA.QA_indicator_MACD(self.market_data)

    def on_bar_ma(self, bar):
        res = self.ma()
        print(res.iloc[-1])
        if res.MA2[-1] > res.MA5[-1]:
            print('LONG')
            if self.positions.volume_long == 0:
                self.send_order('BUY', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_short > 0:
                self.send_order('SELL', 'CLOSE', price=bar['close'], volume=1)

        else:
            print('SHORT')
            if self.positions.volume_short == 0:
                self.send_order('SELL', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_long > 0:
                self.send_order('BUY', 'CLOSE', price=bar['close'], volume=1)

    def ma(self, ):
        return QA.QA_indicator_MA(self.market_data, 2, 5)

    def risk_check(self):
        pass
        # pprint.pprint(self.qifiacc.message)


if __name__ == '__main__':
    # frequence='day'
    s = Stock_MACD(code=['000001', '000002'], frequence='5min', start='2019-01-01', end='2019-02-01', strategy_id='x')
    # s.debug()
    s.run_sim();
