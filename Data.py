import random
import datetime

import tushare as ts
pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
import pandas as pd


def save_realtime_price(code, name, ktype='5'):
    if type(code) == str and type(name) == str:
        with open('histTickData/%s-%s.txt'%(code, name), 'a', encoding='utf8') as out:
            date_price = get_realtime_price(code, ktype)
            for x in date_price:
                out.write("时间：%s\n" % x[0])
                out.write(", ".join(x[1]))
                out.write("\n")
    elif type(code) == list and type(name) == list:
        for idx in range(len(code)):
            with open('tickData/%s-%s.txt' % (code[idx], name[idx]), 'a', encoding='utf8') as out:
                date_price = get_realtime_price(code[idx], ktype)
                for x in date_price:
                    out.write("时间：%s\n" % x[0])
                    out.write(", ".join(x[1]))
                    out.write("\n")

def get_realtime_price(code='sh', ktype='5'):
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
    return sorted(date_prices.items(),key=lambda date_prices:date_prices[0],reverse=False)


def get_stock_basics():
    return ts.get_stock_basics()

def get_fina_indicator(ts_code):
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
    # get_realtime_price('sh')

    symbol = ["002164", "002517", "002457", "600723", "600918", "600720", "603187", "002271", "000759", "000735", "601933"]
    stock_name = ["宁波东力", "恺英网络", "青龙管业", "首商股份", "中泰证券", "祁连山", "海容冷链", "东方雨虹", "中百集团", "罗牛山", "永辉超市"]
    save_realtime_price(symbol, stock_name, '5')