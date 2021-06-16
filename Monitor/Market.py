import os
import time
from DataEngine.Data import pro, get_pro_stock_basic, get_concept, get_index_basic, \
    get_stock_concepts, get_index_weight, get_index, get_stock_name, get_daily_basic,\
    get_stock_daily, qo
from Strategy.follow_fund import get_Date_base_gap
from Feature.pre_process_data import process_data
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


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

def all_stock():
    stocks = get_pro_stock_basic()['ts_code'].tolist()
    new_stocks = []
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
    if not os.path.exists('stock'):
        os.makedirs('stock')
    existStock = os.listdir('stock')
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
                df = get_stock_daily(ts_code=code, start_date=ago, end_date=today)
                if len(df) < 80:
                    count += 1
                    continue
                df.to_csv('stock/%s.csv' % code, index=False)
                # print( code+'.csv' +" not in stock!")
            else:
                df = pd.read_csv('stock/%s.csv'%code)
                # count += 1
                # print( code+'.csv' +" in stock!")
            if len(df)<10:
                print( code+'.csv' +" not long enough!")
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
                time.sleep(61)
    return stock_data, ok_stock


def get_best_stcok(stock_data, ok_stock, ss=0, gap= 30):
    stock_name = get_stock_name()
    print("\n")
    code_90 = []
    code_80 = []
    for code in ok_stock[:100]:
        data = stock_data[code]
        length = len(data)
        target = length - ss
        close = data.loc[0:gap, 'close'].tolist()
        open = data.loc[0:gap, 'open'].tolist()
        ma = data.loc[0:gap, 'ma20'].tolist()
        # ma5 = data.loc[target - gap:target, 'ma5'].tolist()
        # if close[-1] < ma5[-1] or close[-1] < ma10[-1]:
        #     continue
        up = 0
        down = 0
        sumDay = len(ma)
        name = stock_name[code]
        # if name.lower().find('st') != -1:
        #     continue
        for i in range(sumDay):
            if close[i] < ma[i] or open[i] < ma[i]:
                down += 1
            else:
                up += 1
        if down < sumDay * 0.1:
            if ss > 0:
                print("90per > ma10 【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s" % (code, name, up, down, close[0], data.loc[target, 'close']))
            else:
                print("90per > ma10 【%s:%s】，上：%s, 下:%s, close:%s" % (code, name, up, down, close[0]))
            code_90.append(code)

        # elif down < sumDay * 0.2:
        #     if ss > 0:
        #         print("80per > ma10 【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s" % (
        #         code, name, up, down, close[-1], data.loc[target, 'close']))
        #     else:
        #         print("80per > ma10 【%s:%s】，上：%s, 下:%s, close:%s" % (code, name, up, down, close[-1]))
    return code_90

def test():
    stock_name = get_stock_name()
    length = len(stock_data['000001.SZ'])
    earn80 = 1000000
    earn90 = 1000000
    keep = 5
    gap = 30
    for target in range(gap + 20, length-keep, keep):
        for code in ok_stock:
            data = stock_data[code]
            close = data.loc[target - gap:target, 'close'].tolist()
            open = data.loc[target - gap:target, 'open'].tolist()
            ma10 = data.loc[target - gap:target, 'ma10'].tolist()
            ma5 = data.loc[target - gap:target, 'ma5'].tolist()
            if close[-1] < ma5[-1] or close[-1] < ma10[-1]:
                continue
            up = 0
            down = 0
            sumDay = len(ma10)
            name = stock_name[code]
            for i in range(sumDay):
                if close[i] < ma10[i] or open[i] < ma10[i]:
                    down += 1
                else:
                    up += 1
            if down < sumDay * 0.1:
                # print("\n90per > ma10 【%s:%s】，上：%s, 下:%s, close:%s, sell_price:%s" % (code, name, up, down, close[-1], data.loc[target+1, 'close']))
                if close[-1]>100:
                    earn90 += (data.loc[target + keep, 'close'] - close[-1] )*100
                else:
                    amount = int( 10000 / ( close[-1]*100) ) * 100
                    earn90 += (data.loc[target + keep, 'close'] - close[-1] )*amount

            elif down < sumDay * 0.2:
                # print("80per > ma10【%s:%s】，上：%s, 下:%s" % (code, name, up, down))
                if close[-1]>100:
                    earn80 += (data.loc[target + keep, 'close'] - close[-1] )*100
                else:
                    amount = int( 10000 / ( close[-1]*100) ) * 100
                    earn80 += (data.loc[target + keep, 'close'] - close[-1] )*amount
    print("\nper80初始资金100w，现在:%s\nper90初始资金100w，现在:%s" % (round(earn80), round(earn90)))


def summary_up_rules():
    stock_name = get_stock_name()
    length = len(stock_data['000001.SZ'])
    keep = 5
    gap = 30
    for target in range(gap + 20, length - keep, keep):
        for code in ok_stock:
            data = stock_data[code]
            close = data.loc[target - gap:target, 'close'].tolist()
            open = data.loc[target - gap:target, 'open'].tolist()
            ma10 = data.loc[target - gap:target, 'ma5'].tolist()
            ma5 = data.loc[target - gap:target, 'ma5'].tolist()



def real_time_stock():
    existStock = [x[:9] for x in os.listdir('stock') if x[0]!='3' or x[:3]!='688']
    datas = {}
    for e in existStock:
        code = e
        data = pd.read_csv('stock/%s.csv' % e)
        try:
            newestData = data.iloc[0, :]
            newestData['ma20'] = round((data.loc[0, 'ma20'] * 20 - data.loc[19, 'close'])/19, 4)
            datas[code] = newestData
        except Exception as x:
            continue
    breaks = []
    while True:
        price_nows = qo.stocks([i[:6] for i in existStock])
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
        time.sleep(10)


if __name__ == '__main__':
    df = get_daily_basic('20210609')
    df.set_index(['ts_code'], inplace=True)
    # niceCode = get_best_stcok(0)
    stock_name = get_stock_name()
    # for code in niceCode:
    #     if df.loc[code, 'total_mv'] > 1000000:
    #         print("niceMount:%s"%stock_name[code])
    #
    # real_time_stock()

    niceCode={}
    stock_data, ok_stock = all_stock()
    for i in range(1):
         c = get_best_stcok(stock_data, ok_stock, i, 20)
         for code in c:
            if not niceCode.get(code):
                niceCode[code] = 1
            else:
                niceCode[code] += 1
    for i in niceCode.keys():
        try:
            if df.loc[i,'total_mv'] > 1000000 and niceCode[i] > 5:
                print("Name:%s Times:%s Vol:%s"%(stock_name[i], niceCode[i], df.loc[i,'total_mv']))
        except KeyError as x:
            print(x)