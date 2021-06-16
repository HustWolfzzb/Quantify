import os
import sys
sys.path.append('../')
from DataEngine.Data import get_fund_basic, get_fund_daily, get_fund_name, qo
import time
import datetime
import pandas as pd
import jieba

def get_all_alive_fund(timegap):
    # 先获得时间数组格式的日期
    monthAgo = (datetime.datetime.now() - datetime.timedelta(days=timegap))
    # 转换为其他字符串格式
    monthago = monthAgo.strftime("%Y%m%d")
    df = get_fund_basic()
    x = df[df['status'] == 'L']
    x = x[x['list_date'] < monthago]
    all_fund = x['ts_code'].tolist()
    all_fund.append('516020.SH')
    return all_fund

def get_Date_base_gap(timebase, timegap):
    today = datetime.datetime.now() - datetime.timedelta(days=timebase)
    monthAgo = (today - datetime.timedelta(days=timegap))
    today = today.strftime("%Y%m%d")
    monthAgo = monthAgo.strftime("%Y%m%d")
    return today, monthAgo

all_etf = get_all_alive_fund(10)
fund_name = get_fund_name()


def get_sorted_etf_data(timebase=0, timegap=30):
    today, monthAgo = get_Date_base_gap(timebase, timegap)
    etf2data = {}
    count = 0
    if not os.path.exists('etf_cache'):
        os.makedirs('etf_cache')
    existETF = os.listdir('etf_cache')
    for e in all_etf:
        if e+'.csv' not in existETF:
            if (count + 1) % 79 == 0:
                print("\rProgress:%s / %s" % (len(etf2data), len(all_etf)), end='...', flush=True)
                time.sleep(60)
            try:
                data = get_fund_daily(e, monthAgo, today)
            except OSError as x:
                time.sleep(61)
                data = get_fund_daily(e, monthAgo, today)
            data.to_csv('etf_cache/%s.csv'%e, index=False)
            print("【%s】存储了新的ETF：%s %s"%(count, fund_name[e],e))
            count += 1
        else:
            # print("读取了ETF：%s" % fund_name[e])
            data = pd.read_csv('etf_cache/%s.csv'%e)
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
            if data.iloc[0,:]['vol']<100000 or data.iloc[0,:]['close']>10:
                etf2data[e] = -1
            else:
                etf2data[e] = price_change
        except Exception as e:
            pass
    d_order = sorted(etf2data.items(), key=lambda x: x[1], reverse=True)
    return d_order


def get_best_etf(timebase=0, timegap=30):
    etf2data = {}
    count = 0
    existETF = os.listdir('etf_cache')
    for e in all_etf:
        if e + '.csv' not in existETF:
            today, monthAgo = get_Date_base_gap(0, 3650)
            if (count + 1) % 79 == 0:
                print("\rProgress:%s / %s" % (len(etf2data), len(all_etf)), end='...')
                time.sleep(60)
            try:
                data = get_fund_daily(e, monthAgo, today)
            except OSError as x:
                print(x)
                time.sleep(61)
                data = get_fund_daily(e, monthAgo, today)
            data.to_csv('etf_cache/%s.csv' % e, index=False)
            count += 1
        else:
            data = pd.read_csv('etf_cache/%s.csv' % e)
        today, monthAgo = get_Date_base_gap(timebase, timegap)
        try:
            if data.iloc[0, :]['amount'] < 100 or \
                    data.iloc[0, :]['close'] > 10 or data.iloc[0, :]['close'] < 0.5:
                continue
        except Exception as e:
            continue
        try:
            if str(today) not in [str(x) for x in data['trade_date']]:
                continue
            if type(data.loc[0, 'trade_date']) == str:
                data = data[data['trade_date'] <= today]
                data = data[data['trade_date'] >= monthAgo]
            else:
                data = data[data['trade_date'] <= int(today)]
                data = data[data['trade_date'] >= int(monthAgo)]
        except Exception as e:
            continue
        if data.iloc[0, :]['close'] > data.iloc[0, :]['ma20'] \
                and data.iloc[0, :]['open'] <= data.iloc[0, :]['ma20'] : #"\
                # and  data.iloc[1, :]['ma20'] > data.iloc[0, :]['ma20'] :
            print("%s, %s - %s突破20日线，可关注当天收盘：%s"
                  %(data.iloc[0, :]['trade_date'], fund_name[e],e,
                    data.iloc[0, :]['close']))
        if data.iloc[0, :]['close'] < data.iloc[0, :]['ma20'] \
                and data.iloc[0, :]['open'] >= data.iloc[0, :]['ma20'] : #"\
                # and  data.iloc[1, :]['ma20'] > data.iloc[0, :]['ma20'] :
            print("%s, 【回踩！】%s - %s突破20日线，可关注当天收盘：%s"
                  %(data.iloc[0, :]['trade_date'], fund_name[e],e,
                    data.iloc[0, :]['close']))



