import os
import random
import time
from DataEngine.Data import pro, get_pro_stock_basic, get_concept, get_index_basic, \
    get_stock_concepts, get_index_weight, get_index, get_stock_name, get_daily_basic,\
    get_stock_daily, qo
from Strategy.follow_fund import get_Date_base_gap
from Feature.pre_process_data import process_data
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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

def get_stock_info(field='industry'):
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

def get_industry_avg(stock_data, filed_stock, ss):
    field_avg = {}
    for field in filed_stock.keys():
        stocks =  filed_stock[field]
        avg = []
        for code in stocks:
            if code not in stock_data.keys():
                continue
            data = stock_data[code]
            avg.append(data.loc[ss, 'pct_chg'])
        field_avg[field] = round(sum(avg)/len(avg),3)
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


def get_best_stcok(stock_data, ok_stock, ss=0, gap = 30, ma_value=5, filter_rate = 0.1):
    stock_name = get_stock_name()
    print("\n")
    code_90 = []
    code_80 = []
    stock_industry, industry_stock = get_stock_info('industry')
    field_avg = get_industry_avg(stock_data, industry_stock, ss)
    for code in ok_stock:
        data = stock_data[code]
        length = len(data)
        close = data.loc[ss:gap+ss, 'close'].tolist()
        high = data.loc[ss:gap+ss, 'high'].tolist()
        open = data.loc[ss:gap+ss, 'open'].tolist()
        ma = data.loc[ss:gap+ss, 'ma'+str(ma_value)].tolist()
        ma1 = data.loc[ss:gap+ss, 'ma20'].tolist()
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
            if close[i] < ma[i] or open[i] < ma[i]:
                down += 1
            else:
                up += 1
        if down < sumDay * filter_rate :# and (high[0] - close[0])*2 < (close[0] - open[0]) and close[0]>open[0]:
            if ss > 0:
                print("【%s:%s】，上：%s, 下:%s, close:%s, nextClose:%s。 【%s】"
                      % (code, name, up, down, close[0], data.loc[ss-1, 'close'], data.loc[ss,'trade_date']))
            else:
                print("[%s:%s]【%s:%s】，上：%s, 下:%s, close:%s。【%s】" % (
                    stock_industry[code], field_avg[stock_industry[code]],
                     code, name, up, down, close[0], data.loc[ss,'trade_date']))
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

import tensorflow as tf

class nerual_:
    def __init__(self, data, code, evaluate_data,
                 cols=['alpha_ma5', 'alpha_ma20', 'alpha_ma50', 'alpha_ma_v_5', 'alpha_ma_v_20', 'alpha_ma_v_50' ]):
        self.data = data
        self.cols = cols
        self.evaluate_data = evaluate_data
        self.evaluate_target = evaluate_data
        self.target = data['pct_chg'].tolist()
        self.feature = len(self.cols)
        self.batch_size = 200
        self.epoch = 1000
        self.code = code
        self.trained = False
        self.init()

    def get_batch(self, batch_size=100):
        loc = []
        for i in range(batch_size):
            loc.append(random.randint(1, len(self.data) - 1))
        X_re = []
        y_re = []
        for i in loc:
            X_re.append(self.data.loc[:, self.cols].loc[i,:].tolist())
            y_re.append(self.target[i])
        return np.array(X_re), np.array(y_re)

    def evaluate(self):
        X = [self.data.loc[0, self.cols].tolist()]
        Y = [[self.data.loc[0, 'pct_chg']]]
        with tf.Session() as sess:
            feed_dict = {
                self.x: X,
                self.y: Y,
            }
            pridict, _ = sess.run([self.output], feed_dict=feed_dict)
            print("预测明天的涨幅为：%s")

    def init(self):
        self.x = tf.placeholder(tf.float32, [None, 6])
        self.y = tf.placeholder(tf.float32, [None])
        # X->hidden_layer
        self.w1 = tf.Variable(tf.random_uniform([6, 25], 0, 1))
        self.b1 = tf.Variable(tf.random_uniform([25], 0, 1))
        self.out_put_hidden1 = tf.matmul(self.x, self.w1) + self.b1
        # self.out_put_1 = tf.reduce_mean(self.out_put_hidden1, 1, keep_dims=False)
        self.layer1 = tf.nn.sigmoid(self.out_put_hidden1) # 激励函数
        # # hidden_layer->output
        self.w2 = tf.Variable(tf.random_uniform([25,1],0,1))
        self.b2 = tf.Variable(tf.random_uniform([1],0,1))
        self.output = tf.matmul(self.layer1, self.w2) + self.b2
        # # down = tf.reshape(y - output, [-1,1])
        # layer2 = tf.nn.relu(output)
        # layer2 = y-output
        self.loss = tf.reduce_sum(self.output - self.y)  # y为真实数据， layer2为网络预测结果
        # loss1 = tf.reduce_sum(loss, 1, keep_dims=False)

    def train(self):
        self.saver = tf.train.Saver()
        with tf.Session() as sess:
            start = time.clock()
            saver_add = 'model/%s/' % self.code
            if not self.trained:
                sess.run(tf.global_variables_initializer())
            else:
                self.saver.restore(sess, saver_add + 'model.ckpt')
            self.train_op = tf.train.GradientDescentOptimizer(0.01).minimize(self.loss)
            for i in range(self.epoch):
                X, Y = self.get_batch(self.batch_size)
                # print(X.shape)
                # print(Y.shape)
                feed_dict = {
                    self.x : X,
                    self.y :Y,
                }
                loss,_ = sess.run([self.loss, self.train_op], feed_dict=feed_dict)
                if i % 100 == 0:
                    try:
                        os.makedirs(saver_add)
                    except:
                        pass
                    self.saver.save(sess, saver_add + 'model.ckpt')
                if i % 10 == 0:
                    print("LOSS:%s, EPOCH:%s"%(loss, i))

    def loadModel(self):
        self.trained = True



def ngram(data, code, ngram_probability):
    data['alpha_ma5'] = data['ma5'] / data['close']
    data['alpha_ma10'] = data['ma10'] / data['close']
    data['alpha_ma20'] = data['ma20'] / data['close']
    data['alpha_ma50'] = data['ma50'] / data['close']
    data['alpha_ma_v_5'] = data['ma_v_5'] / data['vol']
    data['alpha_ma_v_10'] = data['ma_v_10'] / data['vol']
    data['alpha_ma_v_20'] = data['ma_v_20'] / data['vol']
    data['alpha_ma_v_50'] = data['ma_v_50'] / data['vol']
    data['zhangdie'] =  data['pct_chg']/10 + 1
    data = data.fillna(0)
    cols = ['alpha_ma5', 'alpha_ma10', 'alpha_ma20', 'alpha_ma50', 'alpha_ma_v_5', 'alpha_ma_v_10', 'alpha_ma_v_20', 'alpha_ma_v_50', 'zhangdie']
    if not os.path.exists('ngram_prob'):
        os.makedirs('ngram_prob')
    existStock = os.listdir('ngram_prob')
    choose_col = cols[1]
    col_data = data.loc[:, choose_col].to_list()
    pct_chg = data.loc[:, 'pct_chg'].to_list()
    print("length:%s"%len(col_data))
    bit = 2
    ma = 5
    for i in range(1,len(col_data)-5):
        ngram = "-".join([str(round(x , bit)) for x in col_data[i:i+5]])
        #print(ngram)
        target = round(pct_chg[i-1], 0)
        if not ngram_probability.get(ngram):
            ngram_probability[ngram] = {target:1}
        else:
            if not ngram_probability[ngram].get(target):
                ngram_probability[ngram][target] = 1
            else:
                ngram_probability[ngram][target] += 1
    today_ngram = "-".join([str(round(x , bit)) for x in col_data[0:5]])
    try:
        print("今天的Ngram为",  today_ngram, '\n其对应的可能涨跌为：%s', ngram_probability[today_ngram])
    except Exception as e:
        print(e)
        pass
    # print(ngram_probability)
    return ngram_probability

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

    niceCode={}
    stock_data, ok_stock = all_stock()
    # money = 1000000
    #
    c = get_best_stcok(stock_data, ok_stock, 0, 30, ma_value=20, filter_rate=0.15)

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
