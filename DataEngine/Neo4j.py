import pandas as pd
from py2neo import Node, Relationship, Graph, NodeMatcher
import datetime
import time
from DataEngine.Data import *


def InitializationGraph(ts_code=''):
    # 获取需要的股票基础数据
    df = get_pro_stock_basic()
    concepts = get_concept()['name']
    index_basic = get_index_basic()
    length = int(df.size / len(df.columns))
    count = 0
    if len(ts_code) == 0:
        # 生成指数节点
        try:
            index_ = graph.run("match (n:`指数`) return n.name").data()
            existIndex = [x['n.name'] for x in index_]
        except KeyError as e:
            print("没有指数这个类别，创建")
            existIndex = []
        for idx in range(len(index_basic['name'])):
            if index_basic.at[idx,'name'] in existIndex:
                continue
            node = Node('指数', index_id=index_basic.at[idx,'ts_code'], name=index_basic.at[idx,'name'], category=index_basic.at[idx,'category'])
            graph.create(node)
            count += 1
        count = 0

        # 生成行业节点
        try:
            industry_ = graph.run("match (n:`行业`) return n.name").data()
            existIndustry = [x['n.name'] for x in industry_]
        except KeyError as e:
            print("没有这个类别，创建")
            existIndustry = []
        for industry in set(df['industry']):
            if industry in existIndustry:
                continue
            node = Node('行业', industry_id=count, name=industry)
            graph.create(node)
            count += 1
        count = 0

        # 生成地区节点
        try:
            area_ = graph.run("match (n:`地区`) return n.name").data()
            existIArea = [x['n.name'] for x in area_]
        except KeyError as e:
            print("没有这个类别，创建")
            existIArea = []
        for area in set(df['area']):
            if area in existIArea:
                continue
            node = Node('地区', area_id=count, name=area)
            graph.create(node)
            count += 1
        count = 0

        # 生成概念节点
        try:
            concept_ = graph.run("match (n:`概念`) return n.name").data()
            existConcept = [x['n.name'] for x in concept_]
        except KeyError as e:
            print("没有这个类别，创建")
            existConcept = []
        for con in concepts:
            if con in existConcept:
                continue
            node = Node('概念', concept_id=count, name=con)
            graph.create(node)
            count += 1

        # 生成股票数据
    try:
        stock_ = graph.run("match (n:`股票`) return n.stock_id").data()
        existStock = [x['n.stock_id'] for x in stock_]
    except KeyError as e:
        print("没有股票，创建")
        existStock = []

    for index in range(length):
        if index % int(length/20) == 0:
            print("Progress: %s / %s"%(index,length))
        if df.at[index, 'ts_code'] in existStock:
            continue
        if len(ts_code) == 0:
            code = df.at[index, 'ts_code']
        else:
            code = ts_code
        if code[0] == '6':
            if code[1] == '8' and code[2]=='8':
                type = '科创板'
            else:
                type = '沪市'
        elif code[0] == '3':
            type = '创业板'
        elif code[0] == '0':
            type = '深市'
        try:
            time.sleep(0.1)
            stock_concepts = list(get_stock_concepts(df.at[index, 'ts_code'])['concept_name'])
        except Exception:
            time.sleep(80)
            stock_concepts = list(get_stock_concepts(df.at[index, 'ts_code'])['concept_name'])
        if len(stock_concepts) == 0:
            time.sleep(80)
            stock_concepts = list(get_stock_concepts(df.at[index, 'ts_code'])['concept_name'])
        node = Node('股票', stock_id = df.at[index, 'ts_code'], name = df.at[index, 'name'], type = type )
        graph.create(node)
        a = graph.nodes.match('股票', stock_id=df.at[index, 'ts_code']).first()
        b = graph.nodes.match('行业', name=df.at[index, 'industry']).first()
        r = Relationship(a, 'belong_to', b)
        graph.create(r)
        b = graph.nodes.match('地区', name=df.at[index, 'area']).first()
        r = Relationship(a, 'locate_at', b)
        graph.create(r)
        concept_ = graph.run("match (n:`概念`) return n.name").data()
        existConcept = [x['n.name'] for x in concept_]
        for c in stock_concepts:
            if c not in existConcept:
                print("额外的概念:%s"%c)
                node = Node('概念', concept_id=count, name=c)
                count += 1
                graph.create(node)
            b = graph.nodes.match('概念', name=c).first()
            r = Relationship(a, 'concept_of', b)
            graph.create(r)


