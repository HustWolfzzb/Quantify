import os
import random
import time
import sys
sys.path.append('../')
from DataEngine.Data import pro, get_pro_stock_basic, get_concept, get_index_basic, \
    get_stock_concepts, get_index_weight, get_index, get_stock_name, get_daily_basic, \
    get_stock_weekly, qo, get_stock_daily
from Strategy.follow_fund import get_Date_base_gap
from Feature.pre_process_data import process_data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib
# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

time_format = 'daily'
def plot_(label_list, num_list1, name):
    """
    绘制条形图
    left:长条形中点横坐标
    height:长条形高度
    width:长条形宽度，默认值0.8
    label:为后面设置legend准备
    """
    plt.figure(figsize=(30, 15))
    x = range(len(num_list1))
    rects1 = plt.bar(x=x, height=num_list1, width=0.4, alpha=0.8, color='red', label=name)
    plt.ylim(min(num_list1) * 1.1, max(num_list1) * 1.1)  # y轴取值范围
    plt.ylabel("涨幅", fontsize=15)
    """
    设置x轴刻度显示值
    参数一：中点坐标
    参数二：显示值
    """
    plt.xticks([index + 0.2 for index in x], label_list)
    plt.xticks(size='small', rotation=90, fontsize=12)

    plt.xlabel(name, fontsize=20)
    plt.title("%s-涨幅" % name, fontsize=len(label_list))
    plt.legend()  # 设置题注
    # 编辑文本
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom")
    plt.savefig('%s.png' % name)
    plt.show()



