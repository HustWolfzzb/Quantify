from random import random, randint

import tushare as ts

from datetime import datetime, time, timedelta
from time import sleep
import numpy as np
from Strategy import nihe

# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
DAY_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

symbol = ["002164","002517","002457","600723","600918","600720","603187","002271","000759","000735","601933"]
stock_name =["宁波东力","恺英网络","青龙管业","首商股份","中泰证券","祁连山","海容冷链","东方雨虹","中百集团","罗牛山","永辉超市"]
stock_code = { symbol[x]:stock_name[x] for x in range(len(symbol))}
def is_openMartket():
    current_time = datetime.now().time()
    if not ((current_time > DAY_START and current_time < AFTERNOON_END )):
        return -1
    elif not ((current_time > DAY_START and current_time < DAY_END) or (current_time >AFTERNOON_START and current_time < AFTERNOON_END )):
        return 0
    return 1


def predict(data):
    para, func, func_min_offset = nihe(data)
    if func_min_offset == -1:
        return [0]
    x2 = np.arange(0, len(data) + 20)
    y2 = None
    if func_min_offset == 0 or func_min_offset == 2:
        A, B, C = para
        y2 = func(x2, A, B, C)
    elif func_min_offset == 1:
        A, B, C, D = para
        y2 = func(x2, A, B, C, D)
    elif func_min_offset == 3:
        A, B = para
        y2 = func(x2, A, B)
    return y2



def main():
    tick_data = {}
    for s in symbol:
        tick_data[s] = []
    while(True):
        time = is_openMartket()
        if time == -1:
            break
        if time == 0:
            sleep(120)
            continue
        else:
            sleep(120)
        realtimeData = list(ts.get_realtime_quotes(symbol).price)
        print(datetime.now().isoformat().replace('T', "  "))
        try:
            for idx in range(len(realtimeData)):
                data = tick_data[symbol[idx]]
                data.append(realtimeData[idx])
                if len(data) < 8:
                    sleep(int(120/len(symbol)))
                    continue
                y2 = predict(data)
                if y2[0] == 0:
                    continue
                if max(y2) != y2[-1]:
                    max_y2 = max(y2)
                    for x in range(len(y2[-20:])):
                        if y2[-20+x] == max_y2:
                            print("%s 卖出点在：%s, 时间为：%s" %(symbol[idx], max_y2, datetime.now() + timedelta(minutes=2*x)))
                elif min(y2) != y2[-1]:
                    min_y2 = min(y2)
                    for x in range(len(y2[-20:])):
                        if y2[-20 + x] == min_y2:
                            print("%s 买入点在：%s, 时间为：%s" % (symbol[idx], min_y2, datetime.now() + timedelta(minutes=2 * x)))
                else:
                    if max(y2) < y2[len(data)]:
                        print("%s持续下行中！！"%symbol[idx])
                    else:
                        print("%s 持续上升中！！" % symbol[idx])
        except Exception as e:
            print(e)
    # for s in symbol:
    #     with open('tickData/%s-%s.txt'%(stock_code[s],s), 'a', encoding='utf8') as out:
    #         out.write("时间：%s\n"%datetime.now().isoformat())
    #         out.write(", ".join(tick_data[s]))
    #         out.write("\n")

def operate(stock_position, price, amount, operation, record):
    if operation == 'b':
        if stock_position['可用余额'] < amount * price:
            return
        stock_position['当前成本'] = (stock_position['当前成本'] * stock_position['持有股份'] + price * amount * 1.0001 ) / (stock_position['持有股份']  + amount)
        stock_position['持有股份'] += amount
        stock_position['可用余额'] -= amount * price * 1.0001
        stock_position['冻结股份'] += amount
        stock_position['买卖总手数'] += amount/100
        record.append("===>>>>买入成功！价格：%s，数量：%s，当前持仓：%s, 当前可用：%s，价格成本：%s"%(price, amount, stock_position['持有股份'], stock_position['可用股份'], stock_position['当前成本']))
    elif operation == 's':
        if stock_position['可用股份'] < amount:
            return
        if stock_position['持有股份'] - amount == 0:
            record.append("清仓！")
            stock_position['当前成本'] = 0
            stock_position['买卖总手数'] += amount/100
        else:
            stock_position['当前成本'] = (stock_position['当前成本'] * stock_position['持有股份'] - price * amount * 0.9989 ) / (stock_position['持有股份'] - amount)
        stock_position['持有股份'] -= amount
        stock_position['可用股份'] -= amount
        stock_position['可用余额'] += amount * price * 0.9989
        stock_position['买卖总手数'] += amount/100
        record.append("<<<===卖出成功！价格：%s，数量：%s，当前持仓：%s, 当前可用：%s, 价格成本：%s"%(price, amount, stock_position['持有股份'], stock_position['可用股份'], stock_position['当前成本']))


