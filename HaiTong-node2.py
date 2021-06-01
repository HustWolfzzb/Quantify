import datetime

import easytrader
import json
import sys
from Strategy.gridTrade import grid_bs, time


if sys.platform == 'linux':
    user = ''
elif sys.platform == 'darwin':
    user = ''
else:
    user = easytrader.use('htzq_client')
    user.connect(r'C:\Program Files\海通证券委托\xiadan.exe')


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



def get_Account():
    return User(user)


if __name__ == '__main__':
    # codes = ['510050', '588000', '601666', '600900', '002044', '000725', '600031']
    codes = ['510050', '601666', '600900', '002044', '000725', '600031', '601607', '603126']
    print(user.position)

    timeReady = False
    while len(codes) > 0:
        s = grid_bs(codes, user)
        codes.remove(s)

    # grid_bs(['513550','510050','002044','000725','600031'], user)