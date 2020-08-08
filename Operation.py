from random import random, randint

import tushare as ts

from datetime import datetime, time, timedelta
from time import sleep
import numpy as np

from HaiTong import get_Account
from Strategy import nihe

# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
DAY_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

symbol = ["002164","002517","002457","600723","600918","600720","603187","002271","000759","000735","601933"]
stock_name =["宁波东力","恺英网络","青龙管业","首商股份","中泰证券","祁连山","海容冷链","东方雨虹","中百集团","罗牛山","永辉超市"]
stock_code = { symbol[x]:stock_name[x] for x in range(len(symbol))}
from Data import get_realtime_price


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
    record = []
    for symbol_idx in range(len(symbols)):
        symbol = symbols[symbol_idx]
        stock_name = stock_names[symbol_idx]
        date_price = get_realtime_price(symbol, '5')

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
        buy_rate = rate
        sell_rate = rate
        sell = 0
        buy = 0
        lock = 5
        operate_price = date_price[0][1][0]
        for day in date_price:
            price = day[1]
            for now_price in price[1:]:
                min_count = min(sell, buy)
                if now_price > operate_price * (sell_rate+1):
                    if abs(sell - buy) > lock and now_price < operate_price * (randint(lock//2, lock) * sell_rate+1):
                        continue
                    sell += 1
                    operate(stock, now_price, amount, 's', record)
                    operate_price = now_price
                    sell_rate *= (sell - min_count)
                if now_price * (1+buy_rate) < operate_price:
                    if abs(sell - buy) > lock and now_price * (1 + randint(lock//2, lock) * buy_rate) > operate_price:
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


def run(user, rate = 0.003, amount = 200):
    with open('cache/para.txt','r', encoding='utf8') as f:
        para = eval(f.read())
    stocks = user.stock.get_position()
    symbols = []
    stock_names = []
    print(stocks)
    for s in range(len(stocks)):
        symbols.append(stocks[s]['证券代码'])
        stock_names.append(stocks[s]['证券名称'])

    times = 1
    while (True):
        sleep(1)
        times += 1
        if times > 15:
            break
        # time = is_openMartket()
        # if time == -1:
        #     sleep(120)
        #         #     continue
        # if time == 0:
        #     sleep(120)
        #     continue
        # else:
        #     sleep(120)
        for symbol_idx in range(len(symbols)):
            symbol = symbols[symbol_idx]
            stock_name = stock_names[symbol_idx]
            now_price = float(list(ts.get_realtime_quotes(symbol).price)[0])
            min_count = min(para[stock_name]['sell'], para[stock_name]['buy'])
            if now_price > para[stock_name]['operate_price'] * (para[stock_name]['sell_rate'] + 1):
                if abs(para[stock_name]['sell'] - para[stock_name]['buy']) > para[stock_name]['lock'] and now_price < para[stock_name]['operate_price'] * (
                        randint(para[stock_name]['lock'], para[stock_name]['lock']*2) * para[stock_name]['sell_rate'] + 1):
                    continue
                para[stock_name]['sell'] += 1
                user.sell(symbol, now_price, para[stock_name]['amount'])
                para[stock_name]['operate_price'] = now_price
                para[stock_name]['sell_rate'] *= (para[stock_name]['sell'] - min_count)

            if now_price * (1 + para[stock_name]['buy_rate']) < para[stock_name]['operate_price']:
                if abs(para[stock_name]['sell'] - para[stock_name]['buy']) > para[stock_name]['lock'] and now_price * (1 + randint(para[stock_name]['lock'] // 2, para[stock_name]['lock']) * para[stock_name]['buy_rate']) > para[stock_name]['operate_price']:
                    continue
                para[stock_name]['buy'] += 1
                user.buy(symbol, now_price, para[stock_name]['amount'])
                para[stock_name]['operate_price'] = now_price
                para[stock_name]['buy_rate'] *= (para[stock_name]['buy'] - min_count)

    with open('cache/para.txt', 'w', encoding='utf8') as f:
        f.write(str(para))


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

    run(get_Account())