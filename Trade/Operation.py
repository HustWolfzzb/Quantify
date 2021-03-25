from random import randint
import tushare as ts
from Strategy.ThreeMomentum import threeMonmentum
from datetime import datetime, time, date
from time import sleep
import easyquotation
# from Strategy import nihe
from DataEngine.Data import get_pro_daily,get_pro_stock_basic


# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
MORNING_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

if __name__ == '__main__':
    stocks = get_pro_stock_basic()
    codes = [x for x in stocks['ts_code'] if x[0] != 3 and x[:2]!='68']
    names = [x for x in stocks['name']]
    for x in range(len(codes)):
        if names[x].find('ST') != -1:
            continue
        print("\n\n模拟%s 三重指标"%names[x])
        sleep(1)
        threeMonmentum(codes[x], '20160101', '20210310')


