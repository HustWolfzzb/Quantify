from DataEngine.Data import *


def KLine(code='600900.SH',sdate='20170101',edate='20210323'):
    data = get_pro_daily(code,sdate,edate)
    data=data[::-1].reset_index()
    length = len(data)
    for x in range(30, length):
        MA5 = round(sum(data['close'][x-5:x ]) / 5, 2)
        MA10 = round(sum(data['close'][x-10:x ]) / 10, 2)
        MA30 = round(sum(data['close'][x-30:x ]) / 30, 2)
        status = 'N'
        if MA5 < MA10 * 0.985 and MA10 < MA30 * 0.985:
            status = 'DOWN'
        if MA5 > MA10 * 1.015 and MA10 > MA30 * 1.015:
            status = 'UP'
        Swallow(status, data, x)

def Swallow(status, data, x):
    future_price = list(data['close'][x:x+20])
    if status == 'DOWN' and (data.at[x, 'open'] <= data.at[x - 1, 'close']
                             and data.at[x, 'close'] >= data.at[x - 1, 'open'] and data.at[x - 1, 'close'] < data.at[
                                 x - 1, 'open']):
        # print(list(data.iloc[x,:]))
        print("%s吞没买入点到了！"%data.at[x,'trade_date'])
        print(future_price)

        for i in future_price:
            if i > data.at[x, 'close'] * 1.04:
                print('预测成功\t')
                break


    if status == 'UP' and (data.at[x, 'open'] >= data.at[x - 1, 'close']
                           and data.at[x, 'close'] <= data.at[x - 1, 'open'] and data.at[x - 1, 'close'] > data.at[
                               x - 1, 'open']):
        # print(list(data.iloc[x,:]))
        print("%s吞没卖出点到了！"%data.at[x,'trade_date'])
        print(future_price)
        for i in future_price:
            if i < data.at[x, 'close'] * 0.96:
                print('预测成功\t')
                break

if __name__ == '__main__':
    for i in ['600900.SH', '000157.SZ', '000725.SZ', '002064.SZ', '600048.SH']:
        print(i)
        KLine(i)