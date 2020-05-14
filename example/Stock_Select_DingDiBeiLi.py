# coding=utf-8
import datetime
import sys
from importlib import reload

import QUANTAXIS as QA
import tushare as ts
from example.Stock_Base import *


# 首先是获取沪深两市的股票列表
# 这里得到是对应的dataframe数据结构，它是类似于excel中一片数据的数据结构，有这些列：code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产 fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期

class StockSelectDDBL(Stock_Base):

    def Get_Stock_DDBL(self, code, start='2019-1-1'):
        # df = ts.get_hist_data(code, start='2019-1-1')
        # 0-12 volume：成交量 price_change：价格变动 p_change：涨跌幅
        # ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']
        # print(df)
        today = datetime.date.today()
        end_day = datetime.date(today.year, today.month, today.day)
        # 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'date'
        df = QA.QA_fetch_stock_day(code, start, end_day, "pd")

        df1 = Convert2Tushare(df)
        # print("df1",df1.shape[1]) #df 8
        return StockDDBL_MACD(df1)

    # 然后定义通过MACD判断买入卖出
    def Get_MACD(self, df_Code):
        operate_array = []
        count = len(df_Code)
        index = 1
        for code in df_Code.index:
            (df, operate) = self.Get_Stock_DDBL(code)
            operate_array.append(operate)
            print("Get_Stock_DDBL[{}/{}] {} = {}".format(index,count, code,operate))
            index += 1
        df_Code['MACD'] = pd.Series(operate_array, index=df_Code.index)
        return df_Code

    # def Close_machine():
    #     o = "c:\\windows\\system32\\shutdown -s"  #########
    #     os.system(o)  #########

ss = StockSelectDDBL()
df = ss.Get_Stock_List("20000101")
df = ss.Get_MACD(df)
Output_Csv(df, './')

# 生成的csv文件中，macd列大于0的就是可以买入的，小于0的就是卖出的
