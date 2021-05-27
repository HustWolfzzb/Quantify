import json
import os

from DataEngine.Data import get_qo
from Trade.Operation import Trader
import time

def save_trade_log_once(code, price, amount):
    string = json.dumps({code:{'price':price, 'amount':amount}})
    with open('cache/%s-log.txt'%code, 'w', encoding='utf8') as log:
        log.write(string)

def load_trade_log_once(code):
    with open('cache/%s-log.txt'%code, 'r', encoding='utf8') as f:
        return json.load(f)

def save_gaps_once(gaps):
    string = json.dumps(gaps)
    with open('cache/gaps.txt', 'w', encoding='utf8') as log:
        log.write(string)

def load_gaps():
    with open('cache/gaps.txt', 'r', encoding='utf8') as f:
        return json.load(f)

def save_rates_once(rates):
    string = json.dumps(rates, indent=4)
    with open('cache/rates.txt', 'w', encoding='utf8') as log:
        log.write(string)

def load_rates():
    with open('cache/rates.txt', 'r', encoding='utf8') as f:
        return json.load(f)


qo = get_qo()
def get_all_price(codes=['512900','515650','159801','515880']):
    return qo.stocks(codes)

def abs_reduce(x, y):
    if x > y:
        return x - y
    else:
        return y - x

def grid_bs(codes, user):
    # start = False
    count = 0
    buy_amount_base = 100
    sell_amount_base = 100
    buy_rates = load_rates()['buy']
    sell_rates = load_rates()['sell']
    gaps = load_gaps()
    print(gaps)
    operate_prices=[]
    for c in codes:
        operate_prices.append(float(load_trade_log_once(c)[c]['price']))
    print(operate_prices)
    buyer = Trader(user, codes[0], operate_prices[0], 100, 'b')
    seller = Trader(user, codes[0], operate_prices[0], 100, 's')
    p = get_all_price(codes)
    closes = [p[code]['close'] for code in codes]
    print(closes)
    while True:
        time.sleep(0.5)
        p = get_all_price(codes)
        count += 1
        price_nows = [p[code]['now'] for code in codes]
        closes = [p[code]['close'] for code in codes]
        for i in range(len(codes)):
            try:
                code = codes[i]
                close = closes[i]
                gap = gaps[code]
                buy_rate = buy_rates[code]
                sell_rate = sell_rates[code]

                price_now = price_nows[i]
                operate_price = operate_prices[i]

                # if count % 3600 == 0:
                    # print("\r%s:【Pirce:%s, Gap:%s, Operate:%s】 " % (code, price_now, gap, operate_price))
                if price_now < operate_price - gap * buy_rate:
                    buy_price = round(operate_price - gap, 3)
                    # buy_amount = buy_amount_base
                    buy_amount = buy_amount_base * int(abs_reduce(price_now, close) // (gap * 3) + 1)
                    # if code[:3] == '513':
                    #     buy_amount = 300
                    buy_id = buyer.trade(code, buy_price, buy_amount, 'b')
                    print("Price  Now:%s, Operate_price:%s】" % (price_now, buy_price))
                    save_trade_log_once(code, buy_price, buy_amount)
                    operate_prices[i] = buy_price

                if price_now > operate_price + gap * sell_rate:
                    sell_price = round(operate_price + gap, 3)
                    sell_amount = sell_amount_base
                    # sell_amount = sell_amount_base  * int(abs_reduce(price_now, close) // (gap * 3) + 1)
                    # if code[:3] == '513':
                    #     sell_amount = 300
                    sell_id = seller.trade(code, sell_price, sell_amount, 's')
                    save_trade_log_once(code, sell_price, sell_amount)
                    print("Price  Now:%s, Operate_price:%s" % (price_now, sell_price))
                    operate_prices[i] = sell_price
            except KeyError as e:
                print(e)
            except Exception as e:
                if str(e).find('客户股票不足'):
                    print('客户%s股票不足'%codes[i])
                    return code