def real_time_etf():
    existETF = os.listdir('etf_cache')
    datas = {}
    for e in all_etf:
        code = e
        data = pd.read_csv('etf_cache/%s.csv' % e)
        try:
            if data.iloc[0, :]['vol'] < 100000 or data.iloc[0, :]['close'] > 10:
                continue
        except Exception as x:
            continue
        try:
            newestData = data.iloc[0, :]
            newestData['ma20'] = round((data.loc[0, 'ma20'] * 20 - data.loc[19, 'close'])/19, 4)
            datas[code] = newestData
        except Exception as x:
            continue
    breaks = []
    while True:
        price_nows = qo.stocks([i[:6] for i in existETF])
        for e in datas.keys():
            code = e
            price_now = price_nows[e[:6]]['now']
            price_open = price_nows[e[:6]]['open']
            pre_close = price_nows[e[:6]]['close']
            data = datas[code]
            ma20 = (price_now + data['ma20'] * 19) / 20
            if (price_open < ma20 and price_now >= ma20) or (pre_close < ma20 and price_now >= ma20) :
                s="%s - %s突破20日线，可关注, 昨收[%s] 开盘[%s]  现价[%s] MA20[%s]\n" % ( fund_name[e], e,
                         pre_close, price_open, price_now, round(ma20, 3))
                if s not in breaks:
                    breaks.append(s)
                    print(s)
        # print("\r %s"%lines, end='')
        time.sleep(10)

def fulsh_output(string):
    sys.stdout.write('\r' + str(string) )
    sys.stdout.flush()
    time.sleep(1)

def buy_topK(timebase = 0, timeOld = 7,  timegap = 30, K = 10):
    df =  get_sorted_etf_data(timeOld, timegap)
    K_area = []
    K_name = set()
    for i in df[:50]:
        if list(jieba.cut(fund_name[i[0]]))[0] not in K_name:
            K_name.add(list(jieba.cut(fund_name[i[0]]))[0])
            K_area.append(i)

    print("=======")
    # df1 =  get_sorted_etf_data(timebase, 20)
    # df2 =  get_sorted_etf_data(timebase, 50)
    df = K_area
    for i in df[:K]:
        print(fund_name[i[0]], round(i[1], 3), end=' | ')
    print("\n")
    topK = [x for x in df[:K]]
    code_change = {x[0]:x[1] for x in topK}
    codes = [x[0] for x in topK]
    # codes1 = [x[0] for x in df1[:K]]
    # codes2 = [x[0] for x in df2[:K]]
    today, monthAgo = get_Date_base_gap(timebase, timeOld)
    count = 0
    # time.sleep(60)
    ave = []
    existETF = os.listdir('etf_cache')

    for i in range(len(codes)):
        if codes[i] + '.csv' not in existETF:
            if (count + 1) % 79 == 0:
                print("\rProgress:%s / %s" % (len(codes), len(all_etf)), end='...')
                time.sleep(60)
            # if codes[i] not in codes1 or codes[i]  not in codes2:
            #     continue
            data = get_fund_daily(codes[i], monthAgo, today)
            count += 1
        else:
            data = pd.read_csv('etf_cache/%s.csv' % codes[i])
        data = data[data['trade_date'] <= int(today)]
        data = data[data['trade_date'] >= int(monthAgo)]
        price_change = (data.iloc[0, :]['close'] - data.iloc[-1, :]['close']) / data.iloc[-1, :]['close']
        ave.append(price_change)
        print("TIMEGAP:%s, K:%s, NAME:%s, Earn:%s"%(timebase, K, fund_name[codes[i]], round(price_change,4)))
        # print("Top %s【%s】,PRE_MONTH:%s(%s), THIS_MONTH:%s(%s)"%(i, codes[i], round(code_change[codes[i]],3), data.iloc[-1, :]['close'], round(price_change,3), data.iloc[0, :]['close']))
    print("TIMEGAP:%s, K:%s, Average Earn:%s"%(timebase, K, round(sum(ave)/len(ave),4)))
    return round(sum(ave)/len(ave),4)


if __name__ == '__main__':
    # for i in [20,30,40,50,60,70,80,90,100,110, 120]:
    #     for j in [5,10]:
    #         buy_topK(i, j)
    #         # time.sleep(6)
    #     print("======")
    # fund_name = get_fund_name()
    get_sorted_etf_data(0, 3650)

    # for x in range(10):
    #     df = get_sorted_etf_data(x * 7, 28)
    #     for i in df[:10]:
    #         print(fund_name[i[0]], round(i[1], 3), end=' | ')
    #     print("\n================================================================")
    #
    # for i in range(100,0,-1):
    #     get_best_etf(timebase=i, timegap=30)
    #     print("======\n")
    # change = []
    # s = get_sorted_etf_data(0, 180)
    # for i in range(15):
    #     # for j in range(3):
    #         # for k in [5,10,15,20]:
    #     j = 1
    #     k = 10
    #     # time.sleep(6)
    #     print("\n\nTIMEBASE:%s, GAP:%s, K:%s"%(i*7, (j+1)*7, k))
    #     change.append(buy_topK(i*7, i*7 + 7, (j+1)*7, k))
    # start = 10000
    # for i in range(len(change)):
    #     start = start * (1+change[len(change) - i - 1])
    #     print("一周资金：", start)
    real_time_etf()