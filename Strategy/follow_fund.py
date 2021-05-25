import os

from DataEngine.Data import get_fund_basic, get_fund_daily, get_fund_name
import time
import datetime
import pandas as pd

def get_all_alive_fund(timegap):
    # 先获得时间数组格式的日期
    monthAgo = (datetime.datetime.now() - datetime.timedelta(days=timegap))
    # 转换为其他字符串格式
    monthago = monthAgo.strftime("%Y%m%d")
    df = get_fund_basic()
    x = df[df['status'] == 'L']
    x = x[x['list_date'] < monthago]
    all_fund = x['ts_code'].tolist()
    return all_fund

def get_Date_base_gap(timebase, timegap):
    today = datetime.datetime.now() - datetime.timedelta(days=timebase)
    monthAgo = (today - datetime.timedelta(days=timegap))
    today = today.strftime("%Y%m%d")
    monthAgo = monthAgo.strftime("%Y%m%d")
    return today, monthAgo

all_etf = get_all_alive_fund(180)

def get_sorted_etf_data(timebase=0, timegap=30):
    today, monthAgo = get_Date_base_gap(timebase, timegap)
    etf2data = {}
    count = 0
    existETF = os.listdir('etf_cache')
    for e in all_etf:
        if e+'.txt' not in existETF:
            if (count + 1) % 79 == 0:
                print("Progress:%s / %s" % (len(etf2data), len(all_etf)))
                time.sleep(60)
            data = get_fund_daily(e, monthAgo, today)
            data.to_csv('etf_cache/%s.txt'%e, index=False)
            count += 1
        else:
            data = pd.read_csv('etf_cache/%s.txt'%e)
        try:
            if type(data.loc[0,'trade_date']) == str:
                data = data[data['trade_date'] <= today]
                data = data[data['trade_date'] >= monthAgo]
            else:
                data = data[data['trade_date'] <= int(today)]
                data = data[data['trade_date'] >= int(monthAgo)]
        except Exception as e:
            continue
        try:
            price_change = (data.iloc[0,:]['close'] - data.iloc[-1,:]['close']) / data.iloc[-1,:]['close']
            if data.iloc[0,:]['amount']<10000 or data.iloc[0,:]['close']>10:
                etf2data[e] = -1
            else:
                etf2data[e] = price_change
        except Exception as e:
            pass
    d_order = sorted(etf2data.items(), key=lambda x: x[1], reverse=True)
    return d_order

def buy_topK(timebase = 60, K = 10):
    df =  get_sorted_etf_data(timebase, 50)
    # df1 =  get_sorted_etf_data(timebase, 20)
    # df2 =  get_sorted_etf_data(timebase, 50)
    topK = [x for x in df[:K]]
    code_change = {x[0]:x[1] for x in topK}
    codes = [x[0] for x in topK]
    # codes1 = [x[0] for x in df1[:K]]
    # codes2 = [x[0] for x in df2[:K]]
    today, monthAgo = get_Date_base_gap(timebase-20, 20)
    count = 0
    # time.sleep(60)
    ave = []
    existETF = os.listdir('etf_cache')

    for i in range(len(codes)):
        if codes[i] + '.txt' not in existETF:
            if (count + 1) % 79 == 0:
                print("Progress:%s / %s" % (len(codes), len(all_etf)))
                time.sleep(60)
            # if codes[i] not in codes1 or codes[i]  not in codes2:
            #     continue
            data = get_fund_daily(codes[i], monthAgo, today)
            count += 1
        else:
            data = pd.read_csv('etf_cache/%s.txt' % codes[i])
        data = data[data['trade_date'] <= int(today)]
        data = data[data['trade_date'] >= int(monthAgo)]
        price_change = (data.iloc[0, :]['close'] - data.iloc[-1, :]['close']) / data.iloc[-1, :]['close']
        ave.append(price_change)
        # print("Top %s【%s】,PRE_MONTH:%s(%s), THIS_MONTH:%s(%s)"%(i, codes[i], round(code_change[codes[i]],3), data.iloc[-1, :]['close'], round(price_change,3), data.iloc[0, :]['close']))
    print("TIMEGAP:%s, K:%s, Average Earn:%s"%(timebase-20, K, sum(ave)/len(ave)))


if __name__ == '__main__':
    # for i in [20,30,40,50,60,70,80,90,100,110, 120]:
    #     for j in [5,10]:
    #         buy_topK(i, j)
    #         # time.sleep(6)
    #     print("======")
    fund_name = get_fund_name()
    for x in range(10):
        df = get_sorted_etf_data(x, 90)
        for i in df[:10]:
            print(fund_name[i[0]], round(i[1], 3), end=' | ')
        print("\n================================================================")