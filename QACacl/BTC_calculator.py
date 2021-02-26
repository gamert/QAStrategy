# coding=utf-8

"""
btc_cacl
"""
import json
import pandas as pd
import threading
import time

from QAPUBSUB.consumer import subscriber, subscriber_routing
from QAPUBSUB.producer import publisher, publisher_topic
from QUANTAXIS.QAEngine.QAThreadEngine import QA_Thread
from QUANTAXIS import QA_indicator_BOLL

# 每个Cacl负责一个频率的数据保存和一组计算结果(对应一组Indicator)
#
from QACacl.StrategyCacl import StrategyCacl_BOLL





class BTCCaluator(QA_Thread):
    def __init__(self, code: list, frequency='5min', strategy="BTCEnhance", init_data=None):
        """
        :param code:
        :param indicator_fun:
        :param frequency:
        :param strategy:
        """
        super().__init__()
        if isinstance(frequency, float):
            self.frequency = int(frequency)
        elif isinstance(frequency, str):
            _frequency = frequency.replace('min', '')
            if str.isnumeric(_frequency):
                self.frequency = int(_frequency)
            else:
                print("unknown frequency: %s" % frequency)
                return
        elif isinstance(frequency, int):
            self.frequency = frequency
        else:
            print("unknown frequency: %s" % frequency)
            return
        self.market_data = init_data
        self.stock_code = code
        self.strategy = strategy

        # 接收stock 重采样的数据
        self.sub = subscriber(
            host=self.data_host, exchange='realtime_{}_{}_min'.format(code,self.frequency))
        self.sub.callback = self.stock_min_callback
        # 发送stock indicator result
        # self.pub = publisher_topic(
        #     host=self.data_host, exchange='realtime_stock_calculator_{}_{}_min'.format(self.strategy, self.frequency))
        threading.Thread(target=self.sub.start).start()

        print("REALTIME_STOCK_CACULATOR INIT, strategy: %s frequency: %s" % (self.strategy, self.frequency))

    def unsubscribe(self, item):
        # remove code from market data
        pass

    def stock_min_callback(self, a, b, c, data):
        latest_data = json.loads(str(data, encoding='utf-8'))
        # print("latest data", latest_data)
        context = pd.DataFrame(latest_data)

        # merge update
        if self.market_data is None:
            self.market_data = context
        else:
            self.market_data.update(context)
        # print(self.market_data)
        res_buy, res_sell = StrategyCacl_BOLL(self.market_data)

        #

        # self.pub.pub(json.dumps(res_buy.to_dict(), cls=NpEncoder), routing_key="calculator.buy")
        # self.pub.pub(json.dumps(res_sell.to_dict(), cls=NpEncoder), routing_key="calculator.sell")

    def run(self):
        import datetime
        while True:
            print(datetime.datetime.now(), "realtime stock calculator is running")
            time.sleep(1)


if __name__ == '__main__':
    import QUANTAXIS as QA
    from QUANTAXIS import SUM
    code_list = ['000001', '000002']  # TODO HS300 STOCK CODE LIST
    start_date = '2019-09-29'
    end_date = '2019-09-30'
    init_min_data = QA.QA_fetch_stock_min_adv(code_list, start_date, end_date)
    if init_min_data is not None:
        init_min_data = init_min_data.data
    from QUANTAXIS import QA_indicator_BOLL
    BTCCaluator(
        code_list=code_list, frequency='5min', strategy="HS300Enhance", init_data=init_min_data
    ).start()
