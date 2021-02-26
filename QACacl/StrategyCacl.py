
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