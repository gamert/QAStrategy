
import concurrent
import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import json
import pandas as pd
import pymongo

import QUANTAXIS as QA
from QUANTAXIS.QAFetch import QA_fetch_get_stock_block
from QUANTAXIS.QAUtil import (
    DATABASE,
    QA_util_get_next_day,
    QA_util_get_real_date,
    QA_util_log_info,
    QA_util_to_json_from_pandas,
    trade_date_sse
)
from QUANTAXIS.QAData.data_fq import _QA_data_stock_to_fq
from QUANTAXIS.QAFetch.QAQuery import QA_fetch_stock_day
from QUANTAXIS.QAUtil import Parallelism
from multiprocessing import cpu_count
from io import StringIO
import csv
import urllib.request

# ip=select_best_ip()


def now_time():
    return str(QA_util_get_real_date(str(datetime.date.today() - datetime.timedelta(days=1)), trade_date_sse, -1)) + \
           ' 17:00:00' if datetime.datetime.now().hour < 15 else str(QA_util_get_real_date(
        str(datetime.date.today()), trade_date_sse, -1)) + ' 15:00:00'

# 使用枚举返回?
def date_range(start_date,end_date):
    for n in range(int((end_date-start_date).days)+1):
        yield start_date+datetime.timedelta(n)

# 格式化url地址
def get_cffex_url(month, day, year='2018'):
    return 'http://www.cffex.com.cn/sj/hqsj/rtj/' + year + month + '/' + day + '/' + year + month + day + '_1.csv'

# 爬取中金所csv格式数据
def get_cffex_csv(coll_cffex_day, month, day, year='2020'):
    """构造URL下载日统计数据文件"""
    try:
        url = get_cffex_url(month, day, year)
        print(url)
        data = urllib.request.urlopen(url).read().decode('ascii', 'ignore')
        dataFile = StringIO(data)
        csvReader = csv.reader(dataFile)

        date_value = year + month + day

        for row in csvReader:
            #
            code = row[0].strip()
            nlen = len(code)
            t1 = ""
            t2 = ""
            if nlen == 6 :
                t1 = code[0:2]
                t2 = code[2:6]
            elif nlen == 5 :
                t1 = code[0:1]
                t2 = code[2:5]
            # 是需要保存的数据?
            if t2.isdigit() and t1 in ['IC', 'IF', 'IH', 'T', 'TF', 'TS']:
                str = {'code': code, 'open': row[1], 'highest': row[2], 'lowest': row[3], 'volume': row[4],'value': row[5],
                         'inventory': row[6],'inv_change': row[7], 'close': row[8], 'settlement': row[9], 'settle_pre': row[10],
                         'date_stamp': date_value}
                if coll_cffex_day != None:
                    coll_cffex_day.insert(str)
                pass
    except Exception as e:
        print("It is not a trading day: ")
        QA.QA_util_log_info(e)


# 中金所金融期货日统计数据爬取
# 构造URL下载每个交易日统计的附件csv文件，提取csv文件中的次月交割的股指期货统计数据
# 1. 爬取中金所的日数据.csv,从中取出条..
def QA_SU_save_cffex_day(client=DATABASE, ui_log=None, ui_progress=None):
    '''
     save cffex_day
    保存中金所的日数据
    :param client:
    :param ui_log:  给GUI qt 界面使用
    :param ui_progress: 给GUI qt 界面使用
    :param ui_progress_int_value: 给GUI qt 界面使用
    '''
    coll_cffex_day = client.cffex_day
    coll_cffex_day.create_index(
        [
         ("date_stamp",
          pymongo.ASCENDING),
         ("code",
          pymongo.ASCENDING)
        ]
    )
    err = []

    # 以最后的日数据作为基准数据...
    ref = coll_cffex_day.find()
    if ref.count() > 0:
        start_date = ref[ref.count() - 1]['date_stamp']
        start_date1 = datetime.datetime.strptime(start_date, '%Y%m%d')+datetime.timedelta(1)
    else:
        start_date = '2010-04-01'
        start_date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d')

    end_date = str(now_time())[0:10]
    end_date1 = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    for i in date_range(start_date1, end_date1):
        get_cffex_csv(coll_cffex_day, str(i.month).zfill(2), str(i.day).zfill(2), year=str(i.year))

    if len(err) < 1:
        QA_util_log_info('SUCCESS save stock day ^_^', ui_log)
    else:
        QA_util_log_info('ERROR CODE \n ', ui_log)
        QA_util_log_info(err, ui_log)

# Dump 数据
def QA_dump_cffex(client=DATABASE, code = "IC2012"):
    coll_cffex_day = client.cffex_day
    coll_cffex_day.create_index(
        [
         ("code",
          pymongo.ASCENDING),
         ("date_stamp",
          pymongo.ASCENDING)
        ]
    )
    #
    ref = coll_cffex_day.find({'code': str(code)})
    if ref.count() > 0:
        df = pd.DataFrame([item for item in ref])
        df.fillna('', inplace=True)
        print(df)
        with pd.ExcelWriter(code+'.xlsx') as writer:
            df.to_excel(writer, index=None)
        pass

if __name__ == '__main__':
    # last = QA.QA_util_get_last_day(
    #     QA.QA_util_get_real_date(str(datetime.date.today()))), str(datetime.datetime.now())
    # print("last_day:",last)

    # coll = DATABASE.stock_min
    # print("stock_min:",coll)
    #
    # coll = DATABASE.cffex_day
    # print("cffex_day:",coll)

    # http://www.cffex.com.cn/sj/hqsj/rtj/202009/25/20200925_1.csv
    # http://www.cffex.com.cn/sj/hqsj/rtj/201211/19/20121119_1.csv
    #get_cffex_csv("", "09", "25", '2020')
    QA_dump_cffex(code = "IC2103")
    #QA_SU_save_cffex_day()