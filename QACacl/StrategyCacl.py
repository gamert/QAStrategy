
from QUANTAXIS import QA_indicator_BOLL
import pandas as pd

# 计算BOLL指标
# TODO: 加快计算？截取部分表？
def StrategyCacl_BOLL(market_data:pd.DataFrame):
    # calculate indicator
    ind = market_data.groupby(['code']).apply(QA_indicator_BOLL)
    res = ind.join(market_data).dropna().round(2)
    res.set_value(index=res[res['LB'] >= res.close].index, col='buyorsell', value=1)  # 买入信号
    res.set_value(index=res[res['UB'] < res.close].index, col='buyorsell', value=-1)  # 卖出信号
    res['change'] = res['buyorsell'].diff()  # 计算指标信号是否反转
    res = res.groupby('code').tail(1)  # 取最新的信号
    # Buy信号的股票池
    res_buy: pd.DataFrame = res[res.change > 0].reset_index()
    # res_buy_code = res_buy['code']
    print("calculator.buy", res_buy)
    # Sell信号的股票池
    res_sell: pd.DataFrame = res[res.change < 0].reset_index()
    # res_sell_code = res_sell['code']
    print("calculator.sell", res_sell)
    return res_buy,res_sell

# 分析TLine的特性
# ref : AbuTline
# 包含趋势分析，短中长，在长期趋势 季度级别；月级别；周级别
# 如果4小时向上？ 那么小周期即可买入；
# 参考Tline: 比如BTC的TLine同OKBTline趋势一致，那么当ref方表现异常时，则要注意报警
# AbuTLine.show_least_valid_poly进行poly判断，它返回的结果是检测至少poly次拟合曲线可以代表原始曲线y的走势
# 验证poly（默认＝1）次多项式拟合回归的趋势曲线是否能代表原始曲线y的走势主要代码
# least = benchmark_month_line.show_least_valid_poly(show=False)
# 分段趋势包围：
# # 可视化技术线拟合曲线及上下拟合通道曲线
#     tc_line.show_regress_trend_channel(step_x=step_x)
#     # 可视化技术线骨架通道
#     tc_line.show_skeleton_channel(step_x=step_x)
#     # 可视化技术线比例分割的区域
#     tc_line.show_percents()
#     # 可视化技术线最优拟合次数
#     tc_line.show_best_poly()


class QATLine:
    def __init__(self, code: str, init_data):
        self.market_data = init_data
        self.stock_code = code


# 模型:
class CBaseCalc:
    def __init__(self, code: str, init_data):
        self.market_data = init_data
        self.stock_code = code
    #执行择时
    def do_sel(self):
        pass
    #由趋势类来决定是否要计算，如果主趋势不好，则不能触发买入，但要触发卖出
    def set_qushi(self,ref_qushi):
        self.ref_qushi = ref_qushi

# 择时:
class CCalc_KDJ(CBaseCalc):
    def __init__(self, code: str, init_data):
        super().__init__(code, init_data)
    #执行择时
    def do_sel(self):
        pass

# 择时:
class CCalc_BOLL(CBaseCalc):
    def __init__(self, code: str, init_data):
        super().__init__(code, init_data)
    #执行择时
    def do_sel(self):
        pass

#计算4小时线的趋势? 趋势要最早计算，以便其他参考
class CCalc_Qushi(CBaseCalc):
    def __init__(self, code: str, init_data):
        super().__init__(code, init_data)
    #执行择时
    def do_sel(self):
        pass