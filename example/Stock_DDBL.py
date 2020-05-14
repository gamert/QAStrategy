import talib as ta
import numpy as np
import pandas as pd


# 计算顶底背离标记
# 获取每只股票的历史价格和成交量 对应的列有index列,0 - 6列是 date：日期 open：开盘价 high：最高价 close：收盘价 low：最低价 volume：成交量 price_change：价格变动 p_change：涨跌幅

# 7-12列是 ma5：5日均价 ma10：10日均价 ma20:20日均价 v_ma5:5日均量v_ma10:10日均量 v_ma20:20日均量
# 13-15列，对应的是 DIFF DEA DIFF-DEA
def StockDDBL_MACD(df):
    dflen = df.shape[0]
    operate = 0
    if dflen > 35:
        macd, macdsignal, macdhist = ta.MACD(np.array(df['close']), fastperiod=12, slowperiod=26, signalperiod=9)

        SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
        SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
        SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
        # 在后面增加3列，分别是13-15列，对应的是 DIFF DEA DIFF-DEA
        df['macd'] = pd.Series(macd, index=df.index)  # DIFF
        df['macdsignal'] = pd.Series(macdsignal, index=df.index)  # DEA
        df['macdhist'] = pd.Series(macdhist, index=df.index)  # DIFF-DEA

        # 2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
        diff = df.iat[(dflen - 1), 13]
        dea = df.iat[(dflen - 1), 14]
        if diff > 0:
            if dea > 0:
                if diff > dea:
                    operate = operate + 1  # 买入
        else:
            if dea < 0:
                if diff <= dea:
                    operate = operate - 1  # 卖出

        # 3.DEA线与K线发生背离，行情反转信号。
        ma5 = df.iat[(dflen - 1), 7]
        ma10 = df.iat[(dflen - 1), 8]
        ma20 = df.iat[(dflen - 1), 9]
        MAlen = len(SignalMA5)
        SIndex = MAlen - 1
        if ma5 >= ma10 and ma10 >= ma20:  # K线上涨
            if SignalMA5[SIndex] <= SignalMA10[SIndex] and SignalMA10[SIndex] <= SignalMA20[SIndex]:  # DEA下降
                operate = operate - 1
        elif ma5 <= ma10 and ma10 <= ma20:  # K线下降
            if SignalMA5[SIndex] >= SignalMA10[SIndex] and SignalMA10[SIndex] >= SignalMA20[SIndex]:  # DEA上涨
                operate = operate + 1

        macdhist = df.iat[(dflen - 1), 15]
        # 4.分析MACD柱状线，由负变正，买入信号。
        if macdhist > 0 and dflen > 30:
            for i in range(1, 26):
                if df.iat[(dflen - 1 - i), 15] <= 0:  #
                    operate = operate + 1
                    break
        # 由正变负，卖出信号
        if macdhist < 0 and dflen > 30:
            for i in range(1, 26):
                if df.iat[(dflen - 1 - i), 15] >= 0:  #
                    operate = operate - 1
                    break
    return (df, operate)


