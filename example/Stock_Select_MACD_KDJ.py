# coding=utf-8
import datetime
import os
import sys
import time

import pandas as pd
import tushare as ts

# 获取股票列表
# code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产
# fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期
from example.Stock_DDBL import StockDDBL_MACD, StockDDBL_KDJ, StockDDBL_RSI


def Get_Stock_List():
    df = ts.get_stock_basics()
    return df


# 修改了的函数，按照多个指标进行分析

# 按照MACD，KDJ等进行分析
def Get_TA(df_Code, Dist):
    operate_array1 = []
    operate_array2 = []
    operate_array3 = []

    count = 0
    for code in df_Code.index:
        # index,0 - 6 date：日期 open：开盘价 high：最高价 close：收盘价 low：最低价 volume：成交量 price_change：价格变动 p_change：涨跌幅
        # 7-12 ma5：5日均价 ma10：10日均价 ma20:20日均价 v_ma5:5日均量v_ma10:10日均量 v_ma20:20日均量
        df = ts.get_hist_data(code, start='2014-11-20')
        dflen = df.shape[0]
        count = count + 1
        if dflen > 35:
            try:
                (df, operate1) = StockDDBL_MACD(df)
                (df, operate2) = StockDDBL_KDJ(df)
                (df, operate3) = StockDDBL_RSI(df)
            except Exception as e:
                Write_Blog(e, Dist)
                pass
        operate_array1.append(operate1)  # round(df.iat[(dflen-1),16],2)
        operate_array2.append(operate2)
        operate_array3.append(operate3)
        # if count00 == 0:
        #     Write_Blog(str(count), Dist)
    df_Code['MACD'] = pd.Series(operate_array1, index=df_Code.index)
    df_Code['KDJ'] = pd.Series(operate_array2, index=df_Code.index)
    df_Code['RSI'] = pd.Series(operate_array3, index=df_Code.index)
    return df_Code




def Output_Csv(df, Dist):
    TODAY = datetime.date.today()
    CURRENTDAY = TODAY.strftime('%Y-%m-%d')
    reload(sys)
    sys.setdefaultencoding("gbk")
    df.to_csv(Dist + CURRENTDAY + 'stock.csv', encoding='gbk')  # 选择保存


def Close_machine():
    o = "c:\\windows\\system32\\shutdown -s"  #########
    os.system(o)  #########


# 日志记录
def Write_Blog(strinput, Dist):
    TODAY = datetime.date.today()

    CURRENTDAY = TODAY.strftime('%Y-%m-%d')
    TIME = time.strftime("%H:%M:%S")
    # 写入本地文件
    fp = open(Dist + 'blog.txt', 'a')
    fp.write('------------------------------\n' + CURRENTDAY + " " + TIME + " " + strinput + '  \n')
    fp.close()
    time.sleep(1)

df = Get_Stock_List()
Dist = 'E:\\08 python\\Output\\'
df = Get_TA(df, Dist)
Output_Csv(df, Dist)
time.sleep(1)
Close_machine()