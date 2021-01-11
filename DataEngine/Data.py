
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
    * 历史数据存入Mysql
    * 股票属性（市盈率，市净率等）以图数据库形式存入Neo4j中

"""


import random
import datetime
import easyquotation
import tushare as ts
import pandas as pd


"""
获取Tushare的pro权限账户
:param
    None
:return
    pro
"""
def get_pro():
    return ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')


"""
此处为获取全局的工具：
    qo为快速获取实时股票信息的接口
    pro为 Tushare pro版本接口
"""

def get_qo():
    return easyquotation.use('sina')
qo = get_qo()
pro = get_pro()


def get_news(src='sina', start_date='2018-11-21 09:00:00', end_date='2018-11-22 10:10:00'):
    return pro.news()


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


def fund_basic(market='E'):
    pro.fund_basic(market='E')

def get_stock_basics():
    """
    :function
        获取大盘所有股票的基础信息
    :returns
        Dataframe结构，索引为股票代码，列名如下：
            Index(['name', 'industry', 'area', 'pe', 'outstanding', 'totals',
               'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved',
               'reservedPerShare', 'esp', 'bvps', 'pb', 'timeToMarket', 'undp',
               'perundp', 'rev', 'profit', 'gpr', 'npr', 'holders'],
              dtype='object')
           name,名称
           industry,细分行业
           area,地区
           pe,市盈率
           outstanding,流通股本
           totals,总股本(万)
           totalAssets,总资产(万)
           liquidAssets,流动资产
           fixedAssets,固定资产
           reserved,公积金
           reservedPerShare,每股公积金
           esp,每股收益
           bvps,每股净资
           pb,市净率
           timeToMarket,上市日期
    """
    return ts.get_stock_basics()


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

def get_index():
    return ts.get_index()

def get_pro_stock_basic(fields='ts_code,symbol,name,area,industry,list_date'):
    return pro.stock_basic(exchange='', list_status='L', fields=fields)

def get_pro_daily(ts_code, start_date='2010-01-04', end_date= str(datetime.date.today().isoformat())):
    if type(ts_code) == str:
        return pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    elif type(ts_code) == list:
        return pro.daily(ts_code=",".join(ts_code), start_date=start_date, end_date=end_date)
    else:
        print("输入的股票代码有错误")

def get_hist_data(code = '600355', start = "2000-01-01", end = "2020-07-15" ):
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
    return df

if __name__ == '__main__':
    # get_tick_price('sh')

    symbol = ["002164", "002517", "002457", "600723", "600918", "600720", "603187", "002271", "000759", "000735", "601933"]
    stock_name = ["宁波东力", "恺英网络", "青龙管业", "首商股份", "中泰证券", "祁连山", "海容冷链", "东方雨虹", "中百集团", "罗牛山", "永辉超市"]
    print("数据驱动引擎，获取数据的总接口")