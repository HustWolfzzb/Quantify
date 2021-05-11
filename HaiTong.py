import easytrader
import time
from DataEngine.Data import get_qo
import json
import sys

# user = easytrader.use('htzq_client')
if sys.platform == 'linux':
    user = ''
elif sys.platform == 'darwin':
    user = ''
else:
    user = easytrader.use('ths')
    user.connect(r'E:\Program Files\东方同花顺\xiadan.exe')

# 类似 r'C:\htzqzyb2\xiadan.exe'
# user.connect(r'E:\Program Files\EastTonghuashun\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'
# user.connect(r'C:\Program Files\HaiTong\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'
#user.connect(r'D:\Program Files\海通证券委托\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'


# user.prepare(user='张照博', password='xxx', comm_password='xxx')
# user.prepare('D:\Program Files\海通证券委托\yh_client.json')  # 配置文件路径
# user.buy()

qo = get_qo()
# codes = ['515880']
# names = ['通信etf']
codes = ['512900','515650','159801','515880']
names = [ '证券基金', '消费50','芯片基金','通信etf']
change_ = [0.004, 0.004, 0.005, 0.004]
operate = [100,200,300,400,
           500,600,800,900,
           1000,1200,1400,1600,
           2000,2500,3000,4000 ]
open_sell = {}
open_buy = {}
for x in codes:
    open_sell[x] = []
    open_buy[x] = []




def get_all_price(codes = codes):
    return qo.stocks(codes)


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
        print("资金余额：%s\n-->\t可用资金：%s\n-->\t可取金额：%s\n-->\t总资产：%s\n-->\t"%(self.zi_jin_yu_e, self.ke_yong_jin_e, self.ke_qu_jin_e, self.zong_zi_chan))
        print("当前持仓股票:\n-->\t", self.stock.get_position())

class Stock():
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position

class Trade():
    def __init__(self, code, price, amount, type):
        self.code = code
        if code[0] == '5':
            self.price = round(price,3)
        else:
            self.price = round(price,2)

        self.amount = int(amount//100 * 100)
        if type in ['buy', 'sell', 'b', 's']:
            self.type = type
        else:
            print("委托类型不明",type)
        self.id = ''

    def trade(self, code, price, amount, type):
        self.code = code
        self.price = price
        self.amount = amount
        self.type = type
        type2Namee  = {
            'b':"购入股票",
            's':"卖出股票",
            'buy':"购入股票",
            'sell':"卖出股票"
        }
        if self.code !='' and self.price > 0 and self.amount and self.type in ['buy', 'sell', 'b', 's']:
            if self.type in ['buy','b']:
                try:
                    buy_record = user.buy(self.code, self.price, self.amount)
                    self.id = buy_record['message']
                    print("%s Success， Code:%s, Price：%s, Amount:%s"%(type2Namee[self.type], self.code, self.price, self.amount))
                    return self.id
                except KeyError as e:
                    print("好像没有委托成功-->拿不到合同号：",str(e))
                    print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
                except Exception as e:
                    if str(e).find('不足'):
                        print(str(e), names[self.code])
                        print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
            elif self.type in ['sell','s']:
                try:
                    sell_record = user.sell(self.code, self.price, self.amount)
                    print("%s Success， Code:%s, Price：%s, Amount:%s"%(type2Namee[self.type], self.code, self.price, self.amount))
                    self.id = sell_record['message']

                except KeyError as e:
                    print("好像没有委托成功-->拿不到合同号：",str(e))
                    print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
                except Exception as e:
                    if str(e).find('不足'):
                        print(str(e), names[self.code])
                        print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
        else:
            print("数据不符合规范:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t"%(self.code,self.price,self.amount,self.type))
        return self.id


def get_Account():
    return User(user)

def save_para_once(code, price, amount):
    string = json.dumps({code:{'price':price, 'amount':amount}})
    with open('cache/%s-log.txt'%code, 'w', encoding='utf8') as log:
        log.write(string)

def load_para_once(code):
    with open('cache/%s-log.txt'%code, 'r', encoding='utf8') as f:
        return json.load(f)

def save_gaps_once(gaps):
    string = json.dumps(gaps)
    with open('cachegaps.txt', 'w', encoding='utf8') as log:
        log.write(string)

def load_gaps():
    with open('cache/gaps.txt', 'r', encoding='utf8') as f:
        return json.load(f)


def grid_bs():
    # start = False
    count = 0
    codes = ['513550','510050','002044','000725']
    buy_amount = 100
    sell_amount = 100
    gaps = load_gaps()
    print(gaps)
    operate_prices=[]
    for c in codes:
        operate_prices.append(float(load_para_once(c)[c]['price']))
    print(operate_prices)
    buyer = Trade(codes[0], operate_prices[0], 100, 'b')
    seller = Trade(codes[0], operate_prices[0], 100, 's')
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
                if count % 120 == 0:
                    print("\r%s:【Pirce:%s, Gap:%s, Operate:%s " % (code, price_now, gap, operate_price))
                if price_now < operate_price - gap:
                    buy_price = round(operate_price - gap,3)
                    buy_amount = buy_amount
                    buy_id = buyer.trade(code, buy_price, buy_amount, 'b')
                    print("Price  Now:%s, Operate_price:%s"%(price_now, buy_price))
                    save_para_once(code, buy_price, buy_amount)
                    operate_prices[i] = buy_price
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


if __name__ == '__main__':
    grid_bs()
