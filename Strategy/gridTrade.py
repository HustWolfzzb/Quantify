import json
from DataEngine.Data import get_qo
from Trade.Operation import Trader
import time
from Config.Config import get_BASE_DIR
BASE_DIR = get_BASE_DIR()

def save_para_once(code, price, amount):
    string = json.dumps({code:{'price':price, 'amount':amount}})
    with open(BASE_DIR+'/cache/%s-log.txt'%code, 'w', encoding='utf8') as log:
        log.write(string)

def load_para_once(code):
    with open(BASE_DIR+'/cache/%s-log.txt'%code, 'r', encoding='utf8') as f:
        return json.load(f)

def save_gaps_once(gaps):
    string = json.dumps(gaps)
    with open(BASE_DIR+'/cache/gaps.txt', 'w', encoding='utf8') as log:
        log.write(string)

def load_gaps():
    with open(BASE_DIR+'/cache/gaps.txt', 'r', encoding='utf8') as f:
        return json.load(f)


qo = get_qo()
# codes = ['515880']
# names = ['通信etf']

def get_all_price(codes=['512900','515650','159801','515880']):
    return qo.stocks(codes)


def grid_bs(codes, user ):
    # start = False
    count = 0
    buy_amount = 100
    sell_amount = 100
    gaps = load_gaps()
    print(gaps)
    operate_prices=[]
    for c in codes:
        operate_prices.append(float(load_para_once(c)[c]['price']))
    print(operate_prices)
    buyer = Trader(user, codes[0], operate_prices[0], 100, 'b')
    seller = Trader(user, codes[0], operate_prices[0], 100, 's')
    while True:
        time.sleep(0.5)
        p = get_all_price(codes)
        count += 1
        price_nows = [p[code]['now'] for code in codes]
        for i in range(len(codes)):
            try:
                code = codes[i]
                gap = gaps[code]

                price_now = price_nows[i]
                operate_price = operate_prices[i]
                if count % 3600 == 0:
                    print("\r%s:【Pirce:%s, Gap:%s, Operate:%s】 " % (code, price_now, gap, operate_price))
                if price_now < operate_price - gap:
                    buy_price = round(operate_price - gap,3)
                    buy_amount = buy_amount
                    buy_id = buyer.trade(code, buy_price, buy_amount, 'b')
                    print("Price  Now:%s, Operate_price:%s】"%(price_now, buy_price))
                    save_para_once(code, buy_price, buy_amount)
                    operate_prices[i] = buy_price
                # if codes[0:3] == '513':
                #     gap = gap * 2
                if price_now > operate_price + gap:
                    sell_price = round(operate_price + gap, 3)
                    sell_amount = sell_amount
                    sell_id = seller.trade(code, sell_price, sell_amount, 's')
                    save_para_once(code, sell_price, sell_amount)
                    print("Price  Now:%s, Operate_price:%s"%(price_now, sell_price))
                    operate_prices[i] = sell_price
            except KeyError as e:
                print(e)
            except Exception as e:
                if str(e).find('客户股票不足'):
                    print('客户%s股票不足'%codes[i])

