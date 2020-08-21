from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import time

import datetime

import matplotlib.pyplot as plt
import pandas as pd
from Data import get_hist_data, get_pro_daily, get_pro_stock_basic

import pymysql
keys = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']


def executeSQL(connect, conn, strs, query=False):
    try:
        if isinstance(strs, list):
            for str in strs:
                conn.execute(str)
        else:

                conn.execute(strs)
    except AttributeError as ae:
        print(ae)
        return
    connect.commit()
    if query:
        results = conn.fetchall()
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


def createTable(code):
    connect, conn = connectSQL()
    sql_createTb = "CREATE TABLE `" + code + """`  (
                        `TIME` date	 NOT NULL,
                        `open`            FLOAT,
                        `high`            FLOAT,
                        `close`           FLOAT,
                        `low`             FLOAT,
                        `volume`          FLOAT,
                        `price_change`    FLOAT,
                        `p_change`        FLOAT,
                        `ma5`             FLOAT,
                        `ma10`            FLOAT,
                        `ma20`            FLOAT,
                        `v_ma5`           FLOAT,
                        `v_ma10`          FLOAT,
                        `v_ma20`          FLOAT,
                        PRIMARY KEY(TIME)  )
                     """
    executeSQL(connect, conn, sql_createTb)
    print("Create Table %s"%code)
    closeSQL(connect, conn)


def saveData(dataframe, code):
    # engine = create_engine('mysql+pymysql://root:zzb162122@localhost:3306/STOCK', encoding='utf8')
    connect, conn = connectSQL()
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

connect, conn = connectSQL()
existTables = [ x[0] for x in list(executeSQL(connect, conn, 'show tables;', True)) ]

def updateData(code):
    try:
        connect, conn = connectSQL()
        if code not in existTables:
            return
            createTable(code)
        getDateSQL = "select TIME from `" + code +"` order by TIME desc limit 1;"
        lastestDate = executeSQL(connect, conn, getDateSQL, query=True)[0][0].isoformat()
        if len(lastestDate) < 10:
            lastestDate = '2010-01-01'
        # print(lastestDate)
        dataframe = get_hist_data(code, str(lastestDate), str(datetime.date.today().isoformat()) )
        insertSQL = []
        for idx in dataframe.index[:-1]:
            string = "insert ignore into `%s`(TIME, " % code
            for x in keys[:-1]:
                string += (x + ', ')
            string += keys[-1] + ") values( '%s', " % idx
            for key in keys[:-1]:
                string += (str(dataframe.at[idx, key]) + ', ')
            string += str(dataframe.at[idx, keys[-1]]) + ') ;'
            insertSQL.append(string)
        # print(insertSQL[10])
        executeSQL(connect, conn, insertSQL)
        closeSQL(connect, conn)
    except Exception as e:
        print(e)

def get_all_stock_symbol():
    existTables = [x[0] for x in list(executeSQL(connect, conn, 'show tables;', True))]
    return existTables

def get_all_hushen_data(filename = 'stockName.xlsx'):
    df = get_pro_stock_basic()
    symbol = df['symbol'].tolist()
    names = df['name'].tolist()
    count = -1
    length = len(names)
    for code in symbol:
        count += 1
        if count%100 == 0:
            print('[' + '=' * (count//100) + '>' + " "*((length-count)//100) + ']')
        try:
            df = get_hist_data(code)
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
    codes = list(get_pro_stock_basic()['symbol'])
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
            saveData(get_hist_data(code),code)
        except Exception as e:
            print("%s 这只股票有问题"%code)
            continue

def get_all_columns_with_label(label, existTables = []):
    if len(existTables) == 0:
        existTables =[x[0] for x in list(executeSQL(connect, conn, 'show tables;', True))]
    stock_hist_label = {}
    for table in existTables:
        if table.find('300') == 0:
            continue
        getColumnSQL = "select " + label + " from `" + table + "` order by TIME;"
        stock_hist_label[table] = [x[0] for x in list(executeSQL(connect, conn, getColumnSQL, True))]
    return stock_hist_label

def get_all_hist_data_by_pro():
    all_data = get_pro_stock_basic()
    ts_code = list(all_data.ts_code)
    symbol = list(all_data.symbol)
    connect, conn = connectSQL()
    index_in_here = ['open', 'high', 'low', 'close', 'change', 'pct_chg', 'vol', ]
    index_in_mysql = ['open', 'high', 'low', 'close', 'price_change', 'p_change', 'volume']
    insertSQL = []
    count = 0
    existTables =[x[0] for x in list(executeSQL(connect, conn, 'show tables;', True))]
    not_in_mysql_symbols = [x for x in symbol if x not in existTables]
    for code in not_in_mysql_symbols:
        if code not in existTables:
            createTable(code)
    for idx in all_data.index:
        if count%100 == 0:
            print("Finish %s/%s Stock~ "%(count, len(symbol)))
        count += 1
        # try:
        getDateSQL = "select TIME from `" + symbol[idx] + "` order by TIME limit 1;"
        try:
            lastestDate = executeSQL(connect, conn, getDateSQL, query=True)[0][0].isoformat()
        except IndexError as e:
            lastestDate =  str(datetime.date.today().isoformat())
        # print(ts_code[idx], lastestDate)
        data = get_pro_daily(ts_code=ts_code[idx], start_date='2010-01-04', end_date=str(lastestDate))
        time.sleep(0.12)
        for x in data.index:
            date = str(data.at[x, 'trade_date'])
            date = date[:4] + '-' + date[4:6]  + '-' + date[6:]
            string = "insert ignore into `%s`(TIME, " % (symbol[idx])
            for ss in index_in_mysql[:-1]:
                string += (ss + ', ')
            string += index_in_mysql[-1] + ") values( '%s', " % date
            for key in index_in_here[:-1]:
                string += (str(data.at[x, key]) + ', ')
            string += str(data.at[x, index_in_here[-1]]) + ');'
            insertSQL.append(string)
        # except KeyError as e:
        #     print("Error!", ts_code[idx], e)
        #     continue
    executeSQL(connect, conn, insertSQL)
    closeSQL(connect, conn)


if __name__ == '__main__':
    # graph_data = ts_getData('399106')
    # print(graph_data)
    # saveData(graph_data, '600228')
    # updateData('000018')
    # get_all_hushen_data()
    graph = Graph('http://localhost:11003', username='neo4j', password='zzb162122')
    update_all_hushen_data(graph)
    # get_all_hist_data_by_pro()
