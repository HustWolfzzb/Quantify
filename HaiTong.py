import easytrader
import time
import tushare as ts
import datetime
from DataEngine.Data import get_qo

user = easytrader.use('htzq_client')
user.connect(r'D:\Program Files\海通证券委托\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'
# user.prepare(user='张照博', password='379926', comm_password='379926')
# user.prepare('D:\Program Files\海通证券委托\yh_client.json')  # 配置文件路径
# user.buy()
qo = get_qo()
codes = ['512900','515650','159801','515880']
names = [ '证券基金', '消费50','芯片基金','通信etf']
change_ = [0.004, 0.004, 0.005, 0.004]

class User():
    def __init__(self, user):
        self.user = user
        print(user.balance)
        self.zi_jin_yu_e = user.balance['资金余额']
        self.ke_yong_jin_e = user.balance['可用金额']
        self.ke_qu_jin_e = user.balance['可取金额']
        self.zong_zi_chan = user.balance['总资产']
        self.stock = Stock(user.position)

    def buy(self, code, price, amount):
        self.user.buy(code, price, amount)

    def sell(self, code, price, amount):
        self.user.sell(code, price, amount)

    def get_balance(self):
        return self.ke_yong_jin_e

    def user_refresh(self):
        self.user.refresh()

    def get_today_trades(self):
        return self.user.today_trades

    def get_today_entrusts(self):
        return self.user.today_entrusts

    def show(self):
        print("资金余额：%s\n可用资金：%s\n可取金额：%s\n总资产：%s\n"%(self.zi_jin_yu_e, self.ke_yong_jin_e, self.ke_qu_jin_e, self.zong_zi_chan))
        print("当前持仓股票:\n", self.stock.get_position())

class Stock():
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position

class ETF():
    def __init__(self, price):
        self

def get_Account():
    return User(user)

def get_all_price(codes = codes):
    return qo.stocks(codes)


open_sell = {}
open_buy = {}
for x in codes:
    open_sell[x] = []
    open_buy[x] = []
price_close = get_all_price()
price_close = [price_close[x]['close'] for x in codes]
operate = [100,200,300,400,500,600,800,900,1000,1200,1400,1600,2000,2500,3000]

def open_grid_buy():

    pos = user.position
    keyong_money = user.balance['可用金额']
    keyong_amount = []
    for code in codes:
        for p in pos:
            if p['证券代码'] == code:
                keyong_amount.append(p['可用余额'])
    print(keyong_amount)
    # price_close = [1.431, 1.196, 1.814, 1.312]
    # keyong_money = 20000
    # keyong_amount = [8100, 3600, 5500, 200]
#     #开盘的时候挂卖盘
    for code_idx in range(len(codes)):
        price =  price_close[code_idx]
        ka = keyong_amount[code_idx]
        for i in range(4):
            try:

                for j in range(i+1):
                    if ka>pow(2,i) * 100:
                        price += change_[code_idx]
                        price = round(price, 3)
                        open_sell[codes[code_idx]].append(user.sell(codes[code_idx], price , pow(2,i) * 100))
                        print("Sell %s, %s, %s, %s"%(names[code_idx], price, pow(2,i) * 100 , round(price/price_close[code_idx],3) ))
                        ka -= pow(2,i) * 100
                    elif ka>100:
                        price += change_[code_idx]
                        price = round(price, 3)
                        # open_sell[codes[code_idx]].append(user.sell(codes[code_idx], price , ka-100))
                        print("Sell %s, %s, %s, %s"%(names[code_idx], price, ka-100 , round(price/price_close[code_idx],3) ))
                        ka = 100
            except Excepption as e:
                if str(e).find("客户股票不足"):
                    print("客户%s股票不足"%names[code_idx])
#     # 开盘的时候挂买盘
    km = keyong_money
    for code_idx in range(len(codes)):
        price = price_close[code_idx]
        for i in range(3):
            for j in range(i + 1):
                if km > (price-0.004) * pow(2, i) * 100:
                    price -= change_[code_idx]
                    price = round(price, 3)
                    #  open_buy.append(user.sell(codes[code_idx], price , pow(2,i) * 100))
                    print("Buy %s, %s, %s, %s" % (
                    names[code_idx], price, pow(2, i) * 100, round(price / price_close[code_idx], 3)))
                    km -= pow(2, i) * 100 * price
                elif km > 100 * (price-0.004):
                    amount = int(km / ((price - 0.004)*100))
                    price -= change_[code_idx]
                    price = round(price, 3)
                    # open_buy.append(user.sell(codes[code_idx], price , ka-100))
                    print("Buy %s, %s, %s, %s" % (names[code_idx], price, amount, round(price / price_close[code_idx], 3)))
                    km -= amount * price


# buy_price = [0]*len(codes)
# sell_price = [0]*len(codes)
# buy_amount = [0]*len(codes)
# sell_amount = [0]*len(codes)


def get_amount(now, close, gap):
    if now > close:
        return operate[int((now - close)//gap)]
    else:
        return  operate[int((close - now)//gap)]

#网格交易法
def spy_price():
    start = True
    # start = False
    p = get_all_price()
    price_close = [p[x]['now'] for x in codes]
    operate_price = [x for x in price_close]
    print(price_close)
    # buy_amount = [[] for x in range(len(codes))]
    # sell_amount =[[] for x in range(len(codes))]
    # price = [1.431, 1.429, 1.427, 1.425, 1.423, 1.421, 1.419, 1.417, 1.415, 1.413, 1.411, 1.409, 1.407,
    #           1.405, 1.408, 1.411, 1.414, 1.417, 1.42, 1.423, 1.426, 1.429, 1.432,
    #           1.435, 1.433, 1.431, 1.429, 1.427, 1.425, 1.423, 1.421, 1.419, 1.417,
    #           1.415, 1.417, 1.419, 1.421,
    #           1.421, 1.416, 1.411, 1.406, 1.401, 1.396,
    #           1.397, 1.398, 1.399, 1.4, 1.401, 1.402, 1.403, 1.404, 1.405, 1.406, 1.407, 1.408, 1.409]
    # cou = 0
    # price_close = [1.431, 1.196, 1.814, 1.312]

    # use = 5500
    # money = operate_price[code_idx * use
    sell_ids = ['' for x in range(len(codes))]
    buy_ids = ['' for x in range(len(codes))]
    buy_amount = 100
    sell_amount = 100
    while True:
        time.sleep(1)
        # if cou>=len(price):
        #     break
        p = get_all_price()
        price_now = [p[x]['now'] for x in codes]
        # price_now = [price[cou],]
        # cou += 1
        # op_amount = 0
        for code_idx in range(len(codes)):
        # for code_idx in range(len(codes[0:1])):
            close_price = price_close[code_idx]
            code = codes[code_idx]
            now_price = price_now[code_idx]
            gap = change_[code_idx]
            try:
                if start:
                    start = False
                    # print("挂 Sell %s, %s, %s, %s" % (names[code_idx], close_price + gap, amount , round(now_price / price_close[code_idx], 3)))
                    sell_ids[code_idx] = user.sell(code,  round(now_price + gap, 3), sell_amount)
                    # print("挂 Buy %s, %s, %s, %s" % (names[code_idx], close_price - gap, amount , round(now_price / price_close[code_idx], 3)))
                    buy_ids[code_idx] = user.buy(code, round(now_price - gap, 3), buy_amount)['entrust_no']
                    # op_amount = 100

                if now_price >= operate_price[code_idx] + gap:
                    # use -= op_amount
                    print("%s 价格：%s,的卖单 成交！"%(names[code_idx],operate_price[code_idx] + gap))

                    buy_amount = get_amount(now_price, close_price, gap)
                    sell_amount = get_amount(now_price + gap, close_price, gap)
                    # op_amount = amount
                    operate_price[code_idx] = now_price
                    sell_ids[code_idx] = user.sell(codes[code_idx],  round(now_price + gap, 3), sell_amount)['entrust_no']
                    print("挂 Sell %s, %s, %s, %s" %(names[code_idx], round(now_price + gap, 3), buy_amount, round(now_price / price_close[code_idx], 3)))
                    if buy_ids[code_idx] != '':
                        print("撤买单%s" % sell_ids[code_idx])
                        user.cancel_entrust(buy_ids[code_idx])
                    buy_ids[code_idx] = user.buy(codes[code_idx],  round(now_price - gap, 3), buy_amount)['entrust_no']
                    print("挂 Buy %s, %s, %s, %s" % (names[code_idx], round(now_price - gap, 3), buy_amount, round(now_price / price_close[code_idx], 3)))


                elif now_price <= operate_price[code_idx] - gap:
                    # use += op_amount
                    print("%s 价格：%s,的买单 成交！"%(names[code_idx],operate_price[code_idx] - gap))
                    buy_amount = get_amount(now_price - gap, close_price, gap)
                    sell_amount = get_amount(now_price, close_price, gap)
                    # op_amount = amount
                    operate_price[code_idx] = now_price
                    buy_ids[code_idx] = user.buy(codes[code_idx],  round(now_price - gap, 3), buy_amount)['entrust_no']
                    print("挂 Buy %s, %s, %s, %s" % (names[code_idx], round(now_price - gap, 3), buy_amount, round(now_price / price_close[code_idx], 3)))
                    if sell_ids[code_idx] != '':
                        print("撤%s卖单%s"%sell_ids[code_idx])
                        user.cancel_entrust(sell_ids[code_idx])
                    sell_ids[code_idx] = user.sell(codes[code_idx],  round(now_price + gap, 3), sell_amount)['entrust_no']
                    print("挂 Sell %s, %s, %s, %s" %(names[code_idx], round(now_price + gap, 3), buy_amount, round(now_price / price_close[code_idx], 3)))
            except KeyError as e:
                print(e)
            except Exception as e:
                if str(e).find('客户股票不足'):
                    print('客户%s股票不足'%names[code_idx])


if __name__ == '__main__':
    # spy_price()
    # print(len(user.today_trades))
    # open_grid_buy()
    print(user.today_trades)
    # [{'成交时间': '', '证券代码': '', '证券名称': '', '操作': '', '成交数量': 0, '成交均价': 0.0, '成交金额': 0.0, '合同编号': '0', '成交编号': '',
    #   'Unnamed: 9': ''}]