def all_base():
    stock_info = get_pro_stock_basic()
    length = int(stock_info.size / len(stock_info.columns))
    concept_info = get_concept()
    concepts = concept_info['name']
    concepts_code = concept_info['code']
    concept_code2name = {concepts_code[i]:concepts[i] for i in range(len(concepts))}
    stock_concept = {}
    concept_stock = {}
    # concept_info.set_index(["code"], inplace=True)

    count = 0
    for i in concepts_code[:90]:
        data = get_stock_concepts(i)
        concept_stock[i] = data['ts_code']
        count += 1
        index = count
        length = len(concepts_code)
        if index % 100 == 0:
            print("\r【%s%s%s】" % (
            '>>' * int(index * 100 // length), int(index * 100 // length), '=' * (100 - int(index // length))))
            time.sleep(60)
        for j in data['ts_code']:
            if not stock_concept.get(j):
                stock_concept[j] = [i]
            else:
                stock_concept[j].append(i)

    industry = stock_info['industry']
    stock_industry = {}
    industry_stock = {}
    for index in range(length):
        stock_industry[stock_info.at[index, 'ts_code']] = stock_info.at[index, 'industry']
        if not industry_stock.get(stock_info.at[index, 'industry']):
            industry_stock[stock_info.at[index, 'industry']] = [stock_info.at[index, 'ts_code']]
        else:
            industry_stock[stock_info.at[index, 'industry']].append(stock_info.at[index, 'ts_code'])


    area = stock_info['area']
    stock_area = {}
    area_stock = {}
    for index in range(length):
        stock_area[stock_info.at[index, 'ts_code']] = stock_info.at[index, 'area']
        if not area_stock.get(stock_info.at[index, 'area']):
            area_stock[stock_info.at[index, 'area']] = [stock_info.at[index, 'ts_code']]
        else:
            area_stock[stock_info.at[index, 'area']].append(stock_info.at[index, 'ts_code'])

    df = pro.daily()
    df.set_index(["ts_code"], inplace=True)
    # 去重
    df = df.loc[~df.index.duplicated(keep='first')].copy()
    for name in ['industry', 'concept', 'area']:
        if name == 'industry':
            stock_name = stock_industry
            name_stock = industry_stock
        elif name == 'concept':
            stock_name = stock_concept
            name_stock = concept_stock
        elif name == 'area':
            stock_name = stock_area
            name_stock = area_stock
        num_list = []
        names = list(name_stock.keys())
        for i in names:
            num = 0
            for j in name_stock[i]:
                try:
                    num += df.at[j, 'pct_chg']
                except Exception as e:
                    print(e)
            num_list.append(round(num/len(name_stock[i]),4))
        try:
            names = [concept_code2name[names[i]] + str(len(name_stock[i])) for i in range(len(names))]
        except Exception as e:
            names = [concept_code2name[s]  for s in names]

        names_nums = {names[i]:num_list[i] for i in range(len(num_list))}
        nn = sorted(names_nums.items(), key=lambda x: x[1], reverse=True)
        for i in nn[:5]:
            print(nn[0], name_stock[nn[0]])
        names_nums = {names[i]:num_list[i] for i in range(len(num_list))}
        nn = sorted(names_nums.items(), key=lambda x: x[1], reverse=True)
        if len(nn) > 50:
            nn = nn[:50]
        names = [n[0] for n in nn]
        num_list = [n[1] for n in nn]
        print("NumX:%s, NumY:%s, NAME:%s "%(len(names), len(num_list), name))
        plot_(names, num_list, name)



def all_index():
    index_basic = get_index_basic()
    index_basic = index_basic[index_basic['category']!='债券指数']
    index_basic = index_basic[index_basic['category']!='其他']
    index_code = index_basic['ts_code'].to_list()
    index_name = index_basic['name'].to_list()
    today, ago = get_Date_base_gap(0, 100)
    index_weight = {}
    count = 0
    index_data = {}
    index_pctChg = {}
    stock_name = get_stock_name()
    existIndex = os.listdir('index')
    existIndexWeight = os.listdir('index_weight')
    length = len(index_code)
    code_name = {index_code[i]:index_name[i] for i in range(length)}
    token = 0
    while count < length:
        index = count
        if index % 100 == 0:
            print("\r【%s%s/%s%s】" % ('>' * int(index * 100 // length), index , length, '=' * (100 - int(index * 100 // length))), end='')
        code = index_code[index]
        try:
            # if code.find('h') != -1:
            #     count += 1
            #     continue
            if code+'.csv' not in existIndex:
                df = get_index(code, ago, today, token=token)
                df.to_csv('index/%s.csv' % code, index=False)
                # print( code+'.csv' +" not in index!")
            else:
                df = pd.read_csv('index/%s.csv'%code)

            if code + '.csv' not in existIndexWeight:
                weight = get_index_weight(code, ago, today)
                weight.to_csv('index_weight/%s.csv' % code, index=False)
                # print(code + '.csv' + " not in index_weight!")
            else:
                weight = pd.read_csv('index_weight/%s.csv' % code)

            if len(df) < 10:
                count += 1
                continue
            index_data[code] = df
            index_pctChg[code] = df.loc[0,'pct_chg']
            index_weight[code] = weight
            count += 1
        except Exception as e:
            print(e)
            token += 1
            token %= 2
            time.sleep(30)

    index_code = list(index_data.keys())
    sort_index_pctChg = sorted(index_pctChg.items(), key=lambda x: x[1], reverse=True)
    print("\n")
    for i in sort_index_pctChg:
        code = i[0]
        name = code_name[code]
        weight = index_weight[code]['con_code'].to_list()
        weight_stock_name = []
        for w in weight:
            try:
                if w[0] != '0' and w[0] != '6':
                    continue
                weight_stock_name.append(stock_name[w])
            except KeyError as e:
                continue
        if len(weight_stock_name) > 5:
            print(name, ' : ', i[1], ",".join(weight_stock_name) )

def get_stock_info(field='industry'):
    if field == 'shenwan':
        from Monitor.shenwan import read_classify
        return read_classify()
    data = get_pro_stock_basic()
    data.set_index(['ts_code'], inplace=True)
    industry_stock = {}
    stock_industry = {}
    for index in data.index:
        stock_industry[index] = data.at[index, 'industry']
        if not industry_stock.get(data.at[index, 'industry']):
            industry_stock[data.at[index, 'industry']] = [index]
        else:
            industry_stock[data.at[index, 'industry']].append(index)
    return stock_industry, industry_stock


def all_stock(filter=True, path='/Users/zhangzhaobo/PycharmProjects/Quantify/Monitor/'):
    stocks = get_pro_stock_basic()['ts_code'].tolist()
    new_stocks = []
    if filter:
        for idx in stocks:
            if idx[0]=='3' or idx[:3] == '688':
                continue
            else:
                new_stocks.append(idx)
    stocks = new_stocks
    today, ago = get_Date_base_gap(0, 365)
    count = 0
    length = len(stocks)
    # length = 100
    if path.find('Monitor')==-1:
        base = os.getcwd() + '/Monitor/'
    else:
        base = path
    dir_ = base + 'stock_%ss'%time_format
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    existStock = os.listdir(dir_)
    stock_data = {}
    ok_stock = []
    while count < length:
        index = count
        if index % 10 == 0:
            print("\r【%s%s/%s%s】" % ('>' * int(index * 20 // length), index , length, '=' * (20 - int(index * 20 // length))), end='')
        code = stocks[index]
        try:
            if code+'.csv' not in existStock:
                # count += 1
                # continue
                if dir_.find('daily') != -1:
                    df = get_stock_daily(ts_code=code, start_date=ago, end_date=today, ma=[3, 5, 10, 13, 30])
                else:
                    df = get_stock_weekly(ts_code=code, start_date=ago, end_date=today, ma=[3, 5, 10, 13, 30])

                # if len(df) < 80:
                #     count += 1
                #     continue
                if len(df) < 10:
                    count += 1
                    continue
                df.to_csv(dir_+'/%s.csv' % code, index=False)
                # print( code+'.csv' +" not in stock!")
            else:
                df = pd.read_csv(dir_+'/%s.csv'%code)
                # count += 1
                # print( code+'.csv' +" in stock!")
            if len(df) < 20:
                # print( code+'.csv' +" not long enough!")
                count += 1
                continue
            stock_data[code] = df
            ok_stock.append(code)
            count += 1
        except Exception as e:
            if str(e).find('not enough values to unpack') != -1 \
                    or str(e).find('object is not subscriptable') != -1 \
                    or str(e).find("object of type 'NoneType' has no len()") != -1:
                print(e)
                count += 1
                continue
            else:
                print(e)
                if str(e).find('NoneType')!=-1:
                    count += 1
                    pass
                else:
                    time.sleep(61)
    return stock_data, ok_stock

def get_industry_avg(stock_data, filed_stock, ss):
    field_avg = {}
    for field in filed_stock.keys():
        stocks = filed_stock[field]
        avg = []
        for code in stocks:
            if code not in stock_data.keys():
                continue
            data = stock_data[code]
            try:
                avg.append(data.loc[ss, 'pct_chg'])
            except Exception as e:
                continue
        if len(avg) == 0:
            field_avg[field] = 0
        else:
            field_avg[field] = round(sum(avg)/len(avg), 3)
    return field_avg

def get_industry_avg_real(stock_data, filed_stock):
    field_avg = {}
    for field in filed_stock.keys():
        stocks = [x[:6] for x in filed_stock[field]]
        avg = []
        for code in stocks:
            if code not in stock_data.keys():
                continue
            data = stock_data[code]
            avg.append(round((data['now'] - data['close'])/data['close'],4))
        field_avg[field] = round(sum(avg)/len(avg),3)
    return field_avg

def check_plus(data, gap = 0.995):
    for i in range(len(data) - 1):
        if data[i] < data[i + 1] * gap:
            return 0
        else:
            continue
    return 1

def check_up_times(close, open):
    up = 0
    for i in range(len(close)):
        if close[i] > open[i]:
            up += 1
    return up

def check_high_close(close, high, gap=0.96):
    for i in range(len(close)):
        if close[i] / high[i] < gap:
            return False
    return True

def get_best_stcok_by_awei(stock_data, ok_stock, ss=0, gap = 30, ma_value=7,  ma_value_1 = 14):
    stock_name = get_stock_name()
    print("\n")
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    with open('awei-%s.txt'%time_format, 'w', encoding='utf8') as f:
        for code in ok_stock:
            if code in industry_stock['农业综合'] or code in industry_stock['银行'] or stock_name[code].find('ST') != -1:
                continue
            data = stock_data[code]
            if gap == 0:
                gap = len(data)
            date = data.loc[ss:gap+ss, 'trade_date'].tolist()
            high = data.loc[ss:gap+ss, 'high'].tolist()
            low = data.loc[ss:gap+ss, 'low'].tolist()
            open_ = data.loc[ss:gap+ss, 'open'].tolist()
            close = data.loc[ss:gap+ss, 'close'].tolist()
            amount = data.loc[ss:gap + ss, 'amount'].tolist()
            try:
                vol = data.loc[ss:gap + ss, 'ma_v_' + str(ma_value)].tolist()
                ma = data.loc[ss:gap + ss, 'ma' + str(ma_value)].tolist()
                ma1 = data.loc[ss:gap + ss, 'ma' + str(ma_value_1)].tolist()
            except Exception as e:
                # print(e)
                continue
            # name = stock_name[code]
            if stock_name[code].find('ST') != -1:
                continue
            for idx in range(len(close) - 6, -1, -1):
                DATE = date[idx:idx + 5]
                MA = ma[idx:idx + 5]
                MA1 = ma1[idx:idx + 5]
                VOL = vol[idx:idx + 5]
                AMOUNT = amount[idx:idx + 5]
                CLOSE = close[idx:idx + 5]
                HIGH = high[idx:idx + 5]
                LOW = low[idx:idx + 5]
                OPEN = open_[idx:idx + 5]
                if min(AMOUNT) < 100000:
                    continue
                if check_up_times(CLOSE, OPEN) < 3:
                    continue
                if (CLOSE[0] - OPEN[ 4]) / OPEN[4] > 0.2 or (CLOSE[0] - OPEN[4]) / OPEN[4] < 0.05:
                    continue
                if check_plus(MA) == 0:
                    continue
                if check_plus(VOL) == 0:
                    continue
                # if VOL[0] <= VOL[1]:
                #     continue
                if not check_high_close(CLOSE, HIGH, 0.92):
                    continue
                if HIGH[0] - CLOSE[0] > (CLOSE[0] - OPEN[0]) * 1.5 or CLOSE[0] - OPEN[0] < 0:
                    continue
                if VOL[0] == max(VOL) and CLOSE[0] < OPEN[0]:
                    continue
                buy_price = 0
                if idx >= 5:
                    for i in range(idx - 1, idx - 5, -1):
                        if low[i] < ma[i]:
                            buy_price = ma[i]
                            break
                    if buy_price == 0:
                        continue
                    f.write("%s 当日可买入：%s-%s, 五日涨幅：%s, 买入后五日涨幅：%s, 当日收盘价：%s, \n" % (DATE[0],
                                                                            code, stock_name[code],
                                                                            round((CLOSE[0] - OPEN[4]) / OPEN[4], 3),
                                                                            round((close[idx - 5] - CLOSE[0])/ CLOSE[0], 3),
                                                                            CLOSE[0]))
                else:
                    for i in range(idx - 1, -1, -1):
                        if low[i] < ma[i]:
                            buy_price = ma[i]
                            break
                    if buy_price == 0:
                        buy_price=CLOSE[0]
                    f.write("%s 当日可买入：%s-%s, 五日涨幅：%s, 至今日涨幅：%s, 当日收盘价：%s\n"%(DATE[0],
                                                                      code, stock_name[code],
                                                                         round((CLOSE[0] - OPEN[4]) / OPEN[4], 3),
                                                                         round((close[0] - buy_price) / buy_price, 3),
                                                                      CLOSE[0]))


def get_best_stcok_by_vol(stock_data, ok_stock, ss=0, gap = 30, ma_value=7,  ma_value_1 = 14):
    stock_name = get_stock_name()
    print("\n")
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    if gap < 20:
        gap = 20
    with open('vol-%s.txt'%time_format, 'a', encoding='utf8') as f:
        for code in ok_stock:
            data = stock_data[code]
            name = stock_name[code]
            if gap == 0:
                gap = len(data)
            date = data.loc[ss:gap+ss, 'trade_date'].tolist()
            high = data.loc[ss:gap+ss, 'high'].tolist()
            low = data.loc[ss:gap+ss, 'low'].tolist()
            open_ = data.loc[ss:gap+ss, 'open'].tolist()
            close = data.loc[ss:gap+ss, 'close'].tolist()
            amount = data.loc[ss:gap + ss, 'amount'].tolist()
            vol = data.loc[ss:gap + ss, 'vol'].tolist()
            # name = stock_name[code]
            if stock_name[code].find('ST') != -1:
                continue
            if vol[0] / min(vol) < 2 \
                    and vol[0] / min(vol) > 0.8 \
                    and max(vol) / min(vol) > 5 \
                    and close[0] / min(close) < 1.08 \
                    and close[0] / min(close) > 0.9 \
                    and max(close) / min(close) > 1.12:
                if  ss > 0:
                    f.write("【%s】 [%s: %s] %s:%s, close:%s, nextClose:%s \n"
                            % (data.loc[ss, 'trade_date'], code, name,
                               stock_industry[code], field_avg[stock_industry[code]],
                               close[0], data.loc[ss - 1, 'close']))
                else:
                    f.write("【%s】 [%s: %s] %s:%s, close:%s \n"
                                % (data.loc[ss, 'trade_date'], code, name,
                                   stock_industry[code], field_avg[stock_industry[code]],
                                   close[0]))

def get_best_stcok_by_ma(stock_data, ok_stock, ss=0, gap = 30, ma_value=7,  ma_value_1 = 14):
    stock_name = get_stock_name()
    print("\n")
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    with open('ma.txt', 'w', encoding='utf8') as f:
        for code in ok_stock:
            data = stock_data[code]
            if gap == 0:
                gap = len(data)
            date = data.loc[ss:gap+ss, 'trade_date'].tolist()
            high = data.loc[ss:gap+ss, 'high'].tolist()
            open_ = data.loc[ss:gap+ss, 'open'].tolist()
            close = data.loc[ss:gap+ss, 'close'].tolist()
            vol = data.loc[ss:gap+ss, 'vol'].tolist()
            ma = data.loc[ss:gap + ss, 'ma' + str(ma_value)].tolist()
            ma1 = data.loc[ss:gap + ss, 'ma' + str(ma_value_1)].tolist()
            # name = stock_name[code]
            if stock_name[code].find('ST') != -1:
                continue
            flag = False
            buy_price = 0
            success = 0
            fail = 0
            earn = 0
            loss = 0
            for idx in range(len(close) - 2, -1, -1):
                MA = ma[idx]
                MA1 = ma1[idx]
                CLOSE = close[idx]
                HIGH = high[idx]
                if ma[idx + 1] < ma1[idx + 1] and MA >= MA1 \
                        and not flag \
                        and vol[idx] >= vol[idx + 1] * 0.9\
                        and (close[idx] - open_[idx]) / open_[idx] < 0.2 \
                        and (close[idx] - open_[idx]) / open_[idx]  > 0 \
                        and (high[idx] - close[idx]) / (close[idx] - open_[idx]) < 2:
                    flag = True
                    buy_price = CLOSE
                    f.write("【%s】买入-> %s, MA%s:%s, %s, MA%s:%s, 价格：%s\n"%(date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1, round(MA1, 2), round(CLOSE, 2)))
                    continue
                if ((ma[idx + 1] >= ma1[idx + 1] and MA < MA1) or (HIGH > buy_price * 1.05)) and flag:
                    flag = False
                    if HIGH > buy_price * 1.05 or CLOSE > buy_price:
                        Nice_Shot = '=='
                        success += 1
                        if HIGH > buy_price * 1.05:
                            earn = HIGH - buy_price
                        else:
                            earn = CLOSE - buy_price
                        f.write("【%s】卖出<-：%s, MA%s:%s, %s, MA%s:%s, 【%s价格%s】：%s\n" % (
                        date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1,
                        round(MA1, 2), Nice_Shot, Nice_Shot, round(buy_price * 1.05, 2)))
                    else:
                        Nice_Shot = '~~'
                        fail += 1
                        loss = buy_price - CLOSE
                        f.write("【%s】卖出<- %s, MA%s:%s, %s, MA%s:%s, 【%s价格%s】：%s\n" % (
                            date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1,
                            round(MA1, 2), Nice_Shot, Nice_Shot, round(CLOSE, 2)))
            # print("胜: %s Earn:%s , 负：%s Loss:%s, "%(success, round(earn,2) , fail, round(loss,2)), end='')
            # if success / (fail + 1) > 2:
            #     print("胜手比例:%s"%(round((success + 1) / (loss + 1),2) ))
            # else:
            #     print("")

def get_best_stcok_by_mo(stock_data, ok_stock, ss=0, gap = 30, ma_value=10,  ma_value_1 = 20):
    stock_name = get_stock_name()
    print("\n")
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    with open('mo.txt', 'w', encoding='utf8') as f:
        f.write('[=======]\n')
        for code in ok_stock:
            data = stock_data[code]
            if gap == 0:
                gap = len(data)
            date = data.loc[ss:gap+ss, 'trade_date'].tolist()
            high = data.loc[ss:gap+ss, 'high'].tolist()
            open_ = data.loc[ss:gap+ss, 'open'].tolist()
            close = data.loc[ss:gap+ss, 'close'].tolist()
            vol = data.loc[ss:gap+ss, 'vol'].tolist()
            ma = data.loc[ss:gap + ss, 'ma' + str(ma_value)].tolist()
            ma1 = data.loc[ss:gap + ss, 'ma' + str(ma_value_1)].tolist()
            # name = stock_name[code]
            if stock_name[code].find('ST') != -1:
                continue
            flag = False
            buy_price = 0
            success = 0
            fail = 0
            earn = 0
            loss = 0
            for idx in range(len(close) - 2, -1, -1):
                MA = ma[idx]
                MA1 = ma1[idx]
                CLOSE = close[idx]
                HIGH = high[idx]
                if ma[idx + 1] < ma1[idx + 1] and MA >= MA1 \
                        and not flag \
                        and vol[idx] >= vol[idx + 1] * 0.9\
                        and (close[idx] - open_[idx]) / open_[idx] < 0.2 \
                        and (close[idx] - open_[idx]) / open_[idx]  > 0 \
                        and (high[idx] - close[idx]) / (close[idx] - open_[idx]) < 2:
                    flag = True
                    buy_price = CLOSE
                    f.write("【%s】买入-> %s, MA%s:%s, %s, MA%s:%s, 价格：%s\n"%(date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1, round(MA1, 2), round(CLOSE, 2)))
                    continue
                if ((ma[idx + 1] >= ma1[idx + 1] and MA < MA1) or (HIGH > buy_price * 1.05)) and flag:
                    flag = False
                    if HIGH > buy_price * 1.05 or CLOSE > buy_price:
                        Nice_Shot = '=='
                        success += 1
                        if HIGH > buy_price * 1.05:
                            earn = HIGH - buy_price
                        else:
                            earn = CLOSE - buy_price
                        f.write("【%s】卖出<-：%s, MA%s:%s, %s, MA%s:%s, 【%s价格%s】：%s\n" % (
                        date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1,
                        round(MA1, 2), Nice_Shot, Nice_Shot, round(buy_price * 1.05, 2)))
                    else:
                        Nice_Shot = '~~'
                        fail += 1
                        loss = buy_price - CLOSE
                        f.write("【%s】卖出<- %s, MA%s:%s, %s, MA%s:%s, 【%s价格%s】：%s\n" % (
                            date[idx], stock_name[code], ma_value, round(ma[idx + 1], 2), round(MA, 2), ma_value_1,
                            round(MA1, 2), Nice_Shot, Nice_Shot, round(CLOSE, 2)))
            # print("胜: %s Earn:%s , 负：%s Loss:%s, "%(success, round(earn,2) , fail, round(loss,2)), end='')
            # if success / (fail + 1) > 2:
            #     print("胜手比例:%s"%(round((success + 1) / (loss + 1),2) ))
            # else:
            #     print("")

def get_best_stcok_by_obv(stock_data, ok_stock, ss=0, gap = 30, ma_value=5, filter_rate = 0.1, ma_value_1 = 20):
    stock_name = get_stock_name()
    print("\n")
    code_90 = []
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    code_ok = []
    for code in ok_stock:
        data = stock_data[code]
        length = len(data)
        close = data.loc[ss:gap+ss, 'close'].tolist()
        high = data.loc[ss:gap+ss, 'high'].tolist()
        open = data.loc[ss:gap+ss, 'open'].tolist()


        up = 0
        down = 0
        sumDay = len(close)
        name = stock_name[code]
        # if name.lower().find('st') != -1:
        #     continue
        if close[0] - open[0] < (high[0] - close[0]) * 2 \
                or stock_name[code].find('ST') != -1:
            continue

        # for i in range(sumDay):
        #     if close[i] < open[i]:
        #         down += 1
        #     else:
        #         up += 1
        # if down < sumDay * filter_rate :# and (high[0] - close[0])*2 < (close[0] - open[0]) and close[0]>open[0]:
        #     if ss > 0:
        #         print("【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s。 【%s】"
        #               % (code, name, up, down, close[0], data.loc[ss-1, 'close'], data.loc[ss,'trade_date']))
        #     else:
        #         print("[%s:%s]【%s:%s】，上：%s, 下:%s, close:%s。【%s】" % (
        #             stock_industry[code], field_avg[stock_industry[code]],
        #              code, name, up, down, close[0], data.loc[ss,'trade_date']))
        #     code_ok.append(code)
        if (close[0] - close[10]) / close[10] >  (close[0] - close[20]) / close[20]  \
            and  (close[0] - close[20]) / close[20] > 0 \
            and (close[0] - close[5]) / close[5] > 0 \
            and close[0] > open[0] \
            and (close[0] - close[20]) / close[20] > (close[0] - close[30]) / close[30]:# and (high[0] - close[0])*2 < (close[0] - open[0]) and close[0]>open[0]:
            if ss > 0:
                print("【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s。 【%s】"
                      % (code, name, round((close[0] - close[10]) / close[10],2), round((close[0] - close[20]) / close[20] , 2), close[0], data.loc[ss-1, 'close'], data.loc[ss,'trade_date']))
            else:
                print("[%s:%s]【%s:%s】，上：%s, 下:%s, close:%s。【%s】" % (
                    stock_industry[code], field_avg[stock_industry[code]],
                     code, name, up, down, close[0], data.loc[ss,'trade_date']))
            code_ok.append(code)
    return code_ok

def get_best_stcok(stock_data, ok_stock, ss=0, gap=30, ma_value=5, filter_rate=0.1, ma_value_1=20, codes=[]):
    stock_name = get_stock_name()
    print("\n")
    code_90 = []
    # stock_industry, industry_stock, _, _ = get_stock_info('shenwan')
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    with open('mo-%s.txt'%time_format, 'a', encoding='utf8') as f:
        f.write('========\n')
        for code in ok_stock:
            data = stock_data[code]
            length = len(data)
            close = data.loc[ss:gap + ss, 'close'].tolist()
            high = data.loc[ss:gap + ss, 'high'].tolist()
            open_ = data.loc[ss:gap + ss, 'open'].tolist()
            ma = data.loc[ss:gap + ss, 'ma' + str(ma_value)].tolist()
            ma1 = data.loc[ss:gap + ss, 'ma' + str(ma_value_1)].tolist()
            # ma5 = data.loc[ss : ss + gap, 'ma5'].tolist()
            # if close[-1] < ma5[-1] or close[-1] < ma10[-1]:
            #     continue
            up = 0
            down = 0
            sumDay = len(ma)
            name = stock_name[code]
            # if name.lower().find('st') != -1:
            #     continue
            for i in range(sumDay):
                if close[i] < ma[i]:
                    down += 1
                else:
                    up += 1
            try:
                # close[0] / close[5] < 1.02 or \
                if close[0] < open_[0] or close[0] < close[1] or \
                        data.loc[ss, 'close'] / data.loc[ss + 10, 'close'] < 1.04 or \
                        data.loc[ss, 'close']  / data.loc[ss + 20, 'close'] < 1.08 or \
                        close[0] - open_[0] < (high[0] - close[0]) or \
                        stock_name[code].find('ST') != -1:
                    continue
            except KeyError as e:
                continue
            except IndexError as e:
                continue
            if down < sumDay * filter_rate:  # and (high[0] - close[0])*2 < (close[0] - open[0]) and close[0]>open[0]:
                try:
                    if daily_basic.at[code, 'turnover_rate_f'] < 4:
                        continue
                    if daily_basic.at[code, 'total_mv'] < 500000:
                        continue
                    # try:
                    #     if daily_basic.at[code, 'pe'] < 1 or daily_basic.at[code, 'pe'] > 200:
                    #         continue
                    # except Exception as e:
                    #     continue
                except KeyError as e:
                    pass
                if ss > 0:
                    if close[0] < data.loc[ss - 1, 'close']:
                        shot = '[==]'
                    else:
                        shot = '[~~]'
                    # if field_avg[stock_industry[code]] < 0:
                    #     continue

                    f.write("【%s】 [%s: %s] %s:%s  上：%s, 下:%s, close:%s, nextClose:%s %s Count:%s\n"
                          % (data.loc[ss, 'trade_date'], code, name,
                             stock_industry[code], field_avg[stock_industry[code]],
                             up, down,
                             close[0], data.loc[ss - 1, 'close'], shot, all_code_filter.count(code)))
                else:
                    f.write("【%s】 [%s: %s] %s:%s  上：%s, 下:%s, close:%s, Count:%s\n" % (
                        data.loc[ss, 'trade_date'],
                        stock_industry[code], field_avg[stock_industry[code]],
                        code, name,
                         up, down, close[0],
                        all_code_filter.count(code)))
                code_90.append(code)


        # elif down < sumDay * 0.2 and (high[0] - close[0])*3 < (close[0] - open[0]) and close[0]>open[0]:
        #     if ss > 0:
        #         print("80per > ma10 【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s。 【%s】" % (
        #         code, name, up, down, close[-1], data.loc[ss-1, 'close'], data.loc[ss,'trade_date']))
        #     else:
        #         print("80per > ma10 【%s:%s】，上：%s, 下:%s, close:%s。 【%s】"
        #               % (code, name, up, down, close[-1], data.loc[ss,'trade_date']))
    return code_90

def test(stock_data, ok_stock, ss=0, money = 10000):
    stock_name = get_stock_name()
    if ss < 1:
        print("不行的")
        return
    for code in ok_stock:
        if stock_name[code].find('ST') != -1:
            continue
        data = stock_data[code]
        close = data.loc[ss, 'close']
        next_close = data.loc[ss -1 , 'close']
        buy_amount = (10000 // (close * 100)) * 100
        if buy_amount < 100:
            buy_amount = 100
        money -= buy_amount * close
        money += buy_amount * next_close
    return money


# def summary_up_rules():
#     stock_name = get_stock_name()
#     length = len(stock_data['000001.SZ'])
#     keep = 5
#     gap = 30
#     for target in range(gap + 20, length - keep, keep):
#         for code in ok_stock:
#             data = stock_data[code]
#             close = data.loc[ss : ss + gap, 'close'].tolist()
#             open = data.loc[ss : ss + gap, 'open'].tolist()
#             ma10 = data.loc[ss : ss + gap, 'ma5'].tolist()
#             ma5 = data.loc[ss : ss + gap, 'ma5'].tolist()



def real_time_stock(filed_show=True, stocks_show=True):
    stock_industry, industry_stock = get_stock_info('industry')
    existStock = [x[:9] for x in os.listdir('stock') if x[0]!='3' or x[:3]!='688' or x.find('DS_Store')!=-1]
    datas = {}
    for e in existStock:
        code = e
        try:
            data = pd.read_csv('stock/%s.csv' % e)
        except Exception as x:
            continue
        try:
            newestData = data.iloc[0, :]
            newestData['ma20'] = round((data.loc[0, 'ma20'] * 20 - data.loc[19, 'close'])/19, 4)
            datas[code] = newestData
        except Exception as x:
            continue
    breaks = []
    count = 0
    while True:
        price_nows = qo.stocks([i[:6] for i in existStock])
        if count % 5 == 0 and filed_show:
            field_avg = get_industry_avg_real(price_nows, industry_stock)
            for i in field_avg.keys():
                print("板块：【%s】当前平均涨幅为：%s"%(i, field_avg[i]*100))
        count += 1
        if not stocks_show:
            continue
        for e in datas.keys():
            code = e
            price_now = price_nows[e[:6]]['now']
            price_open = price_nows[e[:6]]['open']
            pre_close = price_nows[e[:6]]['close']
            data = datas[code]
            ma20 = (price_now + data['ma20'] * 19) / 20
            if (price_open < ma20 and price_now >= ma20)\
                    or (pre_close < ma20 and price_now >= ma20) :
                s = "%s - %s突破20日线，可关注, 昨收[%s] 开盘[%s]  现价[%s] MA20[%s]\n" % ( stock_name[e], e,
                         pre_close, price_open, price_now, round(ma20, 3))
                if s not in breaks:
                    breaks.append(s)
                    print(s)

        # print("\r %s"%lines, end='')
        time.sleep(5)


if __name__ == '__main__':
    df = get_daily_basic('20210609')
    df.set_index(['ts_code'], inplace=True)
    # niceCode = get_best_stcok(0)
    # stock_name = get_stock_name()

    ##################
    # data = pd.read_csv('stock/600036.SH.csv')
    # data['alpha_ma5'] = data['ma5'] / data['close']
    # data['alpha_ma20'] = data['ma20'] / data['close']
    # data['alpha_ma50'] = data['ma50'] / data['close']
    # data['alpha_ma_v_5'] = data['ma_v_5'] / data['vol']
    # data['alpha_ma_v_20'] = data['ma_v_20'] / data['vol']
    # data['alpha_ma_v_50'] = data['ma_v_50'] / data['vol']
    #
    # # print(data.head())
    # length = len(data)
    # data = data.loc[1:length - 51 ,:]
    # predict = data.iloc[0,:]
    # model = nerual_(data, code='600036.SH', evaluate_data=predict)
    # model.train()
    # model.evaluate()
    ##################

    # for code in niceCode:
    #     if df.loc[code, 'total_mv'] > 1000000:
    #         print("niceMount:%s"%stock_name[code])
    #
    ##################

    # real_time_stock(filed_show=False)
    ##################
    daily_basic = get_daily_basic()
    daily_basic.set_index(['ts_code'], inplace=True)
    # time_format = 'weekly'
    time_format = 'daily'
    niceCode={}
    os.system('rm mo-%s.txt'%time_format)
    os.system('rm awei-%s.txt'%time_format)
    os.system('rm -rf stock_%ss'%time_format)
    stock_data, ok_stock = all_stock()
    all_code_filter = []
    for i in range(20, -1, -1):
        if time_format == 'weekly':
            code_filter = get_best_stcok(stock_data, ok_stock, i, 5, ma_value=3, ma_value_1=10, filter_rate=0.15, codes = all_code_filter)
        else:
            # get_best_stcok_by_vol(stock_data, ok_stock, i, 40, ma_value=5, ma_value_1=10)
            code_filter = get_best_stcok(stock_data, ok_stock, i, 6, ma_value=5, ma_value_1=10, filter_rate=0.1, codes = all_code_filter)
        all_code_filter += code_filter
    # get_best_stcok_by_ma(stock_data, ok_stock, 0, 0, ma_value=3, ma_value_1=10)

    get_best_stcok_by_awei(stock_data, ok_stock, 0, 5, ma_value=3, ma_value_1=10, )

    # c = get_best_stcok_by_obv(stock_data, ok_stock, 7, 40, ma_value=10, filter_rate=0.2)
    # print('========')
    # x = get_best_stcok(stock_data, ok_stock, 7, 10, ma_value=5, filter_rate=0.2)
    # for cc in c:
    #     if cc in x:
    #         print(cc,' is Good, check It')


    # print("====")
    # d = get_best_stcok(stock_data, ok_stock, 0, 10, ma_value=10)
    # for code in c:
    #     if code in d:
    #         print(code)
    ##################

        # money = test(stock_data, c, i, money)
        # print(money)
    # for i in niceCode.keys():
    #     try:
    #         if df.loc[i,'total_mv'] > 1000000 and niceCode[i] > 5:
    #             print("Name:%s Times:%s Vol:%s"%(stock_name[i], niceCode[i], df.loc[i,'total_mv']))
    #     except KeyError as x:
    #         print(x)
    ##################

    # data = pd.read_csv('stock/600036.SH.csv')
    # code = '600036.SH'
    # stock_data, ok_stock = all_stock()
    # n_p = {}
    # for code in ok_stock:
    #     n_p = ngram(stock_data[code], code, n_p)
    #