def skip_oneday(stock_position, close_price, record):
    stock_position['最新价格'] = round(close_price,2)
    stock_position['当前资金'] = round(stock_position['持有股份'] * stock_position['最新价格'] + stock_position['可用余额'], 2)
    stock_position['可用股份'] = stock_position['持有股份']
    stock_position['冻结股份'] = 0
    stock_position['可用余额'] = round(stock_position['可用余额'], 2)

    # stock_position['买卖总手数'] = 0
    stock_position['总资金增长率'] = round((stock_position['当前资金'] - stock_position['初始资金'])/stock_position['初始资金'],4)
    stock_position['股价波动率'] = round((stock_position['最新价格'] - stock_position['初始价格'])/stock_position['初始价格'],4)
    record.append("*"*10 + "="*10 + "*"*10)



def test(rate = 0.003, amount = 200, symbols=[] , stock_names=[] ):
    from Data import get_realtime_price
    # symbols = ["002164", "002517", "002457", "600723", "600918", "600720", "603187", "002271", "000759", "000735",
    #           "601933"]
    # stock_names = ["宁波东力", "恺英网络", "青龙管业", "首商股份", "中泰证券", "祁连山", "海容冷链", "东方雨虹", "中百集团", "罗牛山", "永辉超市"]
    record = []
    for symbol_idx in range(len(symbols)):
        symbol = symbols[symbol_idx]
        stock_name = stock_names[symbol_idx]
        date_price = get_realtime_price(symbol, '5')
        # date_price = [{'2020-07-20':[7.95, 7.95, 7.95, 7.95, 7.95, 7.95, 7.91, 7.87, 7.62, 7.6, 7.62, 7.61, 7.65, 7.6, 7.66, 7.61, 7.61, 7.68, 7.64, 7.59, 7.56, 7.61, 7.56, 7.67, 7.67, 7.67, 7.67, 7.67, 7.67, 7.68, 7.73, 7.75, 7.79, 7.79, 7.79, 7.75, 7.74, 7.75, 7.71, 7.82, 7.8, 7.89, 7.85, 7.91, 7.89, 7.92, 7.88, 7.95]}]
        # print(date_price[0])
        try:

            start_price = date_price[0][1][0]
            init_money = start_price * 0.8
            start_own = 900
            stock = {
                '初始资金': init_money + start_price * start_own,
                '当前资金': init_money + start_price * start_own,
                '可用余额': init_money,
                '持有股份': start_own,
                '可用股份': start_own,
                '冻结股份': 0,
                '初始价格': start_price,
                '当前成本': start_price,
                '最新价格': start_price,
                '买卖总手数': 0,
                '总资金增长率': 0,
                '股价波动率': 0
            }
        except KeyError as e:
            print(e)
        # rate = 0.005
        buy_rate = rate
        sell_rate = rate
        sell = 0
        buy = 0
        # amount = 200
        lock = 3
        operate_price = date_price[0][1][0]
        for day in date_price:
            price = day[1]
            for now_price in price[1:]:
                min_count = min(sell, buy)
                if now_price > operate_price * (sell_rate+1):
                    if abs(sell - buy) > lock and now_price > operate_price * (randint(lock//2, lock) * sell_rate+1):
                        continue
                    sell += 1
                    operate(stock, now_price, amount, 's', record)
                    operate_price = now_price
                    sell_rate *= (sell - min_count)
                if now_price * (1+buy_rate) < operate_price:
                    if abs(sell - buy) > lock and now_price * (1 + randint(lock//2, lock) * buy_rate) < operate_price:
                        continue
                    buy += 1
                    operate(stock, now_price, amount, 'b', record)
                    operate_price = now_price
                    buy_rate *= (buy - min_count)
            stock['最新价格'] = price[-1]
            kaishi = len(record)
            skip_oneday(stock, price[-1], record)
            if len(record) - kaishi == 1:
                # print(price)
                pass
        # print(stock_name, ":", stock, '\n')
    return stock, record

if __name__ == '__main__':
    symbols = [
                "000725",
               "002517",
               "600291",
               "000759",
               "600196",
               "600048",
               "002164",
               "002837",
               "600723",
                "600438",
                "600276",
                "603187",
                "002457",
                "601607",
                "000557",
                "000157",
                "002079",
                "601988",
               ]
    stock_names = [
                    '京东方A',
                   '恺英网络',
                   '西水股份',
                   '中百集团',
                   '复星医药',
                   '保利地产',
                   "宁波东力",
                   "英维克",
                   "首商集团",
                    "通威股份",
                    "恒瑞医药",
                    "海容冷链",
                    "青龙管业",
                    "上海医药",
                    "西部创业",
                    "中联重科",
                    "苏州固锝",
                    "中国银行",
                   ]
    for idx in range(len(symbols)):
        symbol = [symbols[idx]]
        stock_name = [stock_names[idx]]
        if stock_name[0] != '复星医药':
            continue
        Max_stock = None
        profit = -1
        Max_rate = 0
        Max_amount = 0
        Max_record = []
        for rate in range(2,10):
            for amount in range(0,3):
                stock , record= test((rate+2) * 0.001, (amount + 1) * 100, symbol, stock_name)
                if stock['总资金增长率'] > profit:
                    profit = stock['总资金增长率']
                    Max_stock = stock
                    Max_rate = (rate+2) * 0.001
                    Max_amount = (amount + 1) * 100
                    Max_record = record
        print("\n最优横跳率:%s, 最优每次横跳手数:%s"%(Max_rate, Max_amount), '\n', stock_name[0], Max_stock, "\n\n")
        for item in Max_record:
            print(item)