def update_index_daily(graph, assign_date=''):
    index_ = graph.run("match (n:`指数`) return n.index_id").data()
    existIndex = [x['n.index_id'] for x in index_]
    if assign_date and not assign_date > str(datetime.date.today()).replace('-', ''):
        targetDate = assign_date
    else:
        targetDate = str(datetime.date.today()).replace('-', '')
    lateestDate = str(datetime.date.today() - datetime.timedelta(days=3)).replace('-', '')
    gap = 3
    while lateestDate > targetDate:
        gap += 3
        lateestDate = str(datetime.date.today() - datetime.timedelta(days=gap)).replace('-', '')

    for index in existIndex:
        try:
            data = get_index(index, lateestDate, targetDate)
            time.sleep(0.1)
        except Exception as e:
            print("a Oh~ 读取数据太频繁了")
            time.sleep(80)
            data = get_index(index,lateestDate, targetDate)
            time.sleep(0.1)
        if len(data) == 0:
            continue
        else:
            data = data
        en2cn = {
                "ts_code":"指数代码",
                "trade_date":"交易日",
                "change":"涨跌点",
                "pct_chg":"涨跌幅",
                "open":"开盘点位",
                "pre_close":"昨日收盘点位",
                "close":"收盘点位",
                "high":"最高点位",
                "low":"最低点位",
                "vol":"成交量(手)",
                "amount":"成交金额(亿)"}
        cols = list(en2cn.keys())
        SQL = "match (n:`指数`{index_id:'%s'}) set n+= {"%index
        for col in cols[1:-1]:
            SQL += ('`' + en2cn[col] +"`:'"+str(data.at[0, col]) + "',")
        SQL += ('`' +  en2cn[cols[-1]] +"`:'"+str(data.at[0, cols[-1]])+ "'} ")
        # print(SQL)
        graph.run(SQL)
    print("大盘指数更新完毕！")

def getNode(graph, label, propertity, value, limit_num=10, fuzzy_search = False, createNode = False):
    """
    获取节点，如果没有这个节点，就创建
    :param graph: 图
    :param label: 类型
    :param propertity: 属性名
    :param value: 属性值
    :param limit_num: 限制返回数目
    :param fuzzy_search: 是否模糊搜索
    :param createNode: 是否创建新的node
    :return: 返回查询到的node或者是新创建的node
    """
    createNode = False
    matcher = NodeMatcher(graph)
    where = ""
    if type(propertity) == str and type(value) == str:
        where = ('_.' + propertity + '="' + value + '"' )
    elif type(propertity) == list and type(value) == list:
        if len(propertity) != len(value):
            print("参数长度不匹配~，请重新考虑")
            return
        for x in range(len(propertity)):
            where += ('_.' + propertity[x] + "='" + value[x] +"' and " )
        where = where[:-4]

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
            pass
    return nodes

def update_neo4j_stock_daily_info(graph, assign_date=''):
    """
    更新所有的股票节点的当日信息
    :param graph:  操作的图
    :return: 无返回
    """
    dataframe = get_pro_daily('')
    # data_basic = get_pro_stock_basic()
    para_en = ['trade_date','open', 'high', 'close', 'low', 'vol', 'pre_close', 'change', 'pct_chg', 'amount']
    paras_cn = ["交易日","开盘价", "最高价", "收盘价","最低价","成交量","昨收价","涨跌额","涨跌幅","成交额"]
    codes = list(dataframe.ts_code)
    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    length = len(codes)
    count = 0
    for code in codes:
        count+=1
        if count % int(length/100) == 0:
            print("%s / %s"%(count, length))
        if code not in code_in_Neo4j:
            print("图中无此节点：%s"%code)
            # InitializationGraph(code)
        if assign_date and not assign_date > str(datetime.date.today()).replace('-', ''):
            targetDate = assign_date
        else:
            targetDate = str(datetime.date.today()).replace('-', '')
        lateestDate = str(datetime.date.today() - datetime.timedelta(days=3)).replace('-', '')
        gap = 3
        while lateestDate > targetDate:
            gap += 3
            lateestDate = str(datetime.date.today() - datetime.timedelta(days=gap)).replace('-', '')
        try:
            df = get_pro_daily(code, lateestDate, targetDate)
            time.sleep(0.1)
        except Exception as e:
            print("%s获取数据第一次尝试失败"%code)
            time.sleep(60)
            df = get_pro_daily(code, lateestDate, targetDate)
        if len(df) == 0:
            print("%s获取数据失败" % code)
            continue
            # time.sleep(60)
            # df = get_pro_daily(code, lateestDate, str(datetime.date.today()))
            # if len(df) == 0:
            #     print("%s获取数据第三次尝试失败" % code)
            #     continue
        SQL = "match (n:`股票`{stock_id:'%s'}) set n+= {" % code
        for col in range(len(para_en) - 1):
            SQL += ('`' + paras_cn[col] + "`:'" + str(df.at[df.index[0], para_en[col]]) + "',")
        SQL += ('`' + paras_cn[-1] + "`:'" + str(df.at[df.index[0], para_en[-1]]) + "'} ")
        graph.run(SQL)


