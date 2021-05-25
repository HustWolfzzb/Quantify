import os
import time
from DataEngine.Data import pro, get_pro_stock_basic, get_concept, get_index_basic, \
    get_stock_concepts, get_index_weight, get_index, get_stock_name
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
        if idx[0]==3 or idx[:3] == '688':
            continue
        else:
            new_stocks.append(idx)
    stocks = new_stocks
    today, ago = get_Date_base_gap(0, 200)
    count = 0
    length = len(stocks)
    # length = 100
    existStock = os.listdir('stock')
    stock_data = {}
    while count < length:
        index = count
        if index % 100 == 0:
            print("\r【%s%s/%s%s】" % ('>' * int(index * 100 // length), index , length, '=' * (100 - int(index * 100 // length))), end='')
        code = stocks[index]
        try:
            if code+'.csv' not in existStock:
                df,_ = process_data(code, ago, today)
                if len(df) == 0:
                    count += 1
                    continue
                df.to_csv('stock/%s.csv' % code, index=False)
                # print( code+'.csv' +" not in stock!")
            else:
                df = pd.read_csv('stock/%s.csv'%code)
                # print( code+'.csv' +" in stock!")
            if len(df)<10:
                print( code+'.csv' +" not long enough!")
                count += 1
                continue
            stock_data[code] = df
            count += 1
        except Exception as e:
            if str(e).find('not enough values to unpack') != -1:
                continue
            else:
                print(e)
                time.sleep(61)



if __name__ == '__main__':
    all_stock()


