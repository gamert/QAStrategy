# coding=utf-8
import datetime
import sys
from importlib import reload

import QUANTAXIS as QA
import tushare as ts
from example.Stock_Base import *


# 首先是获取沪深两市的股票列表
# 这里得到是对应的dataframe数据结构，它是类似于excel中一片数据的数据结构，有这些列：code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产 fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期

# 选股: 周线跳空
class StockSelect_WeekJump(Stock_Base):

    def Get_Stock_WeekJump(self, code, start='2020-4-1'):
        today = datetime.date.today()
        end_day = datetime.date(today.year, today.month, today.day)
        # 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'date'
        #df = QA.QA_fetch_stock_day(code, start, end_day, "pd").resample()
        df = QA.QA_fetch_stock_day_adv(code, start, end_day)
        if(df == None):
            return df, "False"
        df = df.to_qfq()
        df = df.resample('w')

        if(len(df) > 1):
            if(df['low'][-1] > df['close'][-2]):
                return df, "True"
        # print("df1",df1.shape[1]) #df 8
        return df, "False"

    # 然后定义通过MACD判断买入卖出
    def Get_WeekJump(self, df_Code):
        operate_array = []
        count = len(df_Code)
        index = 1
        for code in df_Code.index:
            (df, operate) = self.Get_Stock_WeekJump(code)
            operate_array.append(operate)
            if(operate  == "True"):
                print("Get_WeekJump[{}/{}]{} {} = {}".format(index, count, self.stock_name(code), code, operate))
            index += 1
        df_Code['Jump'] = pd.Series(operate_array, index=df_Code.index)
        return df_Code

    # def Close_machine():
    #     o = "c:\\windows\\system32\\shutdown -s"  #########
    #     os.system(o)  #########

ss = StockSelect_WeekJump()
df = ss.Get_Stock_List("20200415")
df = ss.Get_WeekJump(df)
Output_Csv(df, './')

# 生成的csv文件中，macd列大于0的就是可以买入的，小于0的就是卖出的
