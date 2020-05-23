# -*- coding: utf-8 -*-
"""
@author: yinxiuqu
@license: GNU General Public License v3.0
@contact: yinxiuqu@qq.com
@file: ma_strategy.py
@time: 19-1-26 上午7:50
@Software: PyCharm
"""
# 本文件定义均线策略(效果很差，几乎没有超额)
from datetime import datetime

import pandas as pd
import time
import QUANTAXIS as QA

# 获取全市场个股列表
market_list = list(QA.QA_fetch_stock_list_adv().code)


# 定义均线金叉、长期均线上扬、且离长期均线距离极小的选股函数
def ma_select(start, end, code_list=market_list, short=8, long=89, n=0.01):
    """
    :param code_list: 选股范围，默认全市场
    :param start: 选股起始日期，默认None为现在
    :param end: 选股终止日期，默认None为现在
    :param short: 短期均线
    :param long: 长期均线
    :param n: 收盘价高于均线的比例
    :return: 返回选后的股票列表及股票市场数据
    """
    # 取今天的日期
    now = datetime.now().strftime('%Y-%m-%d')

    if start is None:
        start = now

    # 向后取真实交易日
    start = QA.QA_util_get_real_date(date=start, towards=1)

    # 将start日期往前推long个交易日，便于计算长均线不留空
    start = QA.QA_util_get_last_day(start, long)

    if end is None:
        end = now

    # 向前取真实交易日
    end = QA.QA_util_get_real_date(end)

    # # 获取个股数据用于选股和回测
    # df = get_stock_day_QA(code=code_list, start=start, end=end)
    #
    # # 将行情数据转化为QA的DataStruct数据结构，以便于复权
    # data = QA.QA_DataStruct_Stock_day(df)
    # # 前复权(仅计算今天盘中数据时，不能复权，其他情况都做复权处理)
    # if end == now and QA.QA_util_if_trade(end) and \
    #         '09:30' < datetime.now().strftime('%H:%M') < '15:00' and start != end:
    #     data = data.to_qfq()

    data = QA.QA_fetch_stock_day_adv(code=code_list, start=start, end=end)
    data = data.to_qfq()

    # 计算长短均线
    ind_data = data.add_func(QA.QA_indicator_MA, short, long)
    ind_data[['close', 'open']] = data.data[['close', 'open']]

    # 去掉nan行
    ind_data = ind_data.dropna()

    # 筛选金叉的个股
    ind_data_buy = ind_data[(ind_data['MA'+str(short)] > ind_data['MA'+str(long)]) &
                            (ind_data['MA'+str(short)].shift(1) < ind_data['MA'+str(long)].shift(1))]
    # 筛选长线上扬的个股(今日MA89>前日MA89)
    ind_data_buy = ind_data_buy[ind_data_buy['MA'+str(long)] >= ind_data_buy['MA'+str(long)].shift(2)]
    # 筛选收盘价距离长期均线在控制范围内的个股
    # ind_data_buy = ind_data_buy[((-n)*ind_data_buy['MA'+str(long)] <=
    #                              ind_data_buy.close - ind_data_buy['MA'+str(long)]) &
    #                             (ind_data_buy.close - ind_data_buy['MA' + str(long)] <=
    #                              n*ind_data_buy['MA'+str(long)])]
    # 筛选收阴线的个股
    # ind_data_buy = ind_data_buy[ind_data_buy.close <= ind_data_buy.open]
    # 截取买股数据
    data_buy = data.reindex(ind_data_buy.index)
    # 筛选个股死叉信号
    ind_data_sell = ind_data[(ind_data['MA' + str(short)] < ind_data['MA' + str(long)]) &
                             (ind_data['MA' + str(short)].shift(1) > ind_data['MA' + str(long)]).shift(1)]
    # # 筛选收盘价跌破长期均线控制范围内的个股
    # ind_data_sell = ind_data_sell[((-n) * ind_data_sell['MA' + str(long)] >=
    #                                ind_data_sell.close - ind_data_sell['MA' + str(long)])]
    # 截取卖股数据
    data_sell = data.reindex(ind_data_sell.index)

    return data_buy, data_sell, data


# 定义均线策略回测函数
def ma_backtest(start, end, code_list=market_list, long=89, short=8, n=0.01, cash=10000000):
    """
    :param start: 回测开始日期
    :param end: 回测结束日期
    :param code_list: 参与回测的个股范围列表
    :param long: 长期均线参数
    :param short: 短期均线参数
    :param n: 离长期均线的范围比例
    :param cash: 初始资金
    :return: 回测结果
    """

    data_buy, data_sell, data = ma_select(start=start, end=end, code_list=code_list, short=short, long=long, n=n)
    date_range = data_buy.date | data_sell.date
    # 从日期上切齐数据，但个股上仍然有很多冗余数据
    data = data.select_time(date_range[0], date_range[-1])

    # 设置回测架构
    account = QA.QA_Account(strategy_name='MA_Strategy', user_cookie='yinxiuqu',
                            portfolio_cookie='up_or_down_cross', start=start, end=end)
    broker = QA.QA_BacktestBroker()
    account.reset_assets(cash)
    account.account_cookie = 'ma_strategy' + start + end + 'long:' + str(long) + 'short:' + str(short) + \
                             'init_cash:' + str(cash)

    for items in data.panel_gen:
        if items.date[0] in data_sell.date:
            for code in data_sell.select_day(items.date).code:
                if account.sell_available.get(code, 0) > 0:
                    order = account.send_order(
                        code=code,
                        time=items.date,
                        amount=account.sell_available.get(code, 0),
                        towards=QA.ORDER_DIRECTION.SELL,
                        price=0,
                        order_model=QA.ORDER_MODEL.MARKET,
                        amount_model=QA.AMOUNT_MODEL.BY_AMOUNT
                    )
                    if order:  # 能够成交时
                        broker.receive_order(QA.QA_Event(order=order, market_data=items.select_code(code)))
                        trade_mes = broker.query_orders(account.account_cookie, 'filled')
                        res = trade_mes.loc[order.account_cookie, order.realorder_id]
                        order.trade(res.trade_id, res.trade_price, res.trade_amount, res.trade_time)

        if items.date[0] in data_buy.date:
            # 从购买股票代码列表中减去已经购买了的股票代码列表
            real_buycode = list(set(data_buy.select_day(items.date).code) - set(account.sell_available.index))
            if len(real_buycode) != 0:
                cash_weight = 0.96/len(real_buycode)  # 用于购买每只股票的资金比例
            else:
                cash_weight = 0
            for code in real_buycode:
                order = account.send_order(
                    code=code,
                    time=items.date,
                    money=cash_weight * account.cash_available,
                    towards=QA.ORDER_DIRECTION.BUY,
                    price=items.select_code(code).open[0],
                    order_model=QA.ORDER_MODEL.MARKET,
                    amount_model=QA.AMOUNT_MODEL.BY_MONEY
                )
                if order:  # 能够成交时
                    broker.receive_order(QA.QA_Event(order=order, market_data=items.select_code(code)))
                    trade_mes = broker.query_orders(account.account_cookie, 'filled')
                    res = trade_mes.loc[order.account_cookie, order.realorder_id]
                    order.trade(res.trade_id, res.trade_price, res.trade_amount, res.trade_time)
        account.settle()
    risk = QA.QA_Risk(account)
    return account, risk


start = time.time()
ma_backtest('2017-01-01', '2018-01-01')
stop = time.time()
print(stop - start)