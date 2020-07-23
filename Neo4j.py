import pandas as pd
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import tushare as ts
import datetime
import time


def createNode_1(graph, nodeFile):
    df = pd.read_csv(nodeFile, dtype=object)
    length = int(df.size/len(df.columns))
    for index in range(int(df.size/len(df.columns))):
        if index % int(length/10) == 0:
            print("Progress: %s / %s"%(index,length))
        # node = Node(df.at[index, ':LABEL'], stock_id = df.at[index, '股票代码:ID'], name = df.at[index, '股票名称'] )
        # node = Node(df.at[index, ':LABEL'], holder_id = df.at[index, 'Holder:ID'], name = df.at[index, '股东名称'])
        # node = Node(df.at[index, ':LABEL'], industry_id = df.at[index, 'Industry:ID'], name = df.at[index, '行业名称'])
        # node = Node(df.at[index, ':LABEL'], concept_id = df.at[index, 'ConceptId:ID'], name = df.at[index, '概念名称'] )
        # graph.create(node)



        # a = graph.nodes.match('人', person_id = df.at[index, ':START_ID']).first()
        a = graph.nodes.match('股东', holder_id = df.at[index, ':START_ID']).first()
        b = graph.nodes.match('股票', stock_id = df.at[index, ':END_ID']).first()
        #
        # b = graph.nodes.match('行业', industry_id = df.at[index, ':END_ID']).first()
        # b = graph.nodes.match('概念', concept_id = df.at[index, ':END_ID']).first()
        # a = graph.nodes.match('股票', stock_id = df.at[index, ':START_ID']).first()

        # properties = {'jobs': df.at[index, '职位']}
        r = Relationship(a, df.at[index, ':TYPE'], b)

        graph.create(r)


def createIndexNode(graph):
    data = ts.get_index()
    en2cn = {
            "code":"指数代码",
            "change":"涨跌幅",
            "open":"开盘点位",
            "preclose":"昨日收盘点位",
            "close":"收盘点位",
            "high":"最高点位",
            "low":"最低点位",
            "volume":"成交量(手)",
            "amount":"成交金额(亿)"}
    cols = list(en2cn.keys())[:-3]
    for index in data.index:

        node = Node('指数', name = data.at[index, 'name'])
        graph.create(node)
        SQL = "match (n:`指数`{name:'%s'}) set n+= {"%data.at[index, 'name']

        for col in cols[:-1]:
            SQL += ('`' + en2cn[col] +"`:'"+str(data.at[index, col]) + "',")
        SQL += ('`' +  en2cn[cols[-1]] +"`:'"+str(data.at[index, cols[-1]] )+ "'} ")
        print(SQL)
        graph.run(SQL)


# def add_profit_data():

def getNode(graph, label, propertity, value, limit_num=10, fuzzy_search = False, createNode = False):
    matcher = NodeMatcher(graph)
    where = ""
    if type(propertity) == str and type(value) == str:
        where = ('_.' + propertity + '="' + value + '"' )
    elif type(propertity) == list and type(value) == list:
        if len(propertity) != len(value):
            print("参数长度不匹配~，请重新考虑")
            return
        for x in range(len(propertity)):
            where += ('_.' + propertity[x] + "='" + value[x] +"'," )
        where = where[:-1]

    if fuzzy_search:
        where.replace("=", "=~")
    nodes = list(matcher.match(label).where(where).limit(limit_num))
    if createNode:
        if len(nodes) == 0:
            if not fuzzy_search:
                graph.create(Node(label, where))
                nodes = list(matcher.match(label).where(where).limit(limit_num))
            else:
                print("模糊搜索模式下不能创建节点")
        else:
            print("存在节点，不建议重复创建")
    return nodes


def update_neo4j_stock_profit_info(graph):
    dataframe = ts.get_stock_basics()
    para_en = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']
    paras_cn = ["开盘价", "最高价", "收盘价","最低价","成交量","价格变动","涨跌幅","五日均价","十日均价","二十日均价","五日均量","十日均量","二十日均量"]
    codes = list(dataframe.index)
    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    length = len(codes)
    count = 0
    for index in codes:
        count+=1
        if index == '0' or index == None:
            continue
        if len(index) != 6 and len(index) > 0:
            index = '0'*(6-len(index)) + index
        if count % int(length/1000) == 0:
            print("%s / %s"%(count, length))
        if index not in code_in_Neo4j:
            try:
                graph.create(Node('股票', stock_id=index, name= dataframe.at[index, 'name']))
            except KeyError as e:
                print("Index : %s ")
            print("Create Stock %s"%index)
        try:
            lateestDate = graph.run("match (n:`股票`) where n.stock_id='%s' return n.最新日期"%index).data()[0].get('n.最新日期')
            df = ts.get_hist_data(index, lateestDate, str(datetime.date.today()), 'D')
            if df.empty:
                print("没有获取到数据")
                continue
        except TypeError as e:
            print("Code:%s, TypeError!!!"%index)
            continue
        except AttributeError as ae:
            print("Code:%s, AttributeError!"%index)
            continue
        try:
            cypher = "match (n:`股票`{stock_id:'%s'}) set n.%s = '%s'" % (index, '最新日期', df.index[0])
            graph.run(cypher)
        except IndexError as e:
            print("索引 %s 出错"%index)
            print(df)
        # print(cypher)
        for p in range(len(para_en)):
            cypher = "match (n:`股票`{stock_id:'%s'}) set n.%s = '%s'" % (index, paras_cn[p], df.at[df.index[0], para_en[p]])
            graph.run(cypher)
            # print(cypher)

        # except AttributeError as e:
        #     print("属性 %s 出错" % index)
        #     print(df)
        # break


