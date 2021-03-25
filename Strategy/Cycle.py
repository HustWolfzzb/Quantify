from DataEngine.Data import get_pro_stock_basic, get_pro_daily, get_pro_monthly
import prettytable as pt
from time import sleep

def CycleObservation(code='600900.SH',sdate='20100101',edate='20210101',name='万科A'):
    data = get_pro_daily(code, sdate, edate)
    date = list(data['trade_date'])
    date.reverse()
    close_price = list((data['close'] - data['open'])/data['open'])
    close_price.reverse()
    length = len(close_price)
    year_mon = date[0][:6]
    mon = date[0][4:6]
    price = close_price[0]
    month_change = {}
    table = pt.PrettyTable(['name', 'Month', 'Change'])
    for x in range(length):
        if  date[x][:6] != year_mon :
            year_mon = date[x][:6]
            mon = date[x][4:6]
            table.add_row([name, year_mon, round(close_price[x-1] - price,2)])
            price = close_price[x]
            if not month_change.get(mon):
                month_change[mon] = [round(close_price[x-1] - price,2)]
            else:
                month_change[mon].append(round(close_price[x-1] - price,2))
    # print(table)
    ret_m_c = {}
    for x in month_change.keys():
        # print(x,' ---> ', month_change[x], '==>', round(sum(month_change[x])/ len(month_change[x]),4))
        ret_m_c[x] = round(sum(month_change[x])/ len(month_change[x]),4)
    return ret_m_c

if __name__ == '__main__':
    stocks = get_pro_stock_basic()
    codes = [x for x in stocks['ts_code'] if x[0] != 3 and x[:2] != '68']
    names = [x for x in stocks['name']]
    rate = {}
    for x in range(len(codes)):
        if names[x].find('ST') != -1 or x % 100 == 0:
            continue
        # print("\n\n模拟%s 周期观察" % names[x])
        sleep(0.1)
        d = CycleObservation(codes[x], '20150101', '20210110', names[x])
        for x in d.keys():
            if not rate.get(x):
                rate[x] = [d[x]]
            else:
                rate[x].append(d[x])
    for x in rate.keys():
        print(x, '-->', sum(rate[x]))
