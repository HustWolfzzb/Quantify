"""
风险控制模型
目前还没想好
后面有空再写
目前先人工上
哈哈哈哈哈哈
"""

from DataEngine.Data import pro, qo, get_pro_stock_basic
import numpy as np
from Monitor.Market import all_stock
import datetime

stocks = get_pro_stock_basic()['ts_code'].tolist()

def history_Normal_Distribution(gaps = 100):
    today = datetime.datetime.now().strftime("%Y%m%d")
    trade_date = pro.trade_cal(exchange='', start_date='20100101', end_date=today)
    stock_data, ok_stock = all_stock()
    for date in trade_date[trade_date['is_open'] == 1]['cal_date'].to_list()[-gaps:]:
        chgs = []
        open_chgs = []
        for code in ok_stock:
            try:
                df = stock_data[code]
                index = df[df['trade_date']==int(date)].index[0]
                chg = float(df.loc[index, 'pct_chg'])
                open_ = float(df.loc[index, 'open'])
                close_ = float(df.loc[index, 'close'])
                try:
                    pre_close_ = float(df.loc[index + 1, 'pct_chg'])
                except Exception as e:
                    # print("出问题啦！")
                    pre_close_ = close_
                open_chg = round((open_ - close_)/close_ * 100, 4)
                chgs.append(chg)
                open_chgs.append(open_chg)
            except Exception as e:
                continue
        print("Date:%s,  当日开盘均值：%s, 当日开盘标准差：%s,  当日收盘均值：%s, 当日收盘标准差：%s"
              %(date,
                round(np.mean(open_chgs),3),
                round(np.std(open_chgs),3),
                round(np.mean(chgs),3),
                round(np.std(chgs),3),
                ))

def Market_Normal_Distribution():
    price_nows = qo.stocks([i[:6] for i in stocks])
    chgs = [round((x['now'] - x['close'])/x['close'], 4)*100 for x in price_nows.values()]
    print("当日均值：%s"%np.mean(chgs))
    print("当日标准差：%s"%np.std(chgs))

def real_time_Normal_Distribution():
    price_nows = qo.stocks([i[:6] for i in stocks])
    chgs = [round((x['now'] - x['close']) / x['close'], 4) * 100 for x in price_nows.values()]
    open_chgs = [round((x['open'] - x['close']) / x['close'], 4) * 100 for x in price_nows.values()]
    print("开盘均值：%s"%np.mean(open_chgs))
    print("当日均值：%s"%np.mean(chgs))
    print("开盘标准差：%s"%np.std(open_chgs))
    print("当日标准差：%s"%np.std(chgs))

if __name__ == '__main__':
    # gaps = 100
    # history_Normal_Distribution(gaps)
    # Market_Normal_Distribution()
    real_time_Normal_Distribution()