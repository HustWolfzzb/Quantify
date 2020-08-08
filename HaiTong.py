import easytrader
import time
import tushare as ts
import datetime
user = easytrader.use('htzq_client')
user.connect(r'D:\Program Files\海通证券委托\xiadan.exe') # 类似 r'C:\htzqzyb2\xiadan.exe'
# user.prepare(user='张照博', password='379926', comm_password='379926')
# user.prepare('D:\Program Files\海通证券委托\yh_client.json')  # 配置文件路径

codes = ['600723','002205','002131','002621','002457','600918']

start = time.clock()
# for x in range(10):
#     ti = time.strftime(" %H:%M:%S", time.localtime())
#     names = []
#     price = []
#     for xx in codes:
#         data = ts.get_realtime_quotes(xx)
#         names.append(data.at[0, 'name'])
#         price.append(data.at[0, 'price'])
#     time.sleep(5)
#     print('\n' + ti )
#     print(" | ".join(names))
#     print(" | ".join(price))

# print(time.strftime(" %H:%M:%S", time.localtime()) ,'  ', user.position[0]['市价'])




class User():
    def __init__(self, user):
        self.user = user
        self.zi_jin_yu_e = user.balance['资金余额']
        self.ke_yong_jin_e = user.balance['可用金额']
        self.ke_qu_jin_e = user.balance['可取金额']
        self.zong_zi_chan = user.balance['总资产']
        self.stock = Stock(user.position)

    def buy(self, code, price, amount):
        data = ts.get_realtime_quotes(code)
        price_now = data.at[0, 'price']
        if price < price_now and price/price_now > 0.995:
            price = price_now
        elif price > price_now :
            price = price_now
        print(self.user.buy(code, price, amount))



    def sell(self, code, price, amount):
        data = ts.get_realtime_quotes(code)
        price_now = data.at[0, 'price']
        if price < price_now and price / price_now > 0.995:
            price = price_now
        elif price > price_now:
            price = price_now
        for ss in self.stock.get_position():
            if ss['证券代码'] == code:
                if ss['可用余额'] < amount:
                    amount = ss['可用余额']
        self.user.buy(code, price, amount)

    def show(self):
        print("资金余额：%s\n可用资金：%s\n可取金额：%s\n总资产：%s"%(self.zi_jin_yu_e, self.ke_yong_jin_e, self.ke_qu_jin_e, self.zong_zi_chan))
        print("当前持仓股票:\n", self.stock)


class Stock():
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position
if __name__ == '__main__':
    myAccount = User(user)
    myAccount.show()
	# main()
	# os.system('python3 Mysql.py')
	# os.system('python3 Neo4j.py')
	# os.system('python3 Strategy.py')
	# os.system('python3 Operation.py')
	# os.system('python3 Data.py')