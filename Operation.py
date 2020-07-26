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

def operate(stock_position, price, amount, operation):
    if operation == 'b':
        if stock_position['money'] < amount * price:
            return
        stock_position['cost'] = (stock_position['cost'] * stock_position['own'] + price * amount ) / (stock_position['own']  + amount)
        stock_position['own'] += amount
        stock_position['money'] -= amount * price
        stock_position['freeze'] += amount
        # print("===>>>>买入成功！价格：%s，数量：%s，当前持仓：%s, 当前可用：%s，价格成本：%s"%(price, amount, stock_position['own'], stock_position['use'], stock_position['cost']))
    elif operation == 's':
        if stock_position['use'] < amount:
            return
        if stock_position['own'] - amount == 0:
            print("清仓！")
            stock_position['cost'] = 0
        else:
            stock_position['cost'] = (stock_position['cost'] * stock_position['own'] - price * amount) / (stock_position['own'] - amount)
        stock_position['own'] -= amount
        stock_position['use'] -= amount
        stock_position['money'] += amount * price
        # print("<<<===卖出成功！价格：%s，数量：%s，当前持仓：%s, 当前可用：%s, 价格成本：%s"%(price, amount, stock_position['own'], stock_position['use'], stock_position['cost']))


def skip_oneday(stock_position):
    stock_position['position'] = stock_position['own'] * stock_position['cost'] + stock_position['money']
    stock_position['use'] = stock_position['own']
    stock_position['freeze'] = 0


def test():
    from Data import get_realtime_price
    symbols = ["002164", "002517", "002457", "600723", "600918", "600720", "603187", "002271", "000759", "000735",
              "601933"]
    stock_names = ["宁波东力", "恺英网络", "青龙管业", "首商股份", "中泰证券", "祁连山", "海容冷链", "东方雨虹", "中百集团", "罗牛山", "永辉超市"]
    for symbol in symbols:
        print("\n\n%s"%stock_names[symbols.index(symbol)])
        date_price = get_realtime_price(symbol)
        try:
            stock = {
            'position': 10000 + date_price[0][1][0]*1000,
            'money':10000,
            'own':1000,
            'use':1000,
            'freeze':0,
            'cost':date_price[0][1][0],
            }
        except KeyError as e:
            continue
        print(stock)
        for day in date_price:
            price = day[1]
            sell_price = 0
            buy_price = 0
            for idx in range(len(price) - 10):
                data = price[:10+idx]
                y2 = predict(data)
                if y2[0] == 0:
                    continue
                if sell_price != 0 and price[10 + idx] >= sell_price:
                    operate(stock, price[10 + idx], 100, 's')
                    sell_price = 0
                    continue
                if buy_price != 0 and price[10 + idx] <= buy_price:
                    operate(stock, price[10 + idx], 100, 'b')
                    buy_price = 0
                    continue
                pre_max = max(y2[-20:])
                pre_min = min(y2[-20:])
                if pre_max >= price[10+idx] * 1.01 and pre_max > stock['cost']:
                    operate(stock, price[10 + idx], 100, 'b')
                    sell_price = pre_max
                    continue
                if pre_min * 1.01 <= price[10+idx] and pre_min < stock['cost']:
                    operate(stock, price[10 + idx], 100, 's')
                    buy_price = pre_min
                    continue
            skip_oneday(stock)
            print(stock)

if __name__ == '__main__':
    test()
