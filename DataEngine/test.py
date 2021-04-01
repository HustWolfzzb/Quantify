from DataEngine.Data import *
import pandas as pd
from Feature.feature import Average
import time
import os
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180) # 设置打印宽度(**重要**)

if __name__ == '__main__':
    data = get_pro_daily('600900.SH','2020326','20210326')
    data=data[::-1].reset_index()
    amount = 1000
    use_able = amount
    money = 80000
    start = data['open'][0]
    init = data['open'][0]
    all_price = []
    d_gap = 0.1
    u_gap = 0.2
    buy_record = [(init,100)]
    sell_record = [(init,100)]
    flag = True
    print("初始资金%s"%(money + data['open'][0] * amount))
    sell_price = 0
    for x in range(len(data)):
        time = data['trade_date'][x]
        open = data['open'][x]
        close = data['close'][x]
        high = data['high'][x]
        low = data['low'][x]
        sell_out = False
        if high >= buy_record[-1][0] + u_gap:
            base = buy_record[-1][0]
            sell_times = int((high - buy_record[-1][0]) // u_gap)
            for i in range(sell_times):
                idx = -1 - i
                if idx <= -len(buy_record):
                    idx = 0
                if amount > buy_record[idx][1]:
                    sell_amount = buy_record[idx][1]
                    if idx == 0 and sell_price != 0:
                        sell_price += u_gap
                    else:
                        sell_price = buy_record[idx][0] + u_gap
                    money += sell_price * sell_amount
                    amount -= buy_record[idx][1]
                    print('Sell:%s-->%s, %s, %s' % ( round(sell_price,2), buy_record[idx][0], sell_amount, amount))
                else:
                    print("卖光了：%s,%s,%s"%( money + data['close'][x] * amount,round(sell_price, 2),amount) )
            if len(buy_record) > sell_times:
                buy_record = buy_record[:len(buy_record)-sell_times]
            else:
                buy_record = buy_record[0:1]

        if low < buy_record[-1][0] - d_gap:
            for i in range(int((buy_record[-1][0] - low)//d_gap)):

                buy_price = round(buy_record[-1][0] -  d_gap,2)
                buy_amount = \
                    ((init - buy_price) // (d_gap * 3) + 1) * 100
                if money - buy_price * buy_amount > 0:
                    buy_record.append((buy_price, buy_amount))
                    money -= buy_price * buy_amount
                    amount += buy_amount
                    print('Buy: %s, %s, %s'%(buy_price, buy_amount, amount) )
                else:
                    print("没钱买了：%s,%s,%s"%(money,buy_record[-1][0] - (i + 1) * d_gap, amount) )
        # print("\n===========\n")
        # all_price.append(p)
        print("Date:%s, Position:%s = Price:%s X Amount:%s + Money:%s\n"%(time, money + data['close'][x] * amount, data['close'][x] ,amount, money ))



    # etf = pd.read_csv('/Users/zhangzhaobo/PycharmProjects/Quantify/DataEngine/etf.txt')
    # ts.set_token('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    #
    # for year in ['2020']:
    #     all_profit = pd.DataFrame(index=range(0, len(etf)),
    #                               columns=['代码', '名称', '钱', '股份', '入价', '出价', '入金', '出金', '股价波动', '利润率'])
    #     for et in range(len(etf)):
    #         try:
    #             if float(etf.loc[et, '市价']) < 2.5 and float(etf.loc[et, '市价']) > 0.5:# and str(etf.loc[et,'名称']).find('券')!=-1 :
    #                 code = str(etf.loc[et, '代码'])
    #                 if code[0] == '5':
    #                     code += '.SH'
    #                 else:
    #                     code += '.SZ'
    #                 name = etf.loc[et, '名称'].replace('行情吧档案', '')
    #             else:
    #                 continue
    #         except Exception as e:
    #             # print(e)
    #             continue
    #
    #         if code + year + '.txt' not in os.listdir('etf/'):
    #             if len(year) == 4:
    #                 sd = year + '0130'
    #                 ed = str(int(year) + 1) + '0130'
    #             else:
    #                 sd = year
    #                 ed = str(int(year[:4]) + 1) + '0130'
    #             print("第%s个code:%s 需要我自己找？" % (et, code))
    #             time.sleep(0.6)
    #             try:
    #                 df = ts.pro_bar(ts_code=code, asset = 'FD', start_date=sd, end_date=ed)
    #             except Exception as e:
    #                 time.sleep(60)
    #                 df = ts.pro_bar(ts_code=code, asset='FD', start_date=sd,
    #                                 end_date=ed)
    #             if len(df) < 40:
    #                 df.to_csv('etf/' + code + year + '.txt')
    #                 print("太短了,以致于没得数据，记个名字随便应付下")
    #                 continue
    #             df.to_csv('etf/' + code + year + '.txt')
    #         else:
    #             df = pd.read_csv('etf/' + code + year + '.txt')
    #             if len(df) < 40:
    #                 continue
    #         # print(df.head())
    #         money = 40000
    #         amount = 40000
    #         today_data = df.loc[len(df)-1]
    #         gap = round(today_data['pre_close'] * 1003, 3)
    #         # print(gap)
    #         open_ziben = money + amount * today_data['pre_close']
    #         open_price = today_data['pre_close']
    #         # print(
    #         #     '%s | 初始余额：%s, 初始股份:%s, 入场价：%s, 总资本：%s' % (name, money, round(amount), round(today_data['close'],3), round(money + amount * today_data['close'])))
    #         operate_num = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,1500,1600,1700,1800,1900,2000]
    #         col = {id : name for id,name in  zip(list(df.columns), range(len(list(df.columns))))}
    #         for s in range(len(df)-1,-1,-1):
    #             ma5 = df.iloc[s-6:s-1, col['close'] ].sum() / 5
    #             ma10 = df.iloc[s-11:s-1, col['close'] ].sum() / 10
    #             # ma50 = df.iloc[i-51:i-1, col['close'] ].sum() / 50
    #             today_data = df.loc[s]
    #             buy_times = 0
    #             sell_times = 0
    #             try:
    #                 if today_data['high'] >= today_data['pre_close'] + gap:
    #                     for i in range(1, int((today_data['high'] - today_data['pre_close']) // gap)):
    #                         if today_data['pre_close'] > ma10 and i > 1:
    #                             if amount >= (operate_num[i] + 200):
    #                                 money += (today_data['pre_close'] + i * gap) * (operate_num[i] + 200)
    #                                 amount -= (operate_num[i] + 200)
    #                         else:
    #                             if amount >= (operate_num[i]):
    #                                 money += (today_data['pre_close'] + i * gap) * (operate_num[i])
    #                                 amount -= operate_num[i]
    #                         sell_times += 1
    #                 if today_data['low'] <= today_data['pre_close'] - gap:
    #                     for i in range(1, int((today_data['pre_close'] - today_data['low']) // gap)):
    #                         if today_data['pre_close'] < ma10 and i > 1:
    #                             if money >= (today_data['pre_close'] - i * gap) * (operate_num[i] + 200):
    #                                 money -= (today_data['pre_close'] - i * gap) * (operate_num[i] + 200)
    #                                 amount += (operate_num[i] + 200)
    #                         else:
    #                             if money >= (today_data['pre_close'] - i * gap) * (operate_num[i]):
    #                                 money -= (today_data['pre_close'] - i * gap) * (operate_num[i])
    #                                 amount += operate_num[i]
    #                         buy_times += 1
    #                 # if today_data['high'] >= today_data['close'] + gap:
    #                 #     for i in range(1, int((today_data['high'] - today_data['close']) // gap)):
    #                 #         if money >= (today_data['high'] - i * gap) * (operate_num[i]):
    #                 #             money -= (today_data['high'] - i * gap) * (operate_num[i])
    #                 #             amount += (operate_num[i])
    #                 #             buy_times += 1
    #                 # if today_data['low'] <= today_data['close'] - gap:
    #                 #     for i in range(1, int((today_data['close'] - today_data['low']) // gap)):
    #                 #         if amount > (operate_num[i]):
    #                 #             money += (today_data['low'] + i * gap) * (operate_num[i])
    #                 #             amount -= (operate_num[i])
    #                 #             sell_times += 1
    #             except IndexError as e:
    #                 # print("今日份涨跌幅:%s 过大，直接木了"%today_data['pct_chg'])
    #                 pass
    #             # print('「%s」 %s||买：%s,卖：%s, (%s)【%s->[%s, %s]->%s】 余额：%s, 股份:%s, 总金额：%s'%(len(df)-1-s, today_data['trade_date'], buy_times, sell_times,round(today_data['pre_close'],3), round(today_data['open'],3), round(today_data['low'], 3), round(today_data['high'], 3), round(today_data['close'], 3), round(money), round(amount), round(money + amount * today_data['close'])))
    #         start_data = df.loc[len(df) - 1]
    #         today_data = df.loc[0]
    #         all_profit.loc[et] = [code, name, round(money), round(amount), round(open_price, 3), round(today_data['close'], 3), round(open_ziben, 3) , round(money + amount * today_data['close']) , round(today_data['close']/open_price - 1 , 3), round((money + amount * today_data['close']) / open_ziben - 1, 3)]
    #         # if round((money + amount * today_data['close'])/open_ziben - 1,2) < 0.1:
    #         #     continue
    #     # print(all_profit)
    #     print(all_profit[all_profit['钱']>0])
    #     print("len of all profit:%s"%len(all_profit[all_profit['钱']>0]))
    #         # print(
    #         #     '%s|%s__|__结余余额：%s, 结余股份:%s, 价：%s/%s(%s), 钱：%s/%s, (利润率:%s)' % (code, name,
    #         #     round(money), round(amount), round(open_price,3), round(today_data['close'],3), round(today_data['close']/open_price - 1 ,3), round(open_ziben, 3) ,round(money + amount * today_data['close']) , round((money + amount * today_data['close'])/open_ziben - 1,3)))

