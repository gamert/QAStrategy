# coding=utf-8
import datetime
import sys
from importlib import reload

import QUANTAXIS as QA
from example.Stock_DDBL import *


# 输出CSV文件，其中要进行转码，不然会乱码
def Output_Csv(df, Dist):
    TODAY = datetime.date.today()
    CURRENTDAY = TODAY.strftime('%Y-%m-%d')
    # reload(sys)
    # sys.setdefaultencoding("gbk")
    df.to_csv(Dist + CURRENTDAY + 'stock.csv', encoding='gbk')  # 选择保存

# 将QA的格式转为Tushare的格式
def Convert2Tushare(df):
    # df.drop(columns=['code'], inplace=True)
    df1 = pd.DataFrame(df, columns=['open', 'high', 'close', 'low', 'volume'])
    # print(df1)

    close_s = pd.Series(df1['close'])
    volume_s = pd.Series(df1['volume'])

    df1['price_change'] = close_s
    df1['p_change'] = close_s

    df1['ma5'] = QA.MA(close_s, 5)  # .shift()
    df1['ma10'] = QA.MA(close_s, 10)  # .shift(-9)
    df1['ma20'] = QA.MA(close_s, 20)  # .shift(-19)

    df1['v_ma5'] = QA.MA(volume_s, 5)
    df1['v_ma10'] = QA.MA(volume_s, 10)
    df1['v_ma20'] = QA.MA(volume_s, 20)
    return df1


# 使用pandas更新DataFrame某一列（值位于另一个DataFrame）
# df1=pd.DataFrame({'id':[1,2,3],'name':['Andy1','Jacky1','Bruce1']})
# df2=pd.DataFrame({'id':[1,2],'name':['Andy2','Jacky2']})
#
# s = df2.set_index('id')['name']
# df1['name'] = df1['id'].map(s).fillna(df1['name']).astype(str)
# print(df1)


def QA_fetch_stock_info2(code):
    return QA.QA_fetch_stock_info(code).ipo_date

# 基类:
# 初始化股票列表（指定日期前，排除新股）
class Stock_Base():
    def __init__(self):
        self._stock_list = QA.QA_fetch_stock_list()

    def stock_name(self,stoke_code):
        '''通过股票代码导出公司名称'''
        company_name = list(self._stock_list.loc[self._stock_list['code'] == stoke_code].name)[0]
        return company_name

    #          code  decimal_point   name   ...         sec sse volunit
    # code                                   ...
    # 000001  000001              2   平安银行   ...    stock_cn  sz     100
    # # 这里得到是对应的dataframe数据结构，它是类似于excel中一片数据的数据结构，有这些列：code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产 fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期
    def Get_Stock_List(self, beforeDate = None):
        #df = pd.DataFrame([['000001', "平安银行"]], columns=['code', 'name'])
        # df.set_index(["code"], inplace=True)

        # print(df)
        # df = df.drop([0, 1],axis=0)
        # df = df.drop([3, len(df)],axis=0)
        # print(df)
        df = self._stock_list

        if beforeDate:
            pd_info= pd.DataFrame([item for item in QA.DATABASE.stock_info.find()]).drop('_id', axis=1, inplace=False).set_index(
                'code', drop=False)
            # 首先增加一个空列
            df["ipo_date"] = None
            # 指定一个新的Seair 并填充到原DF中
            s = pd_info.set_index('code')['ipo_date']
            df["ipo_date"] = df['code'].map(s).fillna(df['ipo_date']).astype(str)
            # 过滤
            df = df.loc[lambda x: (x['ipo_date']>"0")&(x['ipo_date']<beforeDate)] #df[lambda x: x['ipo_date']!=None and x['ipo_date']!='0']
            #print(df)

            # pd2 = pd.DataFrame()
            # for index, row in df.iterrows():
            #     if int(QA_fetch_stock_info2(row.code)) < int(beforeDate):
            #         # d = pd.DataFrame(row).T
            #         pd2 = pd2.append([row])
            # df = pd2

            #df.sort(columns='year')
            #df = df.loc[lambda x: x['year']>1990,axis=1]
            #df = df.loc[lambda x: int(QA_fetch_stock_info2(x.index)) < int(beforeDate)]
            #df = df[lambda x: int(QA_fetch_stock_info2(x)) < int(beforeDate)]

            # .head(10)

        return df



if __name__ == '__main__':

    SB = Stock_Base()
    df = SB.Get_Stock_List("20000101")
    print(df)