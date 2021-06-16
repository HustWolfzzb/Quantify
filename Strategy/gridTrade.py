import json
import os
import datetime
from DataEngine.Data import get_qo, get_stock_name, get_fund_name
from Trade.Operation import Trader
import time

code_name = {k[:6]:v for k,v in get_stock_name().items()}
fund_name = {k[:6]:v for k,v in get_fund_name().items()}
for i in fund_name.keys():
    code_name[i] = fund_name[i]

fund_codes= [x[:6] for x in fund_name.keys()]

def code2name(codes, operate={}, gaps={}, close={}, buy_r={}, sell_r = {}):
    existFile = [ x[:6] for x in os.listdir('cache/') if x[:6] in codes]
    for i in existFile:
        if len(operate) == 0:
            print("%s:%s"%(i, code_name[i]))
        else:
            try:
                print("%s:%s, op:%s, gap:%s, close:%s, buy_rate:%s, sell_rate:%s"%(i, code_name[i], operate[i], gaps[i], close[i], buy_r[i], sell_r[i]))
            except Exception as e:
                print("%s:%s" % (i, 'None'))

def save_trade_log_once(code, price, amount):
    string = json.dumps({code:{'price':price, 'amount':amount}}, indent=4)
    with open('cache/%s-log.txt'%code, 'w', encoding='utf8') as log:
        log.write(string)

def load_trade_log_once(code):
    with open('cache/%s-log.txt'%code, 'r', encoding='utf8') as f:
        return json.load(f)

def save_gaps_once(gaps):
    string = json.dumps(gaps, indent=4)
    with open('cache/gaps.txt', 'w', encoding='utf8') as log:
        log.write(string)

def load_gaps():
    with open('cache/gaps.txt', 'r', encoding='utf8') as f:
        return json.load(f)

def save_rates_once(rates, type):
    string = json.dumps(rates, indent=4)
    with open('cache/%s_rates.txt'%type, 'w', encoding='utf8') as log:
        log.write(string)

def load_rates(type):
    with open('cache/%s_rates.txt'%type, 'r', encoding='utf8') as f:
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
    buy_rates = load_rates('buy')
    sell_rates = load_rates('sell')
    gaps = load_gaps()
    # print(gaps)
    operate_prices={}
    for c in codes:
        operate_prices[c] = float(load_trade_log_once(c)[c]['price'])
    # print(operate_prices)
    buyer = Trader(user, codes[0], operate_prices[codes[0]], 100, 'b')
    seller = Trader(user, codes[0], operate_prices[codes[0]], 100, 's')
    p = get_all_price(codes)
    closes = {code:p[code]['close'] for code in codes}
    # print(closes)
    code2name(codes, operate_prices, gaps, closes, buy_rates, sell_rates)
    while True:
        time.sleep(0.5)
        p = get_all_price(codes)
        count += 1
        price_nows = {code : p[code]['now'] for code in codes}
        for i in range(len(codes)):
            try:
                code = codes[i]
                close = closes[code]
                gap = gaps[code]
                buy_rate = buy_rates[code]
                sell_rate = sell_rates[code]

                price_now = price_nows[code]
                operate_price = operate_prices[code]

                # if count % 3600 == 0:
                    # print("\r%s:【Pirce:%s, Gap:%s, Operate:%s】 " % (code, price_now, gap, operate_price))
                if price_now < operate_price - gap * buy_rate:
                    if code not in fund_codes:
                        buy_price = round(operate_price - gap, 2)
                        buy_amount = buy_amount_base # * int(abs_reduce(price_now, close) // (gap * 6) + 1)
                    else:
                        buy_amount = buy_amount_base
                        buy_price = round(operate_price - gap, 3)
                        if price_now < close * 0.99:
                            buy_amount = buy_amount_base + 100
                        elif price_now < close * 0.975:
                            buy_amount = buy_amount_base + 200
                        elif price_now < close * 0.96:
                            buy_amount = buy_amount_base + 300
                    buy_id = buyer.trade(code, buy_price, buy_amount, 'b')
                    print("[%s] Price  Now:%s, Operate_price:%s】" % (datetime.datetime.utcnow().strftime('%H:%M%S'), price_now, buy_price))
                    save_trade_log_once(code, buy_price, buy_amount)
                    operate_prices[code] = buy_price
                    time.sleep(0.2)

                if price_now > operate_price + gap * sell_rate:
                    if code not in fund_codes:
                        sell_price = round(operate_price + gap, 2)
                        sell_amount = sell_amount_base #* int(abs_reduce(price_now, close) // (gap * 10) + 1)
                    else:
                        sell_amount = sell_amount_base
                        sell_price = round(operate_price + gap, 3)
                        if price_now > close * 1.01:
                            sell_amount = sell_amount_base + 100
                        elif price_now > close * 1.025:
                            sell_amount = sell_amount_base + 200
                        elif price_now > close * 1.04:
                            sell_amount = sell_amount_base + 300
                    # if code[:3] == '513':
                    #     sell_amount = 300
                    sell_id = seller.trade(code, sell_price, sell_amount, 's')
                    save_trade_log_once(code, sell_price, sell_amount)
                    print("[%s] Price  Now:%s, Operate_price:%s】" % (datetime.datetime.utcnow().strftime('%H:%M%S'), price_now, sell_price))
                    operate_prices[code] = sell_price
                    time.sleep(0.2)
            except KeyError as e:
                print(e)
            except Exception as e:
                if str(e).find('客户股票不足'):
                    print(str(e), codes[i])
                    return code

