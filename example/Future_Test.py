from QAStrategy import QAStrategyCTABase
import QUANTAXIS as QA
import pprint

#
class Future_IC2009(QAStrategyCTABase):

    def on_bar(self, bar):

        res = self.cci()
        #print(res.iloc[-1])
        if res.CCI[-1] < -100:
            #print('LONG')
            if self.positions.volume_long == 0:
                self.send_order('BUY', 'OPEN', price=bar['close'], volume=1)

            if self.positions.volume_short > 0:
                self.send_order('BUY', 'CLOSE', price=bar['close'], volume=1)

        else:
            #print('SHORT')
            if self.positions.volume_short == 0:
                self.send_order('SELL', 'OPEN', price=bar['close'], volume=1)
            if self.positions.volume_long > 0:
                self.send_order('SELL', 'CLOSE', price=bar['close'], volume=1)

    def cci(self,):
        return QA.QA_indicator_CCI(self.market_data, 61)

    def risk_check(self):
        pass
        # pprint.pprint(self.qifiacc.message)

if __name__ == '__main__':

    # tes = QA.QA_fetch_get_future_list('pytdx')
    # future_list = tes.code.unique().tolist()
    # print(future_list)
    # ['PB2103', 'PB2104', 'PB2105', 'PB2106', 'PB2107', 'PB2108', 'PBL8', 'PBL9', 'RB2009', 'RB2010', 'RB2011', 'RB2012', 'RB2101', 'RB2102', 'RB2103', 'RB2104', 'RB2105', 'RB2106', 'RB2107', 'RB2108', 'RBL8', 'RBL9', 'RU2009', 'RU2010', 'RU2011', 'RU2101', 'RU2103', 'RU2104', 'RU2105', 'RU2106', 'RU2107', 'RU2108', 'RUL8', 'RUL9', 'SC2009', 'SC2010', 'SC2011', 'SC2012', 'SC2101', 'SC2102', 'SC2103', 'SC2104', 'SC2105', 'SC2106', 'SC2107', 'SC2108', 'SC2109', 'SC2112', 'SC2203', 'SC2206', 'SC2209', 'SC2212', 'SC2303', 'SC2306', 'SCL8', 'SCL9', 'SN2009', 'SN2010', 'SN2011', 'SN2012', 'SN2101', 'SN2102', 'SN2103', 'SN2104', 'SN2105', 'SN2106', 'SN2107', 'SN2108', 'SNL8', 'SNL9', 'SP2009', 'SP2010', 'SP2011', 'SP2012', 'SP2101', 'SP2102', 'SP2103', 'SP2104', 'SP2105', 'SP2106', 'SP2107', 'SP2108', 'SPL8', 'SPL9', 'SS2009', 'SS2010', 'SS2011', 'SS2012', 'SS2101', 'SS2102', 'SS2103', 'SS2104', 'SS2105', 'SS2106', 'SS2107', 'SS2108', 'SSL8', 'SSL9', 'WR2009', 'WR2010', 'WR2011', 'WR2012', 'WR2101', 'WR2102', 'WR2103', 'WR2104', 'WR2105', 'WR2106', 'WR2107', 'WR2108', 'WRL8', 'WRL9', 'ZN2009', 'ZN2010', 'ZN2011', 'ZN2012', 'ZN2101', 'ZN2102', 'ZN2103', 'ZN2104', 'ZN2105', 'ZN2106', 'ZN2107', 'ZN2108', 'ZNL8', 'ZNL9', 'RM2105', 'RM2107', 'RM2108', 'RML8', 'RML9', 'RS2009', 'RS2011', 'RS2107', 'RS2108', 'RSL8', 'RSL9', 'SA2009', 'SA2010', 'SA2011', 'SA2012', 'SA2101', 'SA2102', 'SA2103', 'SA2104', 'SA2105', 'SA2106', 'SA2107', 'SA2108', 'SAL8', 'SAL9', 'SF2009', 'SF2010', 'SF2011', 'SF2012', 'SF2101', 'SF2102', 'SF2103', 'SF2104', 'SF2105', 'SF2106', 'SF2107', 'SF2108', 'SFL8', 'SFL9', 'SM2009', 'SM2010', 'SM2011', 'SM2012', 'SM2101', 'SM2102', 'SM2103', 'SM2104', 'SM2105', 'SM2106', 'SM2107', 'SM2108', 'SML8', 'SML9', 'SR2009', 'SR2011', 'SR2101', 'SR2103', 'SR2105', 'SR2107', 'SRL8', 'SRL9', 'TA2009', 'TA2010', 'TA2011', 'TA2012', 'TA2101', 'TA2102', 'TA2103', 'TA2104', 'TA2105', 'TA2106', 'TA2107', 'TA2108', 'TAL8', 'TAL9', 'UR2009', 'UR2010', 'UR2011', 'UR2012', 'UR2101', 'UR2102', 'UR2103', 'UR2104', 'UR2105', 'UR2106', 'UR2107', 'UR2108', 'URL8', 'URL9', 'WH2009', 'WH2011', 'WH2101', 'WH2103', 'WH2105', 'WH2107', 'WHL8', 'WHL9', 'ZC2009', 'ZC2010', 'ZC2011', 'ZC2012', 'ZC2101', 'ZC2102', 'ZC2103', 'ZC2104', 'ZC2105', 'ZC2106', 'ZC2107', 'ZC2108', 'ZCL8', 'ZCL9', 'A2009', 'A2011', 'A2101', 'A2103', 'A2105', 'A2107', 'AL8', 'AL9', 'B2009', 'B2010', 'B2011', 'B2012', 'B2101', 'B2102', 'B2103', 'B2104', 'B2105', 'B2106', 'B2107', 'B2108', 'BB2009', 'BB2010', 'BB2011', 'BB2012', 'BB2101', 'BB2102', 'BB2103', 'BB2104', 'BB2105', 'BB2106', 'BB2107', 'BB2108', 'BBL8', 'BBL9', 'BL8', 'BL9', 'C2009', 'C2011', 'C2101', 'C2103', 'C2105', 'C2107', 'CL8', 'CL9', 'CS2009', 'CS2011', 'CS2101', 'CS2103', 'CS2105', 'CS2107', 'CSL8', 'CSL9', 'EB2008', 'EB2009', 'EB2010', 'EB2011', 'EB2012', 'EB2101', 'EB2102', 'EB2103', 'EB2104', 'EB2105', 'EB2106', 'EB2107', 'EBL8', 'EBL9', 'EG2008', 'EG2009', 'EG2010', 'EG2011', 'EG2012', 'EG2101', 'EG2102', 'EG2103', 'EG2104', 'EG2105', 'EG2106', 'EG2107', 'EGL8', 'EGL9', 'FB2009', 'FB2010', 'FB2011', 'FB2012', 'FB2101', 'FB2102', 'FB2103', 'FB2104', 'FB2105', 'FB2106', 'FB2107', 'FB2108', 'FBL8', 'FBL9', 'I2009', 'I2010', 'I2011', 'I2012', 'I2101', 'I2102', 'I2103', 'I2104', 'I2105', 'I2106', 'I2107', 'I2108', 'IL8', 'IL9', 'J2009', 'J2010', 'J2011', 'J2012', 'J2101', 'J2102', 'J2103', 'J2104', 'J2105', 'J2106', 'J2107', 'J2108', 'JD2008', 'JD2009', 'JD2010', 'JD2011', 'JD2012', 'JD2101', 'JD2102', 'JD2103', 'JD2104', 'JD2105', 'JD2106', 'JD2107', 'JDL8', 'JDL9', 'JL8', 'JL9', 'JM2009', 'JM2010', 'JM2011', 'JM2012', 'JM2101', 'JM2102', 'JM2103', 'JM2104', 'JM2105', 'JM2106', 'JM2107', 'JM2108', 'JML8', 'JML9', 'L2009', 'L2010', 'L2011', 'L2012', 'L2101', 'L2102', 'L2103', 'L2104', 'L2105', 'L2106', 'L2107', 'L2108', 'LL8', 'LL9', 'M2009', 'M2011', 'M2012', 'M2101', 'M2103', 'M2105', 'M2107', 'M2108', 'ML8', 'ML9', 'P2009', 'P2010', 'P2011', 'P2012', 'P2101', 'P2102', 'P2103', 'P2104', 'P2105', 'P2106', 'P2107', 'P2108', 'PG2011', 'PG2012', 'PG2101', 'PG2102', 'PG2103', 'PG2104', 'PG2105', 'PG2106', 'PG2107', 'PGL8', 'PGL9', 'PL8', 'PL9', 'PP2009', 'PP2010', 'PP2011', 'PP2012', 'PP2101', 'PP2102', 'PP2103', 'PP2104', 'PP2105', 'PP2106', 'PP2107', 'PP2108', 'PPL8', 'PPL9', 'RR2009', 'RR2010', 'RR2011', 'RR2012', 'RR2101', 'RR2102', 'RR2103', 'RR2104', 'RR2105', 'RR2106', 'RR2107', 'RR2108', 'RRL8', 'RRL9', 'V2009', 'V2010', 'V2011', 'V2012', 'V2101', 'V2102', 'V2103', 'V2104', 'V2105', 'V2106', 'V2107', 'V2108', 'VL8', 'VL9', 'Y2009', 'Y2011', 'Y2012', 'Y2101', 'Y2103', 'Y2105', 'Y2107', 'Y2108', 'YL8', 'YL9', 'AG2009', 'AG2010', 'AG2011', 'AG2012', 'AG2101', 'AG2102', 'AG2103', 'AG2104', 'AG2105', 'AG2106', 'AG2107', 'AG2108', 'AGL8', 'AGL9', 'AL2009', 'AL2010', 'AL2011', 'AL2012', 'AL2101', 'AL2102', 'AL2103', 'AL2104', 'AL2105', 'AL2106', 'AL2107', 'AL2108', 'ALL8', 'ALL9', 'AU2009', 'AU2010', 'AU2011', 'AU2012', 'AU2102', 'AU2104', 'AU2106', 'AU2108', 'AUL8', 'AUL9', 'BU2009', 'BU2010', 'BU2011', 'BU2012', 'BU2101', 'BU2102', 'BU2103', 'BU2106', 'BU2109', 'BU2112', 'BU2203', 'BU2206', 'BUL8', 'BUL9', 'CU2009', 'CU2010', 'CU2011', 'CU2012', 'CU2101', 'CU2102', 'CU2103', 'CU2104', 'CU2105', 'CU2106', 'CU2107', 'CU2108', 'CUL8', 'CUL9', 'FU2009', 'FU2010', 'FU2011', 'FU2012', 'FU2101', 'FU2102', 'FU2103', 'FU2104', 'FU2105', 'FU2106', 'FU2107', 'FU2108', 'FUL8', 'FUL9', 'HC2009', 'HC2010', 'HC2011', 'HC2012', 'HC2101', 'HC2102', 'HC2103', 'HC2104', 'HC2105', 'HC2106', 'HC2107', 'HC2108', 'HCL8', 'HCL9', 'LU2101', 'LU2102', 'LU2103', 'LU2104', 'LU2105', 'LU2106', 'LU2107', 'LU2108', 'LUL8', 'LUL9', 'NI2009', 'NI2010', 'NI2011', 'NI2012', 'NI2101', 'NI2102', 'NI2103', 'NI2104', 'NI2105', 'NI2106', 'NI2107', 'NI2108', 'NIL8', 'NIL9', 'NR2009', 'NR2010', 'NR2011', 'NR2012', 'NR2101', 'NR2102', 'NR2103', 'NR2104', 'NR2105', 'NR2106', 'NR2107', 'NR2108', 'NRL8', 'NRL9', 'PB2009', 'PB2010', 'PB2011', 'PB2012', 'PB2101', 'PB2102', 'AP2010', 'AP2011', 'AP2012', 'AP2101', 'AP2103', 'AP2105', 'APL8', 'APL9', 'CF2009', 'CF2011', 'CF2101', 'CF2103', 'CF2105', 'CF2107', 'CFL8', 'CFL9', 'CJ2009', 'CJ2012', 'CJ2101', 'CJ2103', 'CJ2105', 'CJ2107', 'CJL8', 'CJL9', 'CY2009', 'CY2010', 'CY2011', 'CY2012', 'CY2101', 'CY2102', 'CY2103', 'CY2104', 'CY2105', 'CY2106', 'CY2107', 'CY2108', 'CYL8', 'CYL9', 'FG2009', 'FG2010', 'FG2011', 'FG2012', 'FG2101', 'FG2102', 'FG2103', 'FG2104', 'FG2105', 'FG2106', 'FG2107', 'FG2108', 'FGL8', 'FGL9', 'JR2009', 'JR2011', 'JR2101', 'JR2103', 'JR2105', 'JR2107', 'JRL8', 'JRL9', 'LR2011', 'LR2101', 'LR2103', 'LR2105', 'LR2107', 'LRL8', 'LRL9', 'MA2009', 'MA2010', 'MA2011', 'MA2012', 'MA2101', 'MA2102', 'MA2103', 'MA2104', 'MA2105', 'MA2106', 'MA2107', 'MA2108', 'MAL8', 'MAL9', 'OI2009', 'OI2011', 'OI2101', 'OI2103', 'OI2105', 'OI2107', 'OIL8', 'OIL9', 'PM2009', 'PM2011', 'PM2101', 'PM2103', 'PM2105', 'PM2107', 'PML8', 'PML9', 'RI2009', 'RI2011', 'RI2101', 'RI2103', 'RI2105', 'RI2107', 'RIL8', 'RIL9', 'RM2009', 'RM2011', 'RM2101', 'RM2103', 'IMCI', 'T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007', 'T008', 'T009', 'T010', 'T011', 'T012', 'AF2009', 'EF2009', 'IC2008', 'IC2009', 'IC2012', 'IC2103', 'IC500', 'ICL8', 'ICL9', 'IF2008', 'IF2009', 'IF2012', 'IF2103', 'IF300', 'IFL0', 'IFL1', 'IFL2', 'IFL3', 'IFL8', 'IFL9', 'IH2008', 'IH2009', 'IH2012', 'IH2103', 'IH50', 'IHL8', 'IHL9', 'T2009', 'T2012', 'T2103', 'TF2009', 'TF2012', 'TF2103', 'TFL0', 'TFL1', 'TFL2', 'TFL8', 'TFL9', 'TL2009', 'TL8', 'TL9', 'TS2009', 'TS2012', 'TS2103', 'TSL8', 'TSL9']

    strategy = Future_IC2009(code='BUL8', frequence='1min',
                   strategy_id='a3916de0-bx8-4b19c-bxxax1-94d91f1744ad', start='2019-09-25', end='2019-09-30')

    """测试  一般在jupyter中用
    
    """
    import datetime
    t1 = datetime.datetime.now()
    strategy.debug()
    print(datetime.datetime.now() - t1)
    """
    
    之后你可以用strategy.acc.history_table 这些以前qa回测的东西来查看
    """

    """ 回测
    """
    # strategy.run_backtest()

    # """ 模拟
    # """
    # strategy = Future_IC2009(code='rb2005', frequence='1min',
    #                strategy_id='a3916de0-bd28-4b9c-bea1-94d91f1744ac', send_wx=True,)
    # strategy.debug_sim()
    # strategy.add_subscriber("你的wechatid 在QARPO中获取")

    """debugsim是非阻塞的
    
    在进程中 用run_sim
    """

