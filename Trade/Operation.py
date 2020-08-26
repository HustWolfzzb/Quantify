from random import randint

import tushare as ts

from datetime import datetime, time, date
from time import sleep
import easyquotation
# from Strategy import nihe
from DataEngine.Data import get_realtime_price, get_pro


# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
MORNING_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

symbol = ["002164","002517","002457","600723","600918","600720","603187","002271","000759","000735","601933"]
stock_name =["宁波东力","恺英网络","青龙管业","首商股份","中泰证券","祁连山","海容冷链","东方雨虹","中百集团","罗牛山","永辉超市"]
stock_code = { symbol[x]:stock_name[x] for x in range(len(symbol))}

def is_openMartket(pro):
    today_date = str(date.today().isoformat()).replace('-', '')
    is_open = list(pro.query('trade_cal', start_date=today_date, end_date=today_date).is_open)[0]
    if is_open == 0:
        return -2
    current_time = datetime.now().time()
    if not ((current_time > MORNING_START and current_time < AFTERNOON_END )):
        return -1
    elif not ((current_time > MORNING_START and current_time < DAY_END) or (current_time >AFTERNOON_START and current_time < AFTERNOON_END )):
        return 0
    return 1

# def predict(graph_data):
#     para, func, func_min_offset = nihe(graph_data)
#     if func_min_offset == -1:
#         return [0]
#     x2 = np.arange(0, len(graph_data) + 20)
#     y2 = None
#     if func_min_offset == 0 or func_min_offset == 2:
#         A, B, C = para
#         y2 = func(x2, A, B, C)
#     elif func_min_offset == 1:
#         A, B, C, D = para
#         y2 = func(x2, A, B, C, D)
#     elif func_min_offset == 3:
#         A, B = para
#         y2 = func(x2, A, B)
#     return y2

def operate(stock_position, price, amount, operation, record):
    if operation == 'b':
        if stock_position['可用余额'] < amount * price:
            record.append("资金不足")
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

def skip_oneday(stock_position, close_price, record, day):
    stock_position['最新价格'] = round(close_price,2)
    stock_position['当前资金'] = round(stock_position['持有股份'] * stock_position['最新价格'] + stock_position['可用余额'], 2)
    stock_position['可用股份'] = stock_position['持有股份']
    stock_position['冻结股份'] = 0
    stock_position['可用余额'] = round(stock_position['可用余额'], 2)

    # stock_position['买卖总手数'] = 0
    stock_position['总资金增长率'] = round((stock_position['当前资金'] - stock_position['初始资金'])/stock_position['初始资金'],4)
    stock_position['股价波动率'] = round((stock_position['最新价格'] - stock_position['初始价格'])/stock_position['初始价格'],4)
    record.append("↑"*10 + str(day) + "↑"*10)

def test(rate = 0.003, amount = 200, symbols=[] , stock_names=[] ):
    record = []
    for symbol_idx in range(len(symbols)):
        symbol = symbols[symbol_idx]
        stock_name = stock_names[symbol_idx]
        date_price = get_realtime_price(symbol, '5')

        try:
            start_price = date_price[0][1][0]
            # start_price = 68.7
            start_own = 2000
            init_money = start_price * start_own
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
        # operate_price = 68.7
        operate_price = date_price[0][1][0]
        sell_record = []
        buy_record = []
        for day in date_price:
            price = day[1]
            operate_price = price[0]
            for now_price in price[1:]:
                min_count = min(sell, buy)
                if now_price > operate_price * (sell_rate + 1):
                    if sell - buy > lock :
                    # if sell - buy > lock and now_price < operate_price * (randint(lock, 2 * lock) * sell_rate + 1):
                        continue
                    if len(buy_record) > 0:
                        if now_price > buy_record[-1]:
                            buy_record.pop()
                        else:
                            continue
                    sell += 1
                    operate(stock, now_price, amount, 's', record)
                    operate_price = now_price
                    if sell - min_count == 0:
                        sell_rate = rate
                        continue
                    sell_rate = rate * (sell - min_count)
                    sell_record.append(now_price)
                if now_price * (1 + buy_rate) < operate_price:
                    if buy - sell > lock :
                    # if buy - sell > lock and now_price * (1 + randint(lock, 2 * lock) * buy_rate) > operate_price:
                        continue
                    if len(sell_record) > 0:
                        if now_price < sell_record[-1]:
                            sell_record.pop()
                        else:
                            continue
                    buy += 1
                    operate(stock, now_price, amount, 'b', record)
                    operate_price = now_price
                    if (buy - min_count) == 0:
                        buy_rate = rate
                        continue
                    buy_rate = rate * (buy - min_count)
                    buy_record.append(now_price)
            stock['最新价格'] = price[-1]
            kaishi = len(record)
            skip_oneday(stock, price[-1], record)
            if len(record) - kaishi == 1:
                # print(price)
                pass
        # print(stock_name, ":", stock, '\n')
    return stock, record

