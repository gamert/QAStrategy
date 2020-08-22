import time
import pandas as pd
import matplotlib.pyplot as plt


# RPS 计算模型:

# 计算收益率
def cal_ret(df, w=5):
    '''w:周5;月20;半年：120; 一年250
    '''
    df = df / df.shift(w) - 1
    return df.iloc[w:, :].fillna(0)

# 计算RPS
def get_RPS(ser):
    df = pd.DataFrame(ser.sort_values(ascending=False))
    df['n'] = range(1, len(df) + 1)
    df['rps'] = (1 - df['n'] / len(df)) * 100
    return df

# 计算每个交易日所有股票滚动w日的RPS
def all_RPS(data):
    dates = (data.index).strftime('%Y%m%d')
    RPS = {}
    for i in range(len(data)):
        df = get_RPS(data.iloc[i])
        RPS[dates[i]] = pd.DataFrame(df.values, columns=['收益率', '排名', 'RPS'],
                                     index=df.index)
    return RPS

# 获取所有股票在某个期间的RPS值
def all_data(rps, ret):
    df = pd.DataFrame(pd.np.NaN, columns=ret.columns, index=ret.index)
    for date in ret.index:
        date = date.strftime('%Y%m%d')
        d = rps[date]
        for c in d.index:
            df.loc[date, c] = d.loc[c, 'RPS']
    return df


def Do_RPS(data):

    # 经过这一轮的大幅上涨，截至2019年3月19日，上述3024只股票中，有49只股票120日收益率超过100%，占比1.68%；
    # 收益率在20%-100%之间的股票有1280只，占比达到43.99%；仍有360只股票120日收益率为负数。
    ret120 = cal_ret(data, w=120)
    rps120 = all_RPS(ret120)

    # 构建一个以前面收益率为基础的空表
    df_new = pd.DataFrame(pd.np.NaN, columns=ret120.columns, index=ret120.index)
    # 计算所有股票在每一个交易日的向前120日滚动RPS值。对股票价格走势和RPS进行可视化。
    for date in df_new.index:
        date = date.strftime('%Y%m%d')
        d = rps120[date]
        for c in d.index:
            df_new.loc[date, c] = d.loc[c, 'RPS']

    return rps120, df_new


def plot_rps(data, stock, df_new):
    ddf = data[stock]
    if not ddf:
        print("plot_rps not find: ",stock)
        return

    plt.subplot(211)
    ddf[120:].plot(figsize=(16, 16), color='r')
    plt.title(stock + '股价走势', fontsize=15)
    plt.yticks(fontsize=12)
    plt.xticks([])
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.subplot(212)
    df_new[stock].plot(figsize=(16, 8), color='b')
    plt.title(stock + 'RPS相对强度', fontsize=15)
    my_ticks = pd.date_range('2018-06-9', '2019-3-31', freq='m')
    plt.xticks(my_ticks, fontsize=12)
    plt.yticks(fontsize=12)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.show()