# 通过KDJ判断买入卖出
# 16-17 K,D
def StockDDBL_KDJ(df):
    # 参数9,3,3
    slowk, slowd = ta.STOCH(np.array(df['high']), np.array(df['low']), np.array(df['close']), fastk_period=9,
                            slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    slowkMA5 = ta.MA(slowk, timeperiod=5, matype=0)
    slowkMA10 = ta.MA(slowk, timeperiod=10, matype=0)
    slowkMA20 = ta.MA(slowk, timeperiod=20, matype=0)
    slowdMA5 = ta.MA(slowd, timeperiod=5, matype=0)
    slowdMA10 = ta.MA(slowd, timeperiod=10, matype=0)
    slowdMA20 = ta.MA(slowd, timeperiod=20, matype=0)

    # 16-17 K,D
    df['slowk'] = pd.Series(slowk, index=df.index)  # K
    df['slowd'] = pd.Series(slowd, index=df.index)  # D
    dflen = df.shape[0]
    MAlen = len(slowkMA5)
    operate = 0

    K = df.iat[(dflen - 1), 16]
    D = df.iat[(dflen - 1), 17]
    # 1.K线是快速确认线——数值在90以上为超买，数值在10以下为超卖；D大于80时，行情呈现超买现象。D小于20时，行情呈现超卖现象。
    if K >= 90:
        operate = operate - 3
    elif K <= 10:
        operate = operate + 3

    if D >= 80:
        operate = operate - 3
    elif D <= 20:
        operate = operate + 3

    # 2.上涨趋势中，K值大于D值，K线向上突破D线时，为买进信号。#待修改
    if K > D and df.iat[(dflen - 2), 16] <= df.iat[(dflen - 2), 17]:
        operate = operate + 10
    # 下跌趋势中，K小于D，K线向下跌破D线时，为卖出信号。#待修改
    elif K < D and df.iat[(dflen - 2), 16] >= df.iat[(dflen - 2), 17]:
        operate = operate - 10

    ma5 = df.iat[(dflen - 1), 7]
    ma10 = df.iat[(dflen - 1), 8]
    ma20 = df.iat[(dflen - 1), 9]
    # 3.当随机指标与股价出现背离时，一般为转势的信号。
    if ma5 >= ma10 and ma10 >= ma20:  # K线上涨
        if (slowkMA5[MAlen - 1] <= slowkMA10[MAlen - 1] and slowkMA10[MAlen - 1] <= slowkMA20[MAlen - 1]) or \
                (slowdMA5[MAlen - 1] <= slowdMA10[MAlen - 1] and slowdMA10[MAlen - 1] <= slowdMA20[MAlen - 1]):  # K,D下降
            operate = operate - 1
    elif ma5 <= ma10 and ma10 <= ma20:  # K线下降
        if (slowkMA5[MAlen - 1] >= slowkMA10[MAlen - 1] and slowkMA10[MAlen - 1] >= slowkMA20[MAlen - 1]) or \
                (slowdMA5[MAlen - 1] >= slowdMA10[MAlen - 1] and slowdMA10[MAlen - 1] >= slowdMA20[MAlen - 1]):  # K,D上涨
            operate = operate + 1

    return (df, operate)


# 通过RSI判断买入卖出
# 18-19 慢速real，快速real
def StockDDBL_RSI(df):
    # 参数14,5
    slowreal = ta.RSI(np.array(df['close']), timeperiod=14)
    fastreal = ta.RSI(np.array(df['close']), timeperiod=5)

    slowrealMA5 = ta.MA(slowreal, timeperiod=5, matype=0)
    slowrealMA10 = ta.MA(slowreal, timeperiod=10, matype=0)
    slowrealMA20 = ta.MA(slowreal, timeperiod=20, matype=0)
    fastrealMA5 = ta.MA(fastreal, timeperiod=5, matype=0)
    fastrealMA10 = ta.MA(fastreal, timeperiod=10, matype=0)
    fastrealMA20 = ta.MA(fastreal, timeperiod=20, matype=0)
    # 18-19 慢速real，快速real
    df['slowreal'] = pd.Series(slowreal, index=df.index)  # 慢速real 18
    df['fastreal'] = pd.Series(fastreal, index=df.index)  # 快速real 19
    dflen = df.shape[0]
    operate = 0
    # RSI>80为超买区，RSI<20为超卖区
    if df.iat[(dflen - 1), 18] > 80 or df.iat[(dflen - 1), 19] > 80:
        operate = operate - 2
    elif df.iat[(dflen - 1), 18] < 20 or df.iat[(dflen - 1), 19] < 20:
        operate = operate + 2

    # RSI上穿50分界线为买入信号，下破50分界线为卖出信号
    if (df.iat[(dflen - 2), 18] <= 50 and df.iat[(dflen - 1), 18] > 50) or (
            df.iat[(dflen - 2), 19] <= 50 and df.iat[(dflen - 1), 19] > 50):
        operate = operate + 4
    elif (df.iat[(dflen - 2), 18] >= 50 and df.iat[(dflen - 1), 18] < 50) or (
            df.iat[(dflen - 2), 19] >= 50 and df.iat[(dflen - 1), 19] < 50):
        operate = operate - 4

    MAlen = len(slowrealMA5)
    ma5 = df.iat[(dflen - 1), 7]
    ma10 = df.iat[(dflen - 1), 8]
    ma20 = df.iat[(dflen - 1), 9]
    # RSI掉头向下为卖出讯号，RSI掉头向上为买入信号
    if ma5 >= ma10 and ma10 >= ma20:  # K线上涨
        if (slowrealMA5[MAlen - 1] <= slowrealMA10[MAlen - 1] and slowrealMA10[MAlen - 1] <= slowrealMA20[MAlen - 1]) or \
                (fastrealMA5[MAlen - 1] <= fastrealMA10[MAlen - 1] and fastrealMA10[MAlen - 1] <= fastrealMA20[
                    MAlen - 1]):  # RSI下降
            operate = operate - 1
    elif ma5 <= ma10 and ma10 <= ma20:  # K线下降
        if (slowrealMA5[MAlen - 1] >= slowrealMA10[MAlen - 1] and slowrealMA10[MAlen - 1] >= slowrealMA20[MAlen - 1]) or \
                (fastrealMA5[MAlen - 1] >= fastrealMA10[MAlen - 1] and fastrealMA10[MAlen - 1] >= fastrealMA20[
                    MAlen - 1]):  # RSI上涨
            operate = operate + 1

    # 慢速线与快速线比较观察，若两线同向上，升势较强；若两线同向下，跌势较强；若快速线上穿慢速线为买入信号；若快速线下穿慢速线为卖出信号
    if df.iat[(dflen - 1), 19] > df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] <= df.iat[(dflen - 2), 18]:
        operate = operate + 10
    elif df.iat[(dflen - 1), 19] < df.iat[(dflen - 1), 18] and df.iat[(dflen - 2), 19] >= df.iat[(dflen - 2), 18]:
        operate = operate - 10
    return (df, operate)
