import datetime

import QUANTAXIS as QA
def GetStockDays(code, start='2019-1-1'):
    today = datetime.date.today()
    end_day = datetime.date(today.year, today.month, today.day)
    # 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'date'
    df = QA.QA_fetch_stock_day(code, start, end_day, "pd")
    return df
