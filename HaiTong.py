import easytrader
from DataEngine.Data import get_qo
import json
import sys
from Strategy.gridTrade import grid_bs

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

if __name__ == '__main__':
    grid_bs(['513550','510050','002044','000725','600031'])