def update_neo4j_stock_roe_info(graph):
    dataframe = ts.get_stock_basics()
    # para_en = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']
    # paras_cn = ["开盘价", "最高价", "收盘价","最低价","成交量","价格变动","涨跌幅","五日均价","十日均价","二十日均价","五日均量","十日均量","二十日均量"]
    codes = list(dataframe.index)
    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    length = len(codes)
    count = 0
    pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    ts_code = {x[:6]: x for x in list(pro.query('stock_basic', exchange='', list_status='L', fields='ts_code').ts_code)}
    ROE = {'roe':"净资产收益率(ROE)", 'roe_waa':"加权平均净资产收益率(ROE_WAA)", 'roe_dt':"净资产收益率(扣除非经常损益,ROE_DT)", 'roe_yearly':"年化净资产收益率(ROE_YEARLY)"}
    for index in codes:
        count+=1
        if index == '0' or index == None:
            continue
        if len(index) != 6 and len(index) > 0:
            index = '0'*(6-len(index)) + index
        if count % int(length/50) == 0:
            print("%s / %s"%(count, length))
        if index not in code_in_Neo4j:
            try:
                graph.create(Node('股票', stock_id=index, name= dataframe.at[index, 'name']))
            except KeyError as e:
                print("Index : %s ")
            print("Create Stock %s"%index)
        try:
            df = pro.fina_indicator(ts_code=ts_code[index], start_date=str(datetime.date.today()))
            time.sleep(0.75)
            if df.empty:
                print("没有获取到数据")
                continue
        except TypeError as e:
            print("Code:%s, TypeError!!!"%index)
            continue
        except AttributeError as ae:
            print("Code:%s, AttributeError!"%index)
            continue
        for idx in ROE.keys():
            try:
                cypher = "match (n:`股票`{stock_id:'%s'}) set n.`%s` = '%s'" % (index, ROE[idx], df.at[0, idx])
                graph.run(cypher)
            except IndexError as e:
                print("索引 %s 出错"%index)
                print(df)



def update_stock_basics(graph):
    paras2cn = {"code":"代码",
                "name":"名称",
                "industry":"细分行业",
                "area":"地区",
                "pe":"市盈率",
                "outstanding":"流通股本",
                "totals":"总股本(万)",
                "totalAssets":"总资产(万)",
                "liquidAssets":"流动资产",
                "fixedAssets":"固定资产",
                "reserved":"公积金",
                "reservedPerShare":"每股公积金",
                "esp":"每股收益",
                "bvps":"每股净资",
                "pb":"市净率",
                "timeToMarket":"上市日期"
             }
    paras = list(paras2cn.keys())
    dataframe = ts.get_stock_basics()
    print(dataframe.columns)
    split_industry = set()
    area = set()
    for index in dataframe.index:
        split_industry.add(dataframe.at[index, 'industry'])
        area.add(dataframe.at[index, 'area'])
    count = 10000
    get_si = graph.run("match (n:`行业`) return n.name").data()
    si_in_Neo4j = [ x['n.name'] for x in  get_si]
    print(si_in_Neo4j)
    count += len(si_in_Neo4j)
    for si in split_industry:
        if si not in si_in_Neo4j:
            count+=1
            graph.create(Node('细分行业', splitIndustry_id = str(count), name = si))

    get_area = graph.run("match (n:`地区`) return n.name").data()
    area_in_Neo4j = [x['n.name'] for x in get_area]
    print(area_in_Neo4j)
    print(area)
    count += len(area_in_Neo4j)
    show = True
    for a in area:
        if a not in area_in_Neo4j:
            count += 1
            graph.create(Node('地区', area_id=str(count), name=a))

    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    for index in dataframe.index:
        if index not in code_in_Neo4j:
            graph.create(Node('股票', stock_id=index, name= dataframe.at[index, 'name']))
            print("Create Stock %s"%index)
        node = graph.nodes.match('股票', stock_id=index).first()
        si = graph.nodes.match('细分行业', name=dataframe.at[index, "industry"]).first()
        area = graph.nodes.match('地区', name=dataframe.at[index, "area"]).first()
        s2a = Relationship(node, 'located_in', area)
        graph.create(s2a)
        try:
            s2s = Relationship(node, 'belong_to', si)
            graph.create(s2s)
        except AttributeError as e:
            if show:
                print(node)
                print(si)
                print(area)
                show = False
        for p in ['name'] + paras[4:]:
            cypher = "match (n:`股票`{stock_id:'%s'}) set n.%s = '%s'"%(index, p, dataframe.at[index, p])
            graph.run(cypher)



if __name__ == '__main__':
    graph = Graph('http://localhost:11003', username='neo4j', password='zzb162122')
    # graph = Graph('http://39.99.253.203:7474', username='neo4j', password='zzb162122')
    # createNode_1(graph, 'data/holders_stock.csv')
    # update_neo4j_stock_roe_info(graph)
    update_stock_basics(graph)
    update_neo4j_stock_profit_info(graph)
    # createIndexNode(graph)