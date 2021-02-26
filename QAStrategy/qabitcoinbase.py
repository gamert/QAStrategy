# coding=utf-8

"""
bitcoin_base
"""
import uuid
import datetime
import json
import os
import threading
import requests
import pandas as pd
import pymongo
from qaenv import (eventmq_ip, eventmq_password, eventmq_port,
                   eventmq_username, mongo_ip)

import QUANTAXIS as QA
from QUANTAXIS.QAARP import QA_Risk, QA_User
from QUANTAXIS.QAEngine.QAThreadEngine import QA_Thread
from QUANTAXIS.QAUtil.QAParameter import MARKET_TYPE, RUNNING_ENVIRONMENT, ORDER_DIRECTION, OUTPUT_FORMAT, DATASOURCE
from QAPUBSUB.consumer import subscriber_topic, subscriber_routing, subscriber
from QAPUBSUB.producer import publisher_routing, publisher_topic
from QAStrategy.qactabase import QAStrategyCTABase
from QIFIAccount import QIFI_Account

# BTC 交易策略...
class QAStrategyBitcoinBase(QAStrategyCTABase):

    def __init__(self, code=['OKEX.OKB-USDT'], frequence='1min', strategy_id='QA_STRATEGY', risk_check_gap=1, portfolio='default',
                 start='2021-02-01', end='2021-02-23', send_wx=False, market_type='bitcoin_okex',
                 data_host=eventmq_ip, data_port=eventmq_port, data_user=eventmq_username, data_password=eventmq_password,
                 trade_host=eventmq_ip, trade_port=eventmq_port, trade_user=eventmq_username, trade_password=eventmq_password,
                 taskid=None, mongo_ip=mongo_ip):
        super().__init__(code=code, frequence=frequence, strategy_id=strategy_id, risk_check_gap=risk_check_gap, portfolio=portfolio,
                         start=start, end=end, send_wx=send_wx,
                         data_host=eventmq_ip, data_port=eventmq_port, data_user=eventmq_username, data_password=eventmq_password,
                         trade_host=eventmq_ip, trade_port=eventmq_port, trade_user=eventmq_username, trade_password=eventmq_password,
                         taskid=taskid, mongo_ip=mongo_ip)

        self.code = code
        self.send_wx = send_wx
    # 修改市场类型:
    def _init_market_type(self):
        self.market_type = MARKET_TYPE.CRYPTOCURRENCY

    # code = ['OKEX.1INCH-USDT']
    def subscribe_data(self, code, frequence, data_host, data_port, data_user, data_password):
        """[summary]

        Arguments:
            code {[type]} -- [description]
            frequence {[type]} -- [description]
        """
        if frequence.endswith('min'):
            self.sub = subscriber(exchange='realtime_{}_{}'.format(
                frequence, code), host=data_host, port=data_port, user=data_user, password=data_password)
            self.sub.callback = self.callback
        # elif frequence.endswith('s'):
        #     import re
        #     self._num_cached = 2*int(re.findall(r'\d+', self.frequence)[0])
        #     self.sub = subscriber_routing(
        #         exchange='CTPX', routing_key=code, host=data_host, port=data_port, user=data_user, password=data_password)
        #     self.sub.callback = self.second_callback
        elif frequence.endswith('tick'):
            self._num_cached = 1
            self.sub = subscriber_routing(
                exchange='tick', routing_key=code, host=data_host, port=data_port, user=data_user, password=data_password)
            self.sub.callback = self.tick_callback

    def on_sync(self):
        if self.running_mode != 'backtest':
            self.pubacc.pub(json.dumps(self.acc.message),
                            routing_key=self.strategy_id)

    def _debug_sim(self):
        self.running_mode = 'sim'

        last_day = QA.QA_util_get_last_day(QA.QA_util_get_real_date(str(datetime.date.today())))

        if self.frequence.endswith('min'):
            self._old_data = self._fetch_get_btc_min(self.code, last_day, str(datetime.datetime.now()), self.frequence)[:-1];##.set_index(['datetime', 'code'])
            # self._old_data = self._old_data.assign(volume=self._old_data.trade).loc[:, [
            #     'open', 'high', 'low', 'close', 'volume']]
        else:
            self._old_data = pd.DataFrame()
        print("self._old_data: len = ", len(self._old_data))
        # 重排？
        self._old_data = self._old_data.loc[:, [
            'open', 'high', 'low', 'close', 'volume']]
        # 指定实时数据库..
        self.database = pymongo.MongoClient(mongo_ip).QAREALTIME
        # 账户Collection
        self.client = self.database.account
        self.subscriber_client = self.database.subscribe
        # 创建策略账户(一个基于快期DIFF协议的QA实时账户协议)...
        self.acc = QIFI_Account(
            username=self.strategy_id, password=self.strategy_id, trade_host=mongo_ip)
        self.acc.initial()
        self.acc.on_sync = self.on_sync
        # 分发？
        self.pub = publisher_routing(exchange='QAORDER_ROUTER', host=self.trade_host,
                                     port=self.trade_port, user=self.trade_user, password=self.trade_password)
        self.pubacc = publisher_topic(exchange='QAAccount', host=self.trade_host,
                                      port=self.trade_port, user=self.trade_user, password=self.trade_password)
        # 注册一个MQ
        self.subscribe_data(self.code, self.frequence, self.data_host,
                            self.data_port, self.data_user, self.data_password)

        self.database.strategy_schedule.job_control.update(
            {'strategy_id': self.strategy_id},
            {'strategy_id': self.strategy_id, 'taskid': self.taskid,
             'filepath': os.path.abspath(__file__), 'status': 200}, upsert=True)

        # threading.Thread(target=, daemon=True).start()
        self.sub.start()

    def run(self):
        while True:
            pass

    def init_strategy(self):
        print("init_strategy")
        pass

    def on_1min_bar(self):
        print("on_1min_bar")
        pass

    def on_bar(self, bar):
        print("on_bar")
        pass

    # 返回DF
    def _fetch_get_btc_min(self, codes, start, end, level='1min'):
        return QA.QA_fetch_cryptocurrency_min_adv(codes, start, end, level).data

    def _fetch_btc_data(self, code, start, end, frequence, output=OUTPUT_FORMAT.DATAFRAME):
        """一个统一的获取k线的方法
        如果使用mongo,从本地数据库获取,失败则在线获取

        Arguments:
            code {str/list} -- 期货/股票的代码
            start {str} -- 开始日期
            end {str} -- 结束日期
            frequence {enum} -- 频率 QA.FREQUENCE
            market {enum} -- 市场 QA.MARKET_TYPE
            source {enum} -- 来源 QA.DATASOURCE
            output {enum} -- 输出类型 QA.OUTPUT_FORMAT
        """
        res = QA.QA_fetch_cryptocurrency_min_adv(
            code,
            # code=[
            #     'OKEX.BTC-USDT',
            #     'OKEX.ETH-USDT',
            # ],
            start, #='2017-10-01',
            end, #='2020-05-28 18:10:00',
            frequence, #='60min'
        )
        # print(data2.data)
        # data_4h = QA.QA_DataStruct_CryptoCurrency_min(data2.resample('4h'))
        # print(data_4h.data)

        # try:
        #     res = QAQueryAdv.QA_fetch_stock_min_adv(
        #         code, start, end, frequence=frequence)
        # except:
        #     res = None


        if output is OUTPUT_FORMAT.DATAFRAME:
            return res.data
        elif output is OUTPUT_FORMAT.DATASTRUCT:
            return res
        elif output is OUTPUT_FORMAT.NDARRAY:
            return res.to_numpy()
        elif output is OUTPUT_FORMAT.JSON:
            return res.to_json()
        elif output is OUTPUT_FORMAT.LIST:
            return res.to_list()

    # 获取his数据后
    def debug(self):
        self.running_mode = 'backtest'
        self.database = pymongo.MongoClient(mongo_ip).QUANTAXIS
        user = QA_User(username="admin", password='admin')
        port = user.new_portfolio(self.portfolio)
        self.acc = port.new_accountpro(
            account_cookie=self.strategy_id, init_cash=self.init_cash, market_type=self.market_type, frequence= self.frequence)

        self.init_strategy()
        print(self.acc)

        print(self.acc.market_type)
        data = self._fetch_btc_data(self.code, self.start, self.end,
                                    frequence=self.frequence, output=QA.OUTPUT_FORMAT.DATASTRUCT)

        data.data.apply(self.x1, axis=1)

if __name__ == '__main__':
    ##'OKEX.BTC-USDT' 'OKEX.BTC-USDT'
    #QAStrategyBitcoinBase(code=['OKEX.1INCH-USDT']).debug()
    QAStrategyBitcoinBase(code='OKEX.1INCH-USDT').run_sim()