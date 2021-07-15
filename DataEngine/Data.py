
"""
本模块主要用于构架数据引擎的关于网络数据的获取
其中，主要实现：

:function
    * 股票历史分时数据的获取 get_tick_price
    * 股票历史日K数据的获取 get_hist_data
    * 股票实时数据获取 realTimePrice
    * 股票当天数据获取
    * 获取A股市场里面所有的股票的基础数据 get_stock_basics
    * 获取某只股票的财务数据，比如市盈率roe等 get_fina_indicator
    * 获取大盘一些指数的数据
    * 历史数据存入Mysqlname
    * 股票属性（市盈率，市净率等）以图数据库形式存入Neo4j中

"""


import random
import datetime
import easyquotation
import tushare as ts
import pandas as pd
import sys
sys.path.append('../../Quantify')
from Config.Config import Config
config = Config('ts').getInfo()

"""
获取Tushare的pro权限账户
:param
    None
:return
    pro
"""
def get_pro():
    return ts.pro_api(config['api'])

ts.set_token(config['api'])

"""
此处为获取全局的工具：
    qo为快速获取实时股票信息的接口
    pro为 Tushare pro版本接口
"""

def get_qo():
    return easyquotation.use('sina')

qo = get_qo()
pro = get_pro()

def get_news():
    return pro.news

def realTimePrice(code):
    """
    获取股票当下信息
    :param
        * code:股票代码，可以是'000759'，也可以是['000759','000043']
    :return
        {
        '000759':
                {'name': '中百集团',
                  'open': 7.08,
                  'close': 7.08,
                  'now': 6.97,
                  'high': 7.12,
                  'low': 6.94,
                },
        'xxxxxx':
                {...}
        }
    """
    return qo.stocks(code)



def get_tick_price(code='sh', ktype='5'):
    """
    :function
    获取历史分时记录。最新到当前时间，一共350条记录

    :param
        * code:股票代码
        * ktype:获取数据类型
            * '5' ：五分钟间隔获取数据（默认值）
            * '15'：15mins
            * '60'：60mins
            * 'D'：按天

    :returns
        {
            '2020-08-10':[10.01, 11.01.....],
            '2020-08-11':[12.01, 13.01.....],
        }
    """
    time_price = ts.get_hist_data(code, ktype=ktype)
    date_prices = {}
    for x in time_price.index:
        date = str(x[:10])
        if not date_prices.get(date):
            date_prices[date] = [float(time_price.at[x, 'open'])]
        else:
            date_prices[date].append(float(time_price.at[x, 'open']))
    for s in date_prices.keys():
        date_prices[s].reverse()
    return sorted(date_prices.items(), key=lambda date_prices:date_prices[0],reverse=False)

def get_concept():
    return pro.concept()

def get_pro_monthly(ts_code, start_date='2021-01-04', end_date= str(datetime.date.today().isoformat()).replace('-','')):
    return  pro.monthly(ts_code='000001.SZ', start_date='20180101', end_date='20181101', fields='ts_code,trade_date,open,high,low,close,vol,amount')

def get_stock_concepts(code):
    if code.find('TS')!=-1 or code.find('ts') != -1:
        return pro.concept_detail(id=code, fields='ts_code,name')
    return pro.concept_detail(ts_code = code)


def get_fina_indicator(ts_code):
    """
    :function
        获取一只股票的金融信息，包含很多。。官网看吧
    :param
        * ts_code：股票代码，记得带市场，例如：'000759.SZ'
    :return
        * Dataframe 108 columns
    """
    return pro.fina_indicator(ts_code = ts_code)

def get_daily_basic(date=''):
    if date == '':
        date = datetime.datetime.now().strftime("%Y%m%d")
    df = pro.daily_basic(ts_code='', trade_date=date,
                         fields='ts_code,trade_date,close,turnover_rate_f,volume_ratio,pe,pb,free_share,total_mv')
    return df


def get_index(ts_code='399300.SZ', start_date='20180101', end_date='20181010'):
    df = pro.index_daily(ts_code=ts_code,start_date=start_date,end_date=end_date)
    return df

def get_index_basic(market='SSE'):
    return pro.index_basic(market=market)

def get_index_weight(code='399300.SZ',start_date='20180901', end_date='20180930'):
    return pro.index_weight(index_code = code,start_date= start_date, end_date = end_date )

def get_stock_list_date(to_lower=True):
    def lower(c):
        return c.lower()
    stock_basic = get_pro_stock_basic(fields='ts_code,list_date')
    list_date = list(stock_basic['list_date'])
    if to_lower:
        codes = list(stock_basic['ts_code'].apply(lower))
    code_listdate = {codes[x]: list_date[x] for x in range(len(codes))}
    return code_listdate

def get_pro_stock_basic(fields='ts_code,symbol,name,area,industry,list_date'):
    return pro.stock_basic(exchange='', list_status='L', fields=fields)

def get_stock_name():
    def lower(c):
        return c.lower()
    stock_basic = get_pro_stock_basic(fields='ts_code,name')
    name = list(stock_basic['name'])
    codes = list(stock_basic['ts_code'])
    code_name = {codes[x]: name[x] for x in range(len(codes))}
    return code_name

def get_pro_daily(ts_code, start_date='2021-01-04', end_date= str(datetime.date.today().isoformat()).replace('-','')):
    if type(ts_code) == str:
        return pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    elif type(ts_code) == list:
        return pro.daily(ts_code=",".join(ts_code), start_date=start_date, end_date=end_date)
    else:
        return pro.daily()

def get_fund_basic(EO='E'):
    return pro.fund_basic(market=EO)

def get_fund_name():
    ss = get_fund_basic()
    code_name = {}
    for i in range(len(ss)):
        code = ss.loc[i,'ts_code']
        name = ss.loc[i,'name']
        code_name[code] = name
    return code_name


def get_fund_daily(ts_code='150018.SZ', start_date='20180101', end_date='20181029', ma=[5,10,20,50]):
    return ts.pro_bar(ts_code=ts_code,  asset = 'FD', ma=ma, start_date=start_date, end_date=end_date)

def get_stock_daily(ts_code='150018.SZ', start_date='20180101', end_date='20181029', ma=[5,10,20,50]):
    return ts.pro_bar(ts_code=ts_code,  asset = 'E', start_date=start_date, end_date=end_date, adj='qfq', ma=ma, freq='D')

def get_stock_weekly(ts_code='150018.SZ', start_date='20180101', end_date='20181029', ma=[5,10,20,50]):
    return ts.pro_bar(ts_code=ts_code,  asset = 'E', start_date=start_date, end_date=end_date, adj='qfq',  ma=ma, freq='W')


if __name__ == '__main__':
    # get_tick_price('sh')
    symbol = ["002164", "002517", "002457", "600723", "600918", "600720", "603187", "002271", "000759", "000735", "601933"]
    stock_name = ["宁波东力", "恺英网络", "青龙管业", "首商股份", "中泰证券", "祁连山", "海容冷链", "东方雨虹", "中百集团", "罗牛山", "永辉超市"]
    print("数据驱动引擎，获取数据的总接口")
    data = get_news()
    print(data['datetime','title'])