def ZhongBai(rate = 0.002, amount = 100 , k_type='5'):
    record = []
    symbol = '000759'
    stock_name = '中百集团'
    date_price = get_realtime_price(symbol, k_type)

    try:
        start_price = date_price[0][1][0]
        # start_price = 68.7
        start_own = 900
        init_money = start_price * start_own
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

    buy_times = 1
    sell_times = 1
    buy_rate = rate * buy_times
    sell_rate = rate * sell_times
    sell = 0
    buy = 0
    lock = 5
    # operate_price = 68.7
    operate_price = 0
    sell_record = []
    buy_record = []
    count = 0
    for day in date_price:
        count += 1
        price = day[1]
        if operate_price == 0:
            operate_price = price[0]
        # operate_price = price[0]
        for now_price in price[1:]:
            buy_record.sort()
            buy_record.reverse()
            sell_record.sort()
            sell_record.reverse()
            if now_price > operate_price * (sell_rate + 1):
                # if sell - buy > lock :
                if sell - buy > lock and now_price < operate_price * (randint(lock, 2 * lock) * sell_rate + 1):
                    continue
                operate(stock, now_price, amount * (sell_times), 's', record)
                sell += sell_times
                sell_times += 1
                buy_times -= 1
                if buy_times < 1:
                    buy_times = 1
                operate_price = now_price
                sell_rate = sell_times * rate


            if now_price * (1 + buy_rate) < operate_price:
                # if buy - sell > lock :
                if buy - sell > lock and now_price * (1 + randint(lock, 2 * lock) * buy_rate) > operate_price:
                    continue
                if len(sell_record) > 0 and now_price > sell_record[0]:
                    continue
                operate(stock, now_price, amount * (buy_times), 'b', record)
                buy += buy_times
                buy_times += 1
                sell_times -= 1
                if sell_times < 1:
                    sell_times = 1
                operate_price = now_price
                buy_rate = rate * buy_times
        stock['最新价格'] = price[-1]
        kaishi = len(record)
        skip_oneday(stock, price[-1], record, day[0])
        if len(record) - kaishi == 1:
            # print(price)
            pass
        # print(stock_name, ":", stock, '\n')
    return stock, record

