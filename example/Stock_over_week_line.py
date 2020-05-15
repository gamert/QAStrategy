# -*-coding=utf-8-*-
import datetime
import QUANTAXIS as QA

from QUANTAXIS import QA_quotation, MARKET_TYPE, DATASOURCE, OUTPUT_FORMAT, FREQUENCE

__author__ = 'zz'
'''

'''

# 获取破指定天数内的新高 比如破60日新高
class qa_over_week_line():
    def __init__(self):
        # super().__init__()
        self.stockItems = QA.QA_fetch_stock_list() # QA.QA_fetch_stock_list_adv()
        # print(self.stockItems)

        # self.code_name = {}
        # for stock in self.stockItems:
        #     print(stock)
            # code_list.append(stock['code'])
            # self.code_name[stock['code']] = stock['name']

        # #codes = QA.QA_fetch_stock_block_adv().code # [0:50]
        codes = self.stockItems.code.values #.tolist()
        names = self.stockItems.name.values
        self.code_name = dict(zip(names, codes))
        print("counts = ", len(self.code_name))
        # print(self.code_name)
        # stock_data = QA.QA_fetch_stock_day_adv(code=code_list,
        #                                        start=start_date,
        #                                        end=end_date).to_qfq().resample("w")
        # index_data = QA.QA_fetch_index_day_adv(code='000001',
        #                                        start=start_date,
        #                                        end=end_date).resample("w")
        # DATA = QA.QA_fetch_stock_day_adv(code, start, end).to_qfq()
        # 日线
        # df_from_Tdx = QA_quotation('300439', '2015-01-01', '2019-11-19', frequence=FREQUENCE.DAY,
        #                            market=MARKET_TYPE.STOCK_CN, source=DATASOURCE.MONGO, output=OUTPUT_FORMAT.DATAFRAME)
        # print(df_from_Tdx)
        pass

    def cacl_by_days(self, days):
        # days = 365*4*5/7
        today = datetime.date.today()
        end_day = datetime.date(today.year, today.month, today.day)
        days = int(days) * 7 / 5
        # 考虑到周六日非交易
        start_day = end_day - datetime.timedelta(days)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")

        self.loop_all_stocks(start_day, end_day)

    def loop_all_from(self, start_day):
        today = datetime.date.today()
        end_day = datetime.date(today.year, today.month, today.day)
        end_day = end_day.strftime("%Y-%m-%d")
        self.loop_all_stocks(start_day, end_day)

    def loop_all_stocks(self, start_day, end_day):

        for name, code in self.code_name.items():
        # for stock in self.stockItems:
            EachStockID = code # stock['code'] #  = stock['name']code.split('.')[0]
            # self.data[name] = get_data(code)
            try:
                b, period_high, today_high = self.is_break_high(EachStockID, start_day, end_day)
                if b:
                    print("High price on", EachStockID, name, period_high, today_high)
            except:
                pass

    # '300439', '2015-01-01', '2019-11-19'
    def is_break_high(self, stockID, start_day, end_day):

        # 如何保存k线数据进行快速计算？
        # df = ts.get_k_data(stockID, start=start_day, end=end_day, ktype='W')
        df = QA.QA_fetch_stock_day_adv(stockID, start_day, end_day).to_qfq()
        # df = QA_quotation(stockID, start_day, end_day, frequence=FREQUENCE.DAY,
        #                            market=MARKET_TYPE.STOCK_CN, source=DATASOURCE.MONGO, output=OUTPUT_FORMAT.DATAFRAME)
        # todo: 复权
        #df = df.to_qfq()
        cc = df['close']
        period_high = cc.max()
        # print period_high
        today_high = cc.iloc[-1]
        # 这里不能直接用 .values
        # 如果用的df【：1】 就需要用.values
        # print today_high
        if today_high >= period_high * 0.95:
            return True, period_high, today_high
        else:
            return False, period_high, today_high


# main函数入口
if __name__ == '__main__':
    tow = qa_over_week_line()
    # tow.cacl_by_days(365*4*5/7)
    tow.loop_all_from("2015-1-1")
