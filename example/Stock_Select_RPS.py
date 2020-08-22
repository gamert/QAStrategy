# https://zhuanlan.zhihu.com/p/59867869
# 如何利用欧奈尔的RPS寻找强势股？
# RPS英文全称Relative Price Strength Rating，即股价相对强度，该指标是欧奈尔CANSLIM选股法则中的趋势分析，具有很强的实战指导意义。
# RPS指标是指在一段时间内，个股涨幅在全部股票涨幅排名中的位次值。
# 比如A股共有3500只股票，若某只股票的120日涨幅在所有股票中排名第350位，则该股票的RPS值为：(1-350/3500)*100=90。
# RPS的值代表该股的120日涨幅超过其他90%的股票的涨幅。通过该指标可以反映个股股价走势在同期市场中的表现相对强弱。
# RPS的值介于0-100之间，在过去的一年中，所有股票的涨幅排行中，前1%的股票的RPS值为99至100，前2%的股票的RPS值为98至99，
# 以此类推。RPS时间周期可以自己根据需要进行调整，常用的有60日（3个月）、120日（半年）和250日（一年）等。

# %matplotlib inline

# 正常显示画图时出现的中文和负号
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

from example.Stock_Base import *
from example.Model_RPS import *

class StockStat_RPS(Stock_Base):

    # 'ts_code,symbol,name,area,industry,list_date'
    def DO_Stock_RPS(self, code, start='2019-1-1'):
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
    def DO_MACD(self, df_Codes):
        operate_array = []
        count = len(df_Codes)
        index = 1
        for code in df_Codes.index:
            (df, operate) = self.Get_Stock_DDBL(code)
            operate_array.append(operate)
            print("Get_Stock_DDBL[{}/{}] {} = {}".format(index,count, code,operate))
            index += 1
        df_Codes['MACD'] = pd.Series(operate_array, index=df_Codes.index)
        return df_Codes

    def DO(self):
        # 通过定义的函数获取上述3024只股票自2018年1月5日以来的所有日交易数据，并计算每只股票120日滚动收益率。

        # 构建一个空的dataframe用来装数据
        data = pd.DataFrame()
        for name, code in code_name.items():
            try:
                data[name] = get_data(code)
            except Exception as e:
                print(e)
            time.sleep(0.5)


# 使用tushare获取上述股票周价格数据并转换为周收益率
# 设定默认起始日期为2018年1月5日，结束日期为2019年3月19日
# 日期可以根据需要自己改动
def get_data(code, start='20150101', end='20190319'):
    df = pro.daily(ts_code=code, start_date=start, end_date=end, fields='trade_date,close')
    # 将交易日期设置为索引值
    df.index = pd.to_datetime(df.trade_date)
    df = df.sort_index()
    # 计算收益率
    return df.close




# data.to_csv('daily_data.csv',encoding='gbk')
# data=pd.read_csv('stock_data.csv',encoding='gbk',index_col='trade_date')
# data.index=(pd.to_datetime(data.index)).strftime('%Y%m%d')



# 查看2018年7月31日-2019年3月19日每月RPS情况。下面仅列出每个月RPS排名前十的股票，里面出现不少熟悉的“妖股”身影。
dates = ['20180731', '20180831', '20180928', '20181031', '20181130', '20181228', '20190131', '20190228', '20190319']
df_rps = pd.DataFrame()
for date in dates:
    df_rps[date] = rps120[date].index[:50]

print(df_rps)

plot_rps('万科A')
# plot_rps('华业资本')
# plot_rps('顺鑫农业')

# 欧奈尔研究了1953年至1993年，500只年度涨幅最大的股票，发现每年涨幅居前的，在他们股价真正大幅度攀升之前，其平均的相对强弱指标RPS为87％。
# 这并不意味着，只要RPS>87%就可以买入该股票呢？其实RPS指标只是对强势股的个一个初步筛选，对于A股而言，RPS大于87%的股票就有400多只，
# 都买进也不太现实，具体运用还需结合个股基本面、题材和整体市场情况分析。RPS实际上是欧奈尔在《笑傲股市》中提出的CANSLIM七步选股法的一个技术分析。
# 各字母含义如下所示：
# C：最近一季度报表显示的盈利（每股收益）
# A：每年度每股盈利的增长幅度
# N：新产品，新服务，股价创新高
# S：该股流通盘大小，市值以及交易量的情况
# L：该股票在行业中的低位，是否为龙头
# I：该股票有无有实力的庄家，机构大流通股东
# M：大盘走势如何，如何判断大盘走向
# RPS可以帮助选出创出新高的股票。牛股一定创新高，但是新高不一定是牛股。所以关键是将RPS结合基本面进一步选择，基本面情况好，
# 销售额和盈利增长很快，且这种增长是由公司推出的新产品或新服务带来的。本文主要分享了欧奈尔RPS指标的原理和Python计算方法，受篇幅所限，
# 文中只给出了核心代码，如需完整代码可通过加入知识星球，向博主索要。文中提及股票不构成任何投资建议，投资有风险，入市需谨慎！
