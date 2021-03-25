

from DataEngine.Data import *
# from DataEngine.Mysql import *
import time
import os
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.width', 180) # 设置打印宽度(**重要**)

if __name__ == '__main__':
    # data = get_tick_price('002558', '15')
    data = get_tick_price('600104','15')
    cost = 0
    amount = 0

    use_able = amount
    money = 80000
    start = data[0][1][0]
    all_price = []
    d_gap = 0.97
    u_gap = 1.03
    op = []
    flag = True
    # for x in data:
    #     time = x[0]
    #     price = x[1]
    #     for p in price:
    #         if p <= start * d_gap or flag:
    #             if flag:
    #                 flag = False
    #             if money > pow(2, len(op)) * p:
    #                 print(time)
    #                 op.append(pow(2, len(op)) *100)
    #                 start = p
    #                 cost = (cost * amount + start * op[-1]) / (amount + op[-1])
    #                 amount += op[-1]
    #                 print('Buy:', start, round(cost, 2), amount)
    #                 money -= start * op[-1]
    #                 print(time , op, round(money,1), '\n-------')
    #         if p >= start * u_gap:
    #             if len(op) > 1:
    #                 print(time)
    #                 start = p
    #                 cost = (cost * amount - start * op[-1]) / (amount - op[-1])
    #                 money += start * op[-1]
    #                 amount -= op[-1]
    #                 op = op[:-1]
    #                 print('Sell:', start, round(cost, 2), amount)
    #                 print(time , op, round(money,1), '\n-------')
    #             elif len(op) == 1:
    #                 start = p
    #                 print("卖光了都！\n--------")
    #                 continue
    #         # print("\n===========\n")
    #         # all_price.append(p)
    # print(money +  data[-1][-1][-1] * amount)
    etf = pd.read_csv('/Users/zhangzhaobo/PycharmProjects/Quantify/DataEngine/etf.txt')
    ts.set_token('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')

    for year in ['20200716']:
        all_profit = pd.DataFrame(index=range(0, len(etf)),
                                  columns=['代码', '名称', '钱', '股份', '入价', '出价', '入金', '出金', '股价波动', '利润率'])
        for et in range(len(etf)):
            try:
                if float(etf.loc[et, '市价']) < 2.5 and float(etf.loc[et, '市价']) > 0.5:# and str(etf.loc[et,'名称']).find('南方中证全指证券公司')!=-1 :
                    code = str(etf.loc[et, '代码'])
                    if code[0] == '5':
                        code += '.SH'
                    else:
                        code += '.SZ'
                    name = etf.loc[et, '名称'].replace('行情吧档案', '')
                else:
                    continue
            except Exception as e:
                # print(e)
                continue

            if code + year + '.txt' not in os.listdir('etf/'):
                if len(year) == 4:
                    sd = year + '0130'
                    ed = str(int(year) + 1) + '0130'
                else:
                    sd = year
                    ed = str(int(year[:4]) + 1) + '0130'
                print("第%s个code:%s 需要我自己找？" % (et, code))
                time.sleep(0.6)
                try:
                    df = ts.pro_bar(ts_code=code, asset = 'FD', start_date=sd, end_date=ed)
                except Exception as e:
                    time.sleep(60)
                    df = ts.pro_bar(ts_code=code, asset='FD', start_date=sd,
                                    end_date=ed)
                if len(df) < 40:
                    df.to_csv('etf/' + code + year + '.txt')
                    print("太短了,以致于没得数据，记个名字随便应付下")
                    continue
                df.to_csv('etf/' + code + year + '.txt')
            else:
                df = pd.read_csv('etf/' + code + year + '.txt')
                if len(df) < 40:
                    continue
            # print(df.head())
            money = 40000
            amount = 40000
            today_data = df.loc[len(df)-1]
            gap = round(today_data['pre_close'] * 0.003, 3)
            # print(gap)
            open_ziben = money + amount * today_data['pre_close']
            open_price = today_data['pre_close']
            # print(
            #     '%s | 初始余额：%s, 初始股份:%s, 入场价：%s, 总资本：%s' % (name, money, round(amount), round(today_data['close'],3), round(money + amount * today_data['close'])))
            operate_num = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,1500,1600,1700,1800,1900,2000]
            col = {id : name for id,name in  zip(list(df.columns), range(len(list(df.columns))))}
            for s in range(len(df)-1,-1,-1):
                ma5 = df.iloc[s-6:s-1, col['close'] ].sum() / 5
                ma10 = df.iloc[s-11:s-1, col['close'] ].sum() / 10
                # ma50 = df.iloc[i-51:i-1, col['close'] ].sum() / 50
                today_data = df.loc[s]
                buy_times = 0
                sell_times = 0
                try:
                    if today_data['high'] >= today_data['pre_close'] + gap:
                        for i in range(1, int((today_data['high'] - today_data['pre_close']) // gap)):
                            if today_data['pre_close'] > ma10 and i > 1:
                                if amount >= (operate_num[i] + 100):
                                    money += (today_data['pre_close'] + i * gap) * (operate_num[i] + 100)
                                    amount -= (operate_num[i] + 100)
                            else:
                                if amount >= (operate_num[i] + 100):
                                    money += (today_data['pre_close'] + i * gap) * (operate_num[i])
                                    amount -= operate_num[i]
                            sell_times += 1
                    if today_data['low'] <= today_data['pre_close'] - gap:
                        for i in range(1, int((today_data['high'] - today_data['pre_close']) // gap)):
                            if today_data['pre_close'] > ma10 and i > 1:
                                if money >= (today_data['pre_close'] - i * gap) * (operate_num[i] - 100):
                                    money -= (today_data['pre_close'] - i * gap) * (operate_num[i] - 100)
                                    amount += (operate_num[i] - 100)
                            else:
                                if money >= (today_data['pre_close'] - i * gap) * (operate_num[i] - 100):
                                    money -= (today_data['pre_close'] - i * gap) * (operate_num[i])
                                    amount += operate_num[i]
                            buy_times += 1
                    if today_data['high'] >= today_data['close'] + gap:
                        for i in range(1, int((today_data['high'] - today_data['close']) // gap)):
                            if money >= (today_data['high'] - i * gap) * (operate_num[i]):
                                money -= (today_data['high'] - i * gap) * (operate_num[i])
                                amount += (operate_num[i])
                                buy_times += 1
                    if today_data['low'] <= today_data['close'] - gap:
                        for i in range(1, int((today_data['close'] - today_data['low']) // gap)):
                            if amount > (operate_num[i]):
                                money += (today_data['low'] + i * gap) * (operate_num[i])
                                amount -= (operate_num[i])
                                sell_times += 1
                except IndexError as e:
                    # print("今日份涨跌幅:%s 过大，直接木了"%today_data['pct_chg'])
                    pass
                # print('「%s」 %s||买：%s,卖：%s, (%s)【%s->[%s, %s]->%s】 余额：%s, 股份:%s, 总金额：%s'%(len(df)-1-s, today_data['trade_date'], buy_times, sell_times,round(today_data['pre_close'],3), round(today_data['open'],3), round(today_data['low'], 3), round(today_data['high'], 3), round(today_data['close'], 3), round(money), round(amount), round(money + amount * today_data['close'])))
            start_data = df.loc[len(df) - 1]
            today_data = df.loc[0]
            all_profit.loc[et] = [code, name, round(money), round(amount), round(open_price, 3), round(today_data['close'], 3), round(open_ziben, 3) , round(money + amount * today_data['close']) , round(today_data['close']/open_price - 1 , 3), round((money + amount * today_data['close']) / open_ziben - 1, 3)]
            # if round((money + amount * today_data['close'])/open_ziben - 1,2) < 0.1:
            #     continue
        print(all_profit[all_profit['利润率'] >= 0.1])
        print(all_profit[all_profit['钱']>0])
        print("len of all profit:%s"%len(all_profit[all_profit['钱']>0]))
            # print(
            #     '%s|%s__|__结余余额：%s, 结余股份:%s, 价：%s/%s(%s), 钱：%s/%s, (利润率:%s)' % (code, name,
            #     round(money), round(amount), round(open_price,3), round(today_data['close'],3), round(today_data['close']/open_price - 1 ,3), round(open_ziben, 3) ,round(money + amount * today_data['close']) , round((money + amount * today_data['close'])/open_ziben - 1,3)))



