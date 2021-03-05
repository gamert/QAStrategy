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
import multiprocessing

from pylab import mpl
import QUANTAXIS as QA

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

from example.Stock_Base import *
from example.Model_RPS import *


def f(name, code, self):
    try:
#        data[name] =
        return (name, self.get_data(code).close)
    except Exception as e:
        print(e)


# 统一计算250 120 50 等指定个数bar的强度，放到一个表内
#
class StockStat_RPS(Stock_Base):
    #
    def get_data(self, code, start='2019-1-1'):
        today = datetime.date.today()
        end_day = datetime.date(today.year, today.month, today.day)
        # 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'date'
        dd = QA.QA_fetch_stock_day_adv(code, start, end_day,if_drop_index=False)
        df = dd.to_qfq().data
        return df.set_index(['date'],drop = False)

    def DO(self, limit=200):
        # 通过定义的函数获取上述3024只股票自2018年1月5日以来的所有日交易数据，并计算每只股票120日滚动收益率。
        df = self.Get_Stock_List("20200305")
        codes = df.code.values
        names = df.name.values
        code_name = dict(zip(names, codes))

        i = 0
        # 构建一个空的dataframe用来装数据
        data = pd.DataFrame()

        cores = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=cores)

        start_time = time.time()

        count = len(codes)
        ##zz = zip(names, codes, [self]*count)
        ##pool.starmap(f, zz)

        pool_list = []
        #result_list = []
        start_time = time.time()

        for name, code in code_name.items():
            pool_list.append(pool.apply_async(f, (name, code, self )))
            # try:
            #     data[name] = self.get_data(code).close
            # except Exception as e:
            #     print(e)
            i=i+1
            if i > limit:
                break
        # #在这里不免有人要疑问，为什么不直接在 for 循环中直接 result.get()呢？
        # 这是因为pool.apply_async之后的语句都是阻塞执行的，调用 result.get() 会等待上一个任务执行完之后才会分配下一个任务。
        # 事实上，获取返回值的过程最好放在进程池回收之后进行，避免阻塞后面的语句。
        result_list = [xx.get() for xx in pool_list]
        for (name, df) in result_list:
            data[name] = df
            ##dict1 = {k: v for k, v in dict0.items() if v >= 60}

        pool.close()
        pool.join()

        print(limit,"/",count, ' 并行花费时间 %.2f' % (time.time() - start_time))

        # 倒推120天的收益:
        ret120 = cal_ret(data, w=120)
        # 计算RPS
        rps120 = all_RPS(ret120)
        # 查看2018年7月31日-2019年3月19日每月RPS情况。下面仅列出每个月RPS排名前十的股票，里面出现不少熟悉的“妖股”身影。
        dates = ['20210304']
        df_rps = pd.DataFrame()
        for date in dates:
            df_rps[date] = rps120[date].index[:50]
        print(df_rps)



        # # 构建一个以前面收益率为基础的空表
        # df_new = pd.DataFrame(pd.np.NaN, columns=ret120.columns, index=ret120.index)
        #
        # # 计算所有股票在每一个交易日的向前120日滚动RPS值。对股票价格走势和RPS进行可视化。
        # for date in df_new.index:
        #     date = date.strftime('%Y%m%d')
        #     d = rps120[date]
        #     for c in d.index:
        #         df_new.loc[date, c] = d.loc[c, 'RPS']

if __name__ == '__main__':
    rps = StockStat_RPS()
    ## apply_async 1000
    # 100  并行花费时间 11
    # 1000  并行花费时间 21.89
    # 2000  并行花费时间 37.76 debug
    # 2000  并行花费时间 30.10 run
    # 3000  并行花费时间 39.56 run

    # 普通循环：
    # 2000  并行花费时间 62.25
    # 3000  并行花费时间 91.52
    rps.DO(limit=100)