def base_line(rate = 0.002, amount = 100 , k_type='5'):
    record = []
    symbol = '000759' \
             ''
    stock_name = '中百集团'
    date_price = get_realtime_price(symbol, k_type)

    try:
        start_price = date_price[0][1][0]
        # start_price = 68.7
        start_own = 900
        init_money = start_price * start_own
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

    buy_times = 1
    sell_times = 1
    buy_rate = rate * buy_times
    sell_rate = rate * sell_times
    sell = 0
    buy = 0
    lock = 5
    # operate_price = 68.7
    operate_price = 0
    sell_record = []
    buy_record = []
    count = 0
    buy = 0
    sell_price = 0
    buy_price = 0
    for day in date_price:
        count += 1
        price = day[1]
        if operate_price == 0:
            operate_price = price[0]
        operate_price = price[0]
        for now_price in price[1:]:
            if now_price > operate_price * (sell_rate + 1):
                # if sell - buy > lock :
                if buy >= 0:
                    if now_price < buy_price:
                        continue
                    operate(stock, now_price, 400, 's', record)
                    sell_price = now_price
                    buy -= 1

            if now_price * (1 + buy_rate) < operate_price:
                if buy <= 0:
                    if now_price > sell_price:
                        continue
                    operate(stock, now_price, amount * (buy_times), 'b', record)
                    buy += 1
                    buy_price = now_price

        stock['最新价格'] = price[-1]
        kaishi = len(record)
        skip_oneday(stock, price[-1], record, day[0])
        if len(record) - kaishi == 1:
            # print(price)
            pass
        # print(stock_name, ":", stock, '\n')
    return stock, record


def JiZhunCeLue(rate = 0.002, amount = 100 , k_type='15'):
    record = []
    symbol = '000759'
    stock_name = '中百集团'
    date_price = get_realtime_price(symbol, k_type)

    try:
        start_price = date_price[0][1][0]
        # start_price = 68.7
        start_own = 1600
        init_money = start_price * start_own * 2
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

    smallest_rate = 0.01
    buy_amount = [100]
    for i in range(10):
        buy_amount.append(buy_amount[-1] + 100)
    sell_rate = [0.5] * 10

    operate_price = 0
    cost_price = start_price
    for day in date_price:
        buy_record = [0] * 10
        sell_record = [0] * 10
        price = day[1]
        if operate_price == 0:
            operate_price = price[0]
        operate_price = price[0]
        operate_price = max(cost_price, operate_price)
        for now_price in price[1:]:
            if now_price > operate_price:
                times = int( (now_price - operate_price ) / operate_price // smallest_rate)
                if times >= 10:
                    times = 9
                sell_amount = int((sell_rate[times - 1] * stock['可用股份'])// 100 * 100)
                if sell_record[times] != 0 or times == 0 or sell_amount == 0:
                    continue
                else:
                    if stock['持有股份'] <= sell_amount - 100:
                        sell_amount = stock['持有股份'] - 100
                    if sell_amount == 0:
                        continue
                    operate(stock, now_price, sell_amount, 's', record)
                    sell_record[times] = 1
            if now_price < operate_price:
                times = int((operate_price - now_price) / operate_price // smallest_rate)
                if times >= 10:
                    times = 9
                b_amount = buy_amount[times]
                if buy_record[times] != 0 or b_amount < 100 or times == 0:
                    continue
                operate(stock, now_price, b_amount, 'b', record)
                buy_record[times] = 1
        cost_price = stock['当前成本']
        stock['最新价格'] = price[-1]
        kaishi = len(record)
        skip_oneday(stock, price[-1], record, day[0])
        if len(record) - kaishi == 1:
            # print(price)
            pass
        # print(stock_name, ":", stock, '\n')
    return stock, record


def new_test(rate = 0.003, amount = 100, symbols=[] , stock_names=[] ):
    record = []
    for symbol_idx in range(len(symbols)):
        symbol = symbols[symbol_idx]
        stock_name = stock_names[symbol_idx]
        date_price = get_realtime_price(symbol, '5')

        try:
            start_price = date_price[0][1][0]
            # start_price = 68.7
            init_money = start_price * 900
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
        # operate_price = 68.7
        # operate_price = date_price[0][1][0]
        record = []
        re_log = []
        sell_times = cal_rate_times(record, 0)
        buy_times = cal_rate_times(record, 1)
        operate_price = 0
        for day in date_price:
            price = day[1]
            if operate_price == 0:
                operate_price = price[0]
            for now_price in price[1:]:
                if now_price > operate_price * 1.003:
                    if sell - buy > lock:
                    # if sell - buy > lock and now_price < operate_price * (randint(lock, 2 * lock) * sell_rate + 1):
                        continue
                    if not can_I_go(record, now_price, 0):
                        continue
                    sell += 1
                    operate(stock, now_price, amount * ((sell_times + 1) // 2), 's', re_log)
                    operate_price = now_price
                    record.append({'Type':0, 'price':now_price, 'amount': amount * ((sell_times + 1) // 2) })
                if now_price * 1.003 < operate_price:
                    if buy - sell > lock :
                    # if buy - sell > lock and now_price * (1 + randint(lock, 2 * lock) * buy_rate) > operate_price:
                        continue
                    if not can_I_go(record, now_price, 1):
                        continue
                    buy += 1
                    operate(stock, now_price, amount, 'b', re_log)
                    operate_price = now_price
                    record.append({'Type':1, 'price':now_price, 'amount': amount * ((buy_times + 1) // 2) })
            stock['最新价格'] = price[-1]
            kaishi = len(re_log)
            skip_oneday(stock, price[-1], re_log)
            if len(re_log) - kaishi == 1:
                # print(price)
                pass
        # print(stock_name, ":", stock, '\n')
    return stock, re_log

def cal_rate_times(record, type):
    record_type = [ x['Type'] for x in record[-1::-1] ]
    times = 1
    if len(record_type) != 0:
        while times <= len(record_type) and record_type[times - 1] == type :
            times += 1
    return times

def can_I_go(record, price, type):
    re_price = 0
    if type == 0:
        buy = 0
        sell = 1
        for rec in record[-1::-1]:
            if sell == buy:
                re_price = rec['price']
                if re_price < price:
                    return True
                else:
                    return False
            if rec['Type'] == 0:
                sell += 1
            elif rec['Type'] == 1:
                buy += 1
    elif type == 1:
        buy = 1
        sell = 0
        for rec in record[-1::-1]:
            if sell == buy:
                re_price = rec['price']
                if re_price > price:
                    return True
                else:
                    return False
            if rec['Type'] == 0:
                sell += 1
            elif rec['Type'] == 1:
                buy += 1
    if re_price == 0:
        return True
    else:
        return False

def update_Lock_para(para):
    with open('../cache/lock_para.txt', 'w', encoding='utf8') as f:
        f.write(str(para))

def run(user, rate = 0.01, amount = 100):
    with open('../cache/lock_para.txt', 'r', encoding='utf8') as f:
        para = eval(f.read())
    stocks = user.stock.get_position()
    symbols = []
    stock_names = []
    pro = get_pro()
    print(stocks)
    for s in range(len(stocks)):
        symbols.append(stocks[s]['证券代码'])
        stock_names.append(stocks[s]['证券名称'])
    yue = user.get_balance()
    time = is_openMartket(pro)
    count = 0
    gap = 3
    while (True):
        if count == 0:
            time = is_openMartket(pro)
            if time == -1:
                sleep(120)
                continue
            elif time == -2:
                break
            elif time == 0:
                sleep(120)
                continue
        count += 1
        if not count < 600 / gap:
            count = 0
        for symbol_idx in range(len(symbols)):
            symbol = symbols[symbol_idx]
            stock_name = stock_names[symbol_idx]
            try:
                now_price = float(list(ts.get_realtime_quotes(symbol).price)[0])
            except Exception as e:
                print(e)
                sleep(10)
                continue
            sell_times = cal_rate_times(para[stock_name]['record'], 0)
            buy_times = cal_rate_times(para[stock_name]['record'], 1)
            para[stock_name]['sell_rate'] = sell_times * rate
            para[stock_name]['buy_rate'] = buy_times * rate
            if now_price > para[stock_name]['operate_price'] * (para[stock_name]['sell_rate'] + 1):
                if para[stock_name]['sell'] - para[stock_name]['buy'] > para[stock_name]['lock'] \
                        and now_price < para[stock_name]['operate_price'] * (randint(para[stock_name]['lock'], para[stock_name]['lock'] * 2) * para[stock_name]['sell_rate'] + 1):
                    continue
                if not can_I_go(para[stock_name]['record'], now_price, 0):
                    continue
                try:
                    user.sell(symbol, now_price, para[stock_name]['amount'] * ((sell_times + 1) // 2) )
                    yue += now_price * para[stock_name]['amount']
                    para[stock_name]['sell'] += 1
                    para[stock_name]['operate_price'] = now_price
                    para[stock_name]['record'].append({'Type': 0, 'price': now_price, 'amount': para[stock_name]['amount'] * ((sell_times + 1) // 2)})
                    update_Lock_para(para)
                except Exception as e:
                    print(e)
            elif now_price * (1 + para[stock_name]['buy_rate']) < para[stock_name]['operate_price']:
                if para[stock_name]['sell'] - para[stock_name]['buy'] > para[stock_name]['lock'] \
                        and now_price * (1 + randint(para[stock_name]['lock'], para[stock_name]['lock'] * 2) * para[stock_name]['buy_rate']) > para[stock_name]['operate_price']:
                    continue
                if not can_I_go(para[stock_name]['record'], now_price, 1):
                    continue

                try:
                    if yue < now_price * para[stock_name]['amount']:
                        print("没钱了")
                        continue
                    user.buy(symbol, now_price, para[stock_name]['amount'] * ((buy_times + 1) // 2))
                    para[stock_name]['buy'] += 1
                    yue -= now_price * para[stock_name]['amount']
                    para[stock_name]['operate_price'] = now_price
                    para[stock_name]['record'].append({'Type': 1, 'price': now_price, 'amount': para[stock_name]['amount'] * ((buy_times + 1) // 2)})
                    update_Lock_para(para)
                except Exception as e:
                    print(e)
        sleep(120)

def run_ZhongBai(user, rate = 0.004, amount = 200):
    print("正在监测中百集团")
    stocks = user.stock.get_position()
    symbols = []
    stock_names = []
    pro = get_pro()
    print(stocks)
    for s in range(len(stocks)):
        symbols.append(stocks[s]['证券代码'])
        stock_names.append(stocks[s]['证券名称'])
    yue = user.get_balance()
    buy_times = 1
    sell_times = 1
    sell = 0
    buy = 0
    lock = 4
    # operate_price = 68.7
    operate_price = 7.08
    sell_record = []
    buy_record = []
    symbol = '000759'
    stock_name = '中百集团'
    count = 0
    gap = 3
    while (True):
        if count == 0:
            time = is_openMartket(pro)
            if time == -1:
                sleep(120)
                continue
            elif time == -2:
                break
            elif time == 0:
                sleep(120)
                continue
        count += 1
        if not count < 600 / gap:
            count = 0

        buy_rate = rate * buy_times
        sell_rate = rate * sell_times
        try:
            now_price = float(list(ts.get_realtime_quotes(symbol).price)[0])
        except Exception as e:
            print("Here", e)
            sleep(10)
            continue


        if now_price > operate_price * (sell_rate + 1):
            # if sell - buy > lock :
            if sell - buy > lock and now_price < operate_price * (randint(lock, 2 * lock) * sell_rate + 1):
                continue
            try:
                user.sell(symbol, now_price, amount * (sell_times))
                print("卖出%s，价格%s， 数量%s"%(stock_name, now_price, amount *sell_times))
                yue += now_price * amount * (sell_times)
                sell += 1
                sell_times += 1
                buy_times -= 1
                if buy_times < 1:
                    buy_times = 1
                operate_price = now_price
                sell_record.append(now_price)
            except Exception as e:
                print("now", e)

        if now_price * (1 + buy_rate) < operate_price:
            # if buy - sell > lock :
            if buy - sell > lock and now_price * (1 + randint(lock, 2 * lock) * buy_rate) > operate_price:
                continue
            try:
                if yue < now_price * amount * (buy_times ):
                    print("没钱了")
                    continue
                user.buy(symbol, now_price,  amount * (buy_times ))
                print("买入%s，价格%s， 数量%s"%(stock_name, now_price, amount *buy_times))

                buy += 1
                buy_times += 1
                sell_times -= 1
                if sell_times < 1:
                    sell_times = 1
                operate_price = now_price
                buy_record.append(now_price)
            except Exception as e:
                print(e)

        sleep(gap)

def run_ShangYi(user, rate = 0.01, amount = 100 ):
    sleep(1.5)
    print("正在监测上海医药")
    pro = get_pro()
    yue = user.get_balance()
    buy_times = 1
    sell_times = 1
    sell = 0
    buy = 0
    lock = 4
    # operate_price = 68.7
    operate_price = 22.66
    sell_record = []
    buy_record = []
    symbol = '601607'
    stock_name = '上海医药'
    count = 0
    gap = 3
    while (True):
        if count == 0:
            time = is_openMartket(pro)
            if time == -1:
                sleep(120)
                continue
            elif time == -2:
                break
            elif time == 0:
                sleep(120)
                continue
        count += 1
        if not count < 600 / gap:
            count = 0

        buy_rate = rate * buy_times
        sell_rate = rate * sell_times
        try:
            now_price = float(list(ts.get_realtime_quotes(symbol).price)[0])
        except Exception as e:
            print("Here", e)
            sleep(10)
            continue

        if now_price > operate_price * (sell_rate + 1):
            # if sell - buy > lock :
            if sell - buy > lock and now_price < operate_price * (randint(lock, 2 * lock) * sell_rate + 1):
                continue
            try:
                user.sell(symbol, now_price, amount * (sell_times))
                print("卖出%s，价格%s， 数量%s"%(stock_name, now_price, amount *sell_times))
                yue += now_price * amount * (sell_times)
                sell += sell_times
                sell_times += 1
                buy_times -= 1
                if buy_times < 1:
                    buy_times = 1
                operate_price = now_price
                for x in range(sell_times):
                    sell_record.append(now_price)
            except Exception as e:
                print("now", e)

        if now_price * (1 + buy_rate) < operate_price:
            # if buy - sell > lock :
            if buy - sell > lock and now_price * (1 + randint(lock, 2 * lock) * buy_rate) > operate_price:
                continue
            try:
                if yue < now_price * amount * (buy_times):
                    print("没钱了")
                    continue
                user.buy(symbol, now_price,  amount * (buy_times))
                print("买入%s，价格%s， 数量%s"%(stock_name, now_price, amount * buy_times))
                buy += 1
                buy_times += buy_times
                sell_times -= 1
                if sell_times < 1:
                    sell_times = 1
                operate_price = now_price
                for x in range(buy_times):
                    buy_record.append(now_price)
            except Exception as e:
                print(e)

        sleep(gap)


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
                "601933",
                "000736",
                "600272",
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
                    "永辉超市",
                    "罗牛山",
                    "开开实业",
                   ]
    for idx in range(len(symbols)):
        # symbol = [symbols[idx]]
        # stock_name = [stock_names[idx]]
        if not (stock_names[0] == '中百集团'):
            continue
        # Max_stock = None
        # profit = -1
        # Max_rate = 0
        # Max_amount = 0
        # Max_record = []
        # for rate in range(1,2):
        #     for amount in range(0,3):
        #         stock , record= new_test((rate+2) * 0.001, (amount + 1) * 100, symbol, stock_name)
        #         if stock['总资金增长率'] > profit:
        #             profit = stock['总资金增长率']
        #             Max_stock = stock
        #             Max_rate = (rate+2) * 0.001
        #             Max_amount = (amount + 1) * 100
        #             Max_record = record
        # print("\n最优横跳率:%s, 最优每次横跳手数:%s"%(Max_rate, Max_amount), '\n', stock_name[0], Max_stock, "\n\n")
    freq_days = {
        '5':8,
        '15':24,
        '60':88
    }
    # print("中百集团，原始手数9手，原始可用资金与股票市值相等\n\n")
    stock, record = JiZhunCeLue()
    print(stock)
    for item in record:
        print(item)
    # from HaiTong import get_Account
    # user = get_Account()
