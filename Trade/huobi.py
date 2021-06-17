import datetime
import hashlib
import os
import time
import urllib
from urllib import parse

import json
import requests

import hmac
import base64
from hashlib import sha256
import random

def get_keys(path='./privateconfig.py'):
    with open(path,'r',encoding='utf8') as f:
        data = f.readlines()
        l1 = data[0].strip()
        l2 = data[1].strip()
        p_api_key = l1[l1.find('"')+1:-1]
        p_secret_key = l2[l2.find('"')+1:-1]
    return p_api_key, p_secret_key


ACCESS_KEY, SECRET_KEY = get_keys()
TIMEOUT = 5


def quote(text):
    return text
    # return text.replace(':','%3A').replace(' ','%20')

def quote1(text):
    return parse.quote(text)



def BeijingTime(format = '%H:%M:%S'):
    from datetime import datetime
    from datetime import timedelta
    from datetime import timezone

    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )

    # 协调世界时
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    print(utc_now, utc_now.tzname())
    print(utc_now.date(), utc_now.tzname())

    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    return beijing_now.strftime(format)


def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature



def get_signature(secret, data):
    appsecret = secret.encode('utf-8')  # 秘钥
    data = data.encode('utf-8')  # 加密数据
    signature = base64.b64encode(hmac.new(appsecret, data, digestmod=sha256).digest())
    # 获取十六进制加密数据
    # signature = base64.b64encode(hmac.new(appsecret, data, digestmod=sha256).hexdigest())
    return signature.decode('utf-8')

def get_url(url="https://api.huobi.pro/v1/common/currencys"):
    #
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'Accept': '*/*',
        'Referer': 'http://fund.eastmoney.com/data/fundranking.html',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    }

    json_response = requests.get(
        url, headers=headers).json()
    # print(json_response)
    return json_response

    # 各种请求,获取数据方式

def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    try:
        response = requests.get(url, postdata, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "fail"}
    except Exception as e:
        print("httpGet failed, detail is:%s" % e)
        return {"status": "fail", "msg": "%s" % e}

def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Accept": "application/json",
        'Content-Type': 'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = json.dumps(params)
    try:
        response = requests.post(url, postdata, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()
    except Exception as e:
        print("httpPost failed, detail is:%s" % e)
        return {"status":"fail","msg": "%s"%e}


def createSign(pParams, method, host_url, request_path, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, host_url, request_path, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')
    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature

def api_key_get(url, request_path, params, ACCESS_KEY, SECRET_KEY):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params.update({'AccessKeyId': ACCESS_KEY,
                   'SignatureMethod': 'HmacSHA256',
                   'SignatureVersion': '2',
                   'Timestamp': timestamp})

    host_name = host_url = url
    #host_name = urlparse.urlparse(host_url).hostname
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()

    params['Signature'] = createSign(params, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path
    return http_get_request(url, params)


def api_key_post(url, request_path, params, ACCESS_KEY, SECRET_KEY):
    method = 'POST'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {'AccessKeyId': ACCESS_KEY,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp}

    host_url = url
    #host_name = urlparse.urlparse(host_url).hostname
    host_name = urllib.parse.urlparse(host_url).hostname
    host_name = host_name.lower()
    params_to_sign['Signature'] = createSign(params_to_sign, method, host_name, request_path, SECRET_KEY)
    url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
    return http_post_request(url, params)

def get_price(symbol):
    url = 'https://api.huobi.pro/market/trade'
    para={}
    if symbol.lower().find('usdt')==-1:
        para['symbol'] = symbol.lower() + 'usdt'
    else:
        para['symbol'] = symbol.lower()
    data = http_get_request(url, para)
    data = data['tick']['data'][0]
    price = data['price']
    # print("%s 当前价格为：%s"%(symbol, price))
    return price



def encropt(field):
    AccessKeyId = "AccessKeyId=" + ACCESS_KEY
    SignatureMethod = "SignatureMethod=" + "HmacSHA256"
    SignatureVersion = "SignatureVersion=" + "2"
    Timestamp = "Timestamp=" + quote1(
        time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(int(round(time.time() * 1000)) / 1000)))
    s = sorted([AccessKeyId, SignatureMethod, SignatureVersion, Timestamp])
    # print("Sorted Keys:", "&".join(s))
    strings = ['GET', 'api.huobi.pro', field, "&".join(s)]
    sigStr = get_signature(SECRET_KEY, "\n".join(strings))
    return sigStr, "&".join(s)

def get_account():
    url = "https://api.huobi.pro"
    re_path = '/v1/account/accounts'
    data = api_key_get(url, re_path, {}, ACCESS_KEY, SECRET_KEY)
    return [x for x in data['data'] if x['type']=='spot'][0]


def get_balance():
    url = "https://api.huobi.pro"
    request_path = '/v1/account/accounts/%s/balance'%get_account()['id']
    data = api_key_get(url, request_path, {}, ACCESS_KEY, SECRET_KEY)
    balances = []
    for i in data['data']['list']:
        if float(i['balance']) > 0:
            balances.append(i)
    return balances


def get_open_order():
    url = "https://api.huobi.pro"
    re_path = '/v1/order/openOrders'
    data = api_key_get(url, re_path, {'symbol':'xmrusdt'}, ACCESS_KEY, SECRET_KEY)
    return data['data']


def get_order():
    url = "https://api.huobi.pro"
    re_path = '/v1/order/orders'
    data = api_key_get(url, re_path, {'symbol':'xmrusdt', 'states':'canceled,partial-canceled,filled,partial-filled'}, ACCESS_KEY, SECRET_KEY)
    return data['data']

def get_order_detail():
    url = "https://api.huobi.pro"
    re_path = '/v1/order/orders/%s'%(get_order()[0]['id'])
    data = api_key_get(url, re_path, {'symbol':'xmrusdt'}, ACCESS_KEY, SECRET_KEY)
    return data['data']

def get_order_deal_history():
    url = "https://api.huobi.pro"
    re_path = '/v1/order/matchresults'
    data = api_key_get(url, re_path, {'symbol':'xmrusdt'}, ACCESS_KEY, SECRET_KEY)
    print(data)
    return data['data']

def generate_order_id():
    with open('order-id.txt','r',encoding='utf8') as f:
        existOrderID = [x.strip() for x in f.readlines()]
    length = random.randint(16,32)
    oid = ""
    for i in range(length):
        oid+=str(random.randint(0,9))
    while oid in existOrderID:
        oid = (oid + str(random.randint(0,9)))[:-1]
    return oid

def order(symbol, type, amount, price=0):
    url = "https://api.huobi.pro"
    re_path = '/v1/order/orders/place'
    # id = generate_order_id()
    paras = {
        'account-id':get_account()['id'],
        'symbol':symbol,
        'type': type,
        'price': price,
        'amount':amount,
        'source':'spot-api',
        # 'client-order-id':'24ir043iao3ada'
    }
    if type.find('market') == -1:
        paras['price'] = price
    # print(paras)
    data = api_key_post(url, re_path, paras, ACCESS_KEY, SECRET_KEY)
    # data = eval(str(data))
    paras['status'] = data['status']
    paras['data'] = data['data']
    paras['timestamp'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    save_order_detail_once(paras)
    save_trade_log_once(symbol[:-4], {symbol[:-4]:{'price':price, 'amount':amount}})
    # return data['data']


def save_order_detail_once(para):
    print(para)
    string = json.dumps(para, indent=4)
    with open('trade_log/%s-%s-%s.txt'%(para['symbol'], para['data'], para['timestamp']), 'w', encoding='utf8') as log:
        log.write(string)

def load_trade_log_once(code):
    with open('trade_log/%s-log.txt'%code, 'r', encoding='utf8') as f:
        return json.load(f)


def save_trade_log_once(code, para):
    with open('trade_log/%s-log.txt'%code, 'w', encoding='utf8') as f:
        string = json.dumps(para, indent=4)
        f.write(string)

def load_gaps():
    with open('trade_log/gaps.txt', 'r', encoding='utf8') as f:
        return json.load(f)

def load_rates(type):
    with open('trade_log/%s_rates.txt'%type, 'r', encoding='utf8') as f:
        return json.load(f)

def save_rates_once(rates, type):
    string = json.dumps(rates, indent=4)
    with open('trade_log/%s_rates.txt'%type, 'w', encoding='utf8') as log:
        log.write(string)


def get_order_type(symbol):
    type_freq={
        'buy':0,
        'sell':0
    }
    for log in [x for x in os.listdir('trade_log') if len(x)>20 and x.find(symbol)!=-1]:
        with open('trade_log/' + log, 'r', encoding='utf8') as log:
            l = json.load(log)
            if l['type'].find('sell')!=-1:
                type_freq['sell'] += 1
            else:
                type_freq['buy'] += 1
    return type_freq

def grid_bs(codes=['shib']):
    start = time.time()

    gaps = load_gaps()
    operate_prices = {symbol:load_trade_log_once(symbol)[symbol]['price'] for symbol in codes }
    count = 0
    buy_times = {symbol:get_order_type(symbol)['buy'] for symbol in codes}
    sell_times = {symbol:get_order_type(symbol)['sell'] for symbol in codes}
    buy_rates = load_rates('buy')
    sell_rates = load_rates('sell')
    while True:
        for symbol in codes:
            count += 1
            time.sleep(1)
            gap = gaps[symbol]
            operate_price = operate_prices[symbol]
            buy_rate = buy_rates[symbol]
            sell_rate = sell_rates[symbol]
            try:
                price_now = get_price(symbol)
                if count % 3 == 0:
                    print("\r价格%s, 交易:[buy:%s, sell:%s], 运行时间：%s, GAP:%s, BUY_RATE:%s, SELL_RATE:%s, OP_Pirce:%s" %
                          (price_now, buy_times[symbol], sell_times[symbol], round(time.time() - start), round(gap, 8), buy_rate,
                           sell_rate, operate_price), end='...')
                # if count % 3600 == 0:
                    # print("\r%s:【Pirce:%s, Gap:%s, Operate:%s】 " % (code, price_now, gap, operate_price))
                if price_now < operate_price - gap * buy_rate:
                    sell_rates[symbol] = 3
                    buy_rates[symbol] *= 1.2
                    save_rates_once(sell_rates, 'sell')
                    save_rates_once(buy_rates, 'buy')
                    buy_price = round(operate_price - gap, 8)
                    buy_amount = round(8/buy_price)
                    while buy_price * buy_amount < 5:
                        buy_amount *= 1.02
                    buy_amount = round(buy_amount)
                    order(symbol+'usdt', 'buy-limit', buy_amount, price_now)
                    print("\r [%s] Price  Now:%s, Operate_price:%s" % (BeijingTime('%Y-%m-%dT%H:%M:%S'), price_now, buy_price))
                    operate_prices[symbol] = buy_price
                    time.sleep(0.2)
                    buy_times[symbol] += 1

                if price_now > operate_price + gap * sell_rate:
                    buy_rates[symbol] = 1.2
                    sell_rate[symbol] *= 1.2
                    save_rates_once(sell_rates, 'sell')
                    save_rates_once(buy_rates, 'buy')
                    sell_price = round(operate_price + gap, 8)
                    sell_amount = round(6/sell_price)
                    while sell_price * sell_amount < 5.1:
                        sell_amount *= 1.02
                    sell_amount = round(sell_amount)
                    # if code[:3] == '513':
                    #     sell_amount = 300
                    order(symbol+'usdt', 'sell-limit', sell_amount, price_now)
                    print("\r [%s] Price  Now:%s, Operate_price:%s" % (BeijingTime('%Y-%m-%dT%H:%M:%S'), price_now, sell_price))
                    operate_prices[symbol] = sell_price
                    time.sleep(0.2)
                    sell_times[symbol] += 1
            except KeyError as e:
                print(e)
                break



if __name__ == '__main__':
    # for i in range(10):
    #     time.sleep(1)
    #     print(get_price_eth())

    # print(get_account())
    # for i in get_balance():
    #     print(i)
    grid_bs()
    # order('shibusdt', 'sell-market', 1000000, 7.77e-06)
    # print(get_price('shib'))