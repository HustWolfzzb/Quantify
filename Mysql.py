from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import time
import random
import tushare as ts
import datetime
from sqlalchemy import create_engine

import matplotlib.pyplot as plt
import pandas as pd
import tushare as ts
from scipy.stats import spearmanr

import pymysql
keys = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']


def executeSQL(connect, conn, strs, query=False):

    if isinstance(strs, list):
        for str in strs:
            conn.execute(str)
    else:
        try:
            conn.execute(strs)
        except AttributeError as ae:
            print(ae)
            return
    connect.commit()
    if query:
        results = conn.fetchone()
        return results



def connectSQL():
    connect = pymysql.connect(  # 连接数据库服务器
        user="root",
        password="zzb162122",
        host="127.0.0.1",
        port=3306,
        db="STOCK",
        charset="utf8"
    )
    conn = connect.cursor()
    return connect, conn


def closeSQL( connect, conn):
    conn.close()
    connect.close()



def get_stcokName():
    df = ts.get_stock_basics()
    df.to_excel('stockName.xlsx')

def ts_getData(code = '600355', start = "2000-01-01", end = "2020-07-15" ):
    """
    ------
      code:string
                  股票代码 e.g. 600848
      start:string
                  开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
      end:string
                  结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
      ktype：string
                  数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
      retry_count : int, 默认 3
                 如遇网络等问题重复执行的次数
      pause : int, 默认 0
                重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    return
    -------
      DataFrame
          属性:日期 ，开盘价， 最高价， 收盘价， 最低价， 成交量， 价格变动 ，涨跌幅，5日均价，10日均价，20日均价，5日均量，10日均量，20日均量，换手率
    """
    df = ts.get_hist_data(code, start, end, ktype='D')
    # print(df.columns)
    # df.columns=["开盘价","最高价","收盘价","最低价","成交量","价格变动","涨跌幅","5日均价","10日均价","20日均价","5日均量","10日均量","20日均量"]
    # print(df['开盘价'])
    return df

def saveData(dataframe, code):
    # engine = create_engine('mysql+pymysql://root:zzb162122@localhost:3306/STOCK', encoding='utf8')
    connect, conn = connectSQL()
    # executeSQL(connect, conn, 'drop table if exists `%s`;'%code)
    # sql_createTb = "CREATE TABLE `" + code + """`  (
    #                     `TIME` date	 NOT NULL,
    #                     `open`            FLOAT,
    #                     `high`            FLOAT,
    #                     `close`           FLOAT,
    #                     `low`             FLOAT,
    #                     `volume`          FLOAT,
    #                     `price_change`    FLOAT,
    #                     `p_change`        FLOAT,
    #                     `ma5`             FLOAT,
    #                     `ma10`            FLOAT,
    #                     `ma20`            FLOAT,
    #                     `v_ma5`           FLOAT,
    #                     `v_ma10`          FLOAT,
    #                     `v_ma20`          FLOAT,
    #                     PRIMARY KEY(TIME)  )
    #                  """
    # executeSQL(connect, conn, sql_createTb)
    insertSQL = []
    if dataframe.index == None:
        return
    for idx in dataframe.index:
        string = "insert into `%s`(TIME, "%code
        for x in keys[:-1]:
            string += (x + ', ')
        string += keys[-1] + ") values( '%s', "%idx
        for key in keys[:-1]:
            string += (str(dataframe.at[idx, key]) + ', ')
        string += str(dataframe.at[idx, keys[-1]]) + ');'
        insertSQL.append(string)
    # print(insertSQL[10])
    executeSQL(connect, conn, insertSQL)
    closeSQL(connect, conn)

def updateData(code):
    connect, conn = connectSQL()
    getDateSQL = "select TIME from `" + code +"` order by TIME desc limit 1;"
    lastestDate = executeSQL(connect, conn, getDateSQL, query=True)[0]
    # print(lastestDate)
    dataframe = ts_getData(code, str(lastestDate), str(datetime.date.today().isoformat()) )
    insertSQL = []
    for idx in dataframe.index[:-1]:
        string = "insert into `%s`(TIME, " % code
        for x in keys[:-1]:
            string += (x + ', ')
        string += keys[-1] + ") values( '%s', " % idx
        for key in keys[:-1]:
            string += (str(dataframe.at[idx, key]) + ', ')
        string += str(dataframe.at[idx, keys[-1]]) + ') ON DUPLICATE KEY UPDATE;'
        insertSQL.append(string)
    # print(insertSQL[10])
    executeSQL(connect, conn, insertSQL)
    closeSQL(connect, conn)

def readData(code):
    engine = create_engine('sqlite:///stockHistory.db')
    dataframe = pd.read_sql(code, engine)
    return dataframe

def get_all_hushen_data(filename = 'stockName.xlsx'):
    df = pd.read_excel(filename)
    codestmp = df['code'].tolist()
    codes = []
    for i in codestmp:
        if len(str(i)) != 6:
            codes.append('0'*(6-len(str(i))) + str(i))
        else:
            codes.append(str(i))
    names = df['name'].tolist()
    count  = -1
    length = len(names)
    for code in codes:
        count += 1
        if count%100 == 0:
            print('[' + '=' * (count//100) + '>' + " "*((length-count)//100) + ']')
        try:
            df = ts_getData(code)
        except Exception as e:
            print("%s 这只股票有问题！"%code)
            continue
        try:
            if not df.empty:
                saveData(df, code)
        except AttributeError as e:
            print("在%s 没拉取成功"%code)
            continue

def update_all_hushen_data(graph):
    codestmp = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    codes = []
    for i in codestmp:
        if len(str(i)) != 6:
            codes.append('0'*(6-len(str(i))) + str(i))
        else:
            codes.append(str(i))
    count = -1
    length = len(codes)
    for code in codes:
        count += 1
        if count%100 == 0:
            print('[' + '=' * (count//100) + '>' + " "*((length-count)//100) + ']')
        try:
            updateData(code)
        except AttributeError as e:
            print("在%s 没拉取成功"%code)
        except pymysql.err.ProgrammingError as xe:
            print(xe)
            saveData(ts_getData(code), code)
        except Exception as e:
            print("%s 这只股票有问题"%code)
            continue


def spearman_cal(filename = 'stock-Change.txt', testFile = 'testFile.txt'):
    with open(testFile, 'r', encoding='utf8') as r:
        all_data = [float(x) for x in r.read().strip().split(" ")]
    test_data = all_data[:-1]
    actual = all_data[-1]
    chang = len(test_data)
    x = []
    for i in range(0, chang+1):
        x.append(i)
    niceStockName = []
    niceStockCode = []
    niceStockPredict = []
    count = -1
    length = 3751
    with open(filename, 'r', encoding='utf8') as file:
        for line in file.readlines():
            count += 1
            if count % 100 == 0:
                print('[' + '=' * (count // 100) + '>' + " " * ((length - count) // 100) + '%.2f]' % (count / length))
            line = line.strip()
            data = line.split(' ')
            name = data[0]
            code = data[1]
            change = data[2:]
            if len(change) < chang + 1:
                continue
            for i in range(len(change) - chang - 1):
                train_data = [float(x) for x in change[i:i+chang]]
                if spearmanr(test_data, train_data).correlation >= 0.96:
                    # print("%s 股票，（代码：%s）的趋势能对的上"%(name,code))
                    # print(test_data)
                    # print(change[i:i+chang])
                    # print("预测的内容是：%s, 实际变化是：%s"%(change[i + chang],actual))
                    niceStockName.append(name)
                    niceStockCode.append(code)
                    niceStockPredict.append(float(change[i+chang]))
                    # plt.title('Stock Nihe')
                    # plt.xlabel('date')
                    # plt.ylabel('change')
                    # plt.plot(x, test_data + [actual], 'r', label='test')
                    # plt.plot(x, train_data + [float(change[i+chang])], 'b', label='train')
                    # plt.show()
    plt.title('Stock Nihe')
    plt.xlabel('stock')
    plt.ylabel('predict')
    plt.plot([x for x in range(len(niceStockPredict))], niceStockPredict, 'r', label='predict')
    plt.plot([x for x in range(len(niceStockPredict))], [actual] * len(niceStockPredict), 'b', label='actual')
    plt.plot([x for x in range(len(niceStockPredict))], [0] * len(niceStockPredict), 'b', label='actual')
    plt.show()
    correct = 0
    print(niceStockPredict)
    for i in niceStockPredict:
        if i > 0 and actual > 0:
            correct += 1
    print("准确率在%f"% (correct/len(niceStockPredict)))



def processData(filename = 'stock-Change.txt', newFile = 'lmData.txt'):
    count = -1
    length = 3751
    with open(newFile, 'w', encoding='utf8') as out:
        with open(filename, 'r', encoding='utf8') as file:
            for line in file.readlines():
                count += 1
                if count % 100 == 0:
                    print('[' + '=' * (count // 100) + '>' + " " * ((length - count) // 100) + '%.2f]' % (count / length))
                line = line.strip()
                data = line.split(' ')
                change = data[2:]
                st = ""
                for i in change:
                    st += (str(round(float(i), 1)) + ' ')
                out.write(st.strip() + '\n')

def splitData(filename = 'lmData.txt', outputFile = ['ptb.train.txt', 'ptb.valid.txt', 'ptb.test.txt']):
    count = -1
    length = 3751
    data = open(filename, 'r', encoding='utf8')
    Data = data.readlines()
    data.close()
    trainData = Data[:length//10*6]
    validData = Data[length//10*6: length//10*8]
    testData = Data[length//10*8:]
    allData = [trainData, validData, testData]
    for newFile in outputFile:
        count += 1
        print('[' + '=' * (count * 33) + '>' + " " * ((3 - count) * 33) + '%.2f]' % (count / length))
        with open(newFile, 'w', encoding='utf8') as out:
            for i in allData[count]:
                for line in i:
                    out.write(line)


def checkFile(filename = 'stock-Change.txt'):
    with open(filename, 'r', encoding='utf8') as file:
        name = ''
        count  = 0
        for line in file.readlines():
            line = line.strip()
            data = line.split(' ')
            if data[0] != name:
                name = data[0]
                count += 1
                print("OK🙆 %d "%count)
            else:
                print("重合了：%s"%name)


def get_all_hist_data_by_pro():
    pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    all_data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    ts_code = list(all_data.ts_code)
    symbol = list(all_data.symbol)
    connect, conn = connectSQL()
    index_in_here = ['open', 'high', 'low', 'close', 'change', 'pct_chg', 'vol', ]
    index_in_mysql = ['open', 'high', 'low', 'close', 'price_change', 'p_change', 'volume']
    insertSQL = []

    for idx in all_data.index:
        try:
            getDateSQL = "select TIME from `" + symbol[idx] + "` order by TIME desc limit 1;"
            lastestDate = executeSQL(connect, conn, getDateSQL, query=True)[0]
            # print(ts_code[idx], lastestDate)
            data = pro.daily(ts_code=ts_code[idx], start_date='2010-01-04', end_date=str(lastestDate))
            time.sleep(0.12)
            date = str(data.at[idx, 'trade_date'])
            date = date[:4] + '-' + date[4:6]  + '-' + date[6:]
            string = "insert into `%s`(TIME, " % date
            for x in index_in_mysql[:-1]:
                string += (x + ', ')
            string += index_in_mysql[-1] + ") values( '%s', " % idx
            for key in index_in_here[:-1]:
                string += (str(data.at[idx, key]) + ', ')
            string += str(data.at[idx, index_in_here[-1]]) + ');'
            insertSQL.append(string)
        except Exception as e:
            print(ts_code[idx], e)
            continue
    executeSQL(connect, conn, insertSQL)
    closeSQL(connect, conn)


if __name__ == '__main__':
    # data = ts_getData('399106')
    # print(data)
    # saveData(data, '600228')
    # updateData('000018')
    # get_all_hushen_data()
    graph = Graph('http://localhost:7474', username='neo4j', password='zzb162122')
    # update_all_hushen_data(graph)
    get_all_hist_data_by_pro()