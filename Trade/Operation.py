from random import randint
import tushare as ts
from Strategy.ThreeMomentum import threeMonmentum
from datetime import datetime, time, date
from time import sleep
import easyquotation
from DataEngine.Data import get_pro_daily, get_pro_stock_basic


class Trader():
    def __init__(self, user, code, price, amount, type):
        self.user = user
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
        self.id = '100'

    def trade(self, code, price, amount, type, names={}):
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
                    buy_record = self.user.buy(self.code, self.price, self.amount)
                    # self.id = buy_record['message']
                    print("%s Success， Code:%s, Price：%s, Amount:%s"%(type2Namee[self.type], self.code, self.price, self.amount))
                    return 0
                    # return self.id
                except KeyError as e:
                    print("好像没有委托成功-->拿不到合同号：",str(e))
                    print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
                except Exception as e:
                    if str(e).find('不足'):
                        print(str(e), names[self.code])
                        print("错误日志:\n-->\t代码：%s\n-->\t价格:%s\n-->\t委托数量：%s\n-->\t买卖类型：%s\n-->\t" % (self.code, self.price, self.amount, self.type))
            elif self.type in ['sell','s']:
                try:
                    sell_record = self.user.sell(self.code, self.price, self.amount)
                    print("%s Success， Code:%s, Price：%s, Amount:%s"%(type2Namee[self.type], self.code, self.price, self.amount))
                    # self.id = sell_record['message']

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


# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
MORNING_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

if __name__ == '__main__':
    stocks = get_pro_stock_basic()
    codes = [x for x in stocks['ts_code'] if x[0] != 3 and x[:2]!='68']
    names = [x for x in stocks['name']]
    for x in range(len(codes)):
        if names[x].find('ST') != -1:
            continue
        print("\n\n模拟%s 三重指标"%names[x])
        sleep(1)
        threeMonmentum(codes[x], '20160101', '20210310')