def round2(x):
    return round(float(x),2)

def round4(x):
    return round(float(x),4)


def formatDate(x):
    return x.replace('-', '')


def update_neo4j_stock_realTime(graph):
    """
    更新所有的股票节点的当前信息
    :param graph:  操作的图
    :return: 无返回
    """
    # data_basic = get_pro_stock_basic()
    start = time.clock()
    para_en = ['date','open', 'high', 'close', 'low', 'volume', 'now', 'change', 'pct_chg']
    paras_cn = ["交易日","开盘价", "最高价", "收盘价","最低价","成交量","现价","涨跌额","涨跌幅"]
    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    codes = [x[:6] for x in code_in_Neo4j]
    data = pd.DataFrame(qo.stocks(codes)).T
    data['change'] = (data['now'] - data['close']).map(round2)
    data['date'] = data['date'].map(formatDate)
    data['pct_chg'] = (data['change'] / data['close']).map(round4)
    count = 0
    for code in range(len(code_in_Neo4j)):
        count += 1
        if (count % int(len(code_in_Neo4j)/20) == 0):
            print('[' + '>' * (count // int(len(code_in_Neo4j)/20)) +
                  '*' * (20 - count // int(len(code_in_Neo4j) / 20)) + ']')
        try:
            SQL = "match (n:`股票`{stock_id:'%s'}) set n+= {" % code_in_Neo4j[code]
            for col in range(len(para_en)-1):
                SQL += ('`' +  paras_cn[col] + "`:'" + str(data.at[codes[code], para_en[col]]) + "',")
            SQL += ('`' + paras_cn[-1] + "`:'" + str(data.at[codes[code], para_en[-1]]) + "'} ")
            # print(SQL)
            graph.run(SQL)
        except IndexError as e:
            print("索引 %s 出错"%code)
        # print(cypher)
    print("Time Usage:%s"%(round((time.clock() - start),2) ))

        # except AttributeError as e:
        #     print("属性 %s 出错" % index)
        #     print(df)
        # break


def update_stock_propertity_value(graph, label, propertity, values, condition):
    if len(propertity) != len(values):
        print("属性名和属性值数量不匹配！")
        return
    for val in range(len(values)):
        graph.run("match(n:`%s`) %s set n.%s = '%s' "%(label, condition, propertity[val], values[val]))

def update_neo4j_stock_finance_info(graph):
    """
    更新每个股票节点的财务信息
    :param graph: 图
    :return: 无
    """
    # para_en = ['open', 'high', 'close', 'low', 'volume', 'price_change', 'p_change', 'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20']
    # paras_cn = ["开盘价", "最高价", "收盘价","最低价","成交量","价格变动","涨跌幅","五日均价","十日均价","二十日均价","五日均量","十日均量","二十日均量"]
    code_in_Neo4j = [x['n.stock_id'] for x in graph.run("match (n:`股票`) return n.stock_id").data()]
    count = 0
    basic = get_pro_stock_basic()
    codes = list(basic['symbol'])
    length = len(codes)
    code_ts = {basic.at[idx, 'symbol']:basic.at[idx, 'ts_code'] for idx in basic.index}
    code_name = {basic.at[idx, 'symbol']:basic.at[idx, 'name'] for idx in basic.index}
    ROE = {'current_ratio':"流动比率(资产变现能力)", 'dp_assets_to_eqt':"权益乘数(股东占资产比例)",'roe':"ROE", 'roe_yearly':"ROE_YEARLY"}
    for index in codes:
        count+=1
        if index not in code_in_Neo4j:
            print("图中无此节点：%s" % index)
            InitializationGraph()
        if count % int(length/50) == 0:
            print("%s / %s"%(count, length))
        try:
            df = get_fina_indicator(ts_code=code_ts[index])
            time.sleep(0.15)
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
            update_stock_propertity_value(graph, ",".join(ROE.values()), )
        except IndexError as e:
            print("索引 %s 出错"%index)
            print(df)

def update_propertity_name_for_neo4j(graph, old_new_propertity):
    """
    更新属性的名称
    :param graph: 图
    :param old_new_propertity: 新的老的属性值的名字字典
    :return:
    """
    for old in old_new_propertity.keys():
        graph.run("match(n) where exists(n.%s) set n.%s = n.%s remove n.%s"%(old, old_new_propertity[old], old, old))

def remove_propertity_for_neo4j(graph, delete_propertity):
    """
    更新属性的名称
    :param graph: 图
    :param old_new_propertity: 删除的属性值的名字序列
    :return:
    """
    for old in delete_propertity:
        graph.run("match(n) where exists(n.`%s`) remove n.`%s`"%(old, old))

def update_stock_basics(graph):
    """
    更新股票节点的相关节点信息
    :param graph:
    :return:
    """
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
    dataframe = get_stock_basics()
    print(dataframe.columns)
    split_industry = set()
    area = set()
    for index in dataframe.index:
        split_industry.add(dataframe.at[index, 'industry'])
        area.add(dataframe.at[index, 'area'])
    count = 10000
    get_si = graph.run("match (n:`行业`) return n.name").data()
    si_in_Neo4j = [ x['n.name'] for x in get_si]
    count += len(si_in_Neo4j)
    for si in split_industry:
        if si not in si_in_Neo4j:
            count += 1
            graph.create(Node('细分行业', splitIndustry_id = str(count), name = si))
            for index in dataframe.index:
                if dataframe.at[index, "industry"] == si:
                    node = getNode(graph, '股票', 'stock_id', index, createNode=True)[0]
                    si_1 = graph.nodes.match('细分行业', name=dataframe.at[index, "industry"]).first()
                    s2s = Relationship(node, 'belong_to', si_1)
                    graph.create(s2s)
    get_area = graph.run("match (n:`地区`) return n.name").data()
    area_in_Neo4j = [x['n.name'] for x in get_area]
    count += len(area_in_Neo4j)
    for a in area:
        if a not in area_in_Neo4j:
            count += 1
            graph.create(Node('地区', area_id=str(count), name=a))
            for index in dataframe.index:
                if dataframe.at[index, "area"] == a:
                    node = getNode(graph, '股票', 'stock_id', index, createNode=True)[0]
                    ar = graph.nodes.match('地区', name=dataframe.at[index, "area"]).first()
                    s2a = Relationship(node, 'located_in', ar)
                    graph.create(s2a)
    for index in dataframe.index:
        for p in ['name'] + paras[4:]:
            cypher = "match (n:`股票`{stock_id:'%s'}) set n.%s = '%s'"%(index, paras2cn[p], dataframe.at[index, p])
            graph.run(cypher)


def get_Graph():
    """
    返回图
    :return: 图
    """
    from Config.Config import Config
    config = Config('ts').getInfo()
    return Graph('bolt://localhost:7687',auth=(config.name, config.password))

if __name__ == '__main__':
    graph = get_Graph()
    # createNode_1(graph, 'graph_data/holders_stock.csv')
    # update_neo4j_stock_finance_info(graph)
    # update_stock_basics(graph)
    # update_propertity_name_for_neo4j(graph, {"pe":"市盈率",
    #                                      "outstanding": "`流通股本`",
    #                                      "totals": "`总股本(万)`",
    #                                      "totalAssets": "`总资产(万)`",
    #                                      "liquidAssets": "`流动资产`",
    #                                      "fixedAssets": "`固定资产`",
    #                                      "reserved": "`公积金`",
    #                                      "reservedPerShare": "`每股公积金`",
    #                                      "esp": "`每股收益`",
    #                                      "bvps": "`每股净资`",
    #                                      "pb": "`市净率`",
    #                                      "timeToMarket": "`上市日期`"
    #                                      })
    # InitializationGraph()
    # update_index_daily(graph)
    update_neo4j_stock_daily_info(graph)
    # update_neo4j_stock_realTime(graph)
    data = graph.run("match(n:`股票`)-[:belong_to]->(p:`行业`) return p,n").data()
    # data = graph.run("match(n:`股票`)-[:belong_to]->(p:`行业`) where n.`涨跌幅` > '0.03' return p,n").data()
    key = ''
    for d in data:
        for x in d.keys():
            if x=='p':
                if key == d['p']['name']:
                    continue
                else:
                    key = d['p']['name']
                    print(d['p']['name'])
            else:
                if d['n']['name'].find('ST')!=-1:
                    print('\t' + d['n']['name'] +'\t' + d['n']['stock_id'] +'\t' + d['n']['涨跌幅'])


