from DataEngine.Data import  *
from Feature.feature import Average
def avg(x):
    amount = 0
    for s in x:
        amount += s
    return amount/len(x)

def MovingAverage(code='600900.SH',sdate='20120101',edate='20210323'):
    data = get_pro_daily(code,sdate,edate)
    data = data[::-1].reset_index()
    length = len(data['close'])
    change = 0
    flag = True
    money = 100000
    stock = 100
    gap = round(data['close'][0] * 0.02, 2)
    print("Start Position:%s, money:%s, stock:%s, Price:%s"%(money + stock * data['close'][10], money, stock,data['close'][10]))
    pos = [money + stock * data['close'][10]]
    sell_price = 0
    buy_price = 0
    for x in range(10,length):
        MA5 = Average(data,'close',x, 5)
        MA10 = Average(data,'close',x, 10)
        if flag and change == 0:
            change = round( (MA5 - MA10), 2)
            flag = False
        else:
            pos.append(money + stock * data['close'][x])
            nowChange = round((MA5 - MA10),2)
            if nowChange >= gap and change < nowChange and stock > 0:
                if buy_price != 0 and buy_price > data['close'][x]:
                    continue
                money = round(money + stock * data['close'][x], 2)
                sell_price = data['close'][x]
                stock = 0
                print("Sell Price:%s, Pre：%s, Now:%s,money:%s, stock:%s" % (
                data['close'][x], change, nowChange, money, stock))
            elif change > nowChange and nowChange <= -gap and money > data['close'][x] * 100:
                if sell_price != 0 and data['close'][x] > sell_price:
                    continue
                stock += money // (data['close'][x] * 100) * 100
                buy_price  = data['close'][x]
                money = round(money - money // (data['close'][x] * 100) * data['close'][x] * 100, 2)
                print("Buy Price:%s, Pre：%s, Now:%s, money:%s, stock:%s" % (
                data['close'][x], change, nowChange, money, stock))

            change = nowChange
    print("股价回撤率：%s, 资金回撤率：%s, 股价涨幅：%s, 资金涨幅：%s" % (
        round(1 - min(data['close']) / data['close'][10], 2),
        round(1 - min(pos) / pos[0], 2),
        round(data['close'][-1] / data['close'][10] - 1, 2),
        round(pos[-1] / pos[0] - 1, 2)))
    print("End Position:%s, money:%s, stock:%s, Price:%s" % (
    money + stock * data['close'][-1], money, stock, data['close'][-1]))


if __name__ == '__main__':
    for i in ['600900.SH','000157.SZ','000725.SZ','002064.SZ','600048.SH']:
        print(i)
        MovingAverage(i)