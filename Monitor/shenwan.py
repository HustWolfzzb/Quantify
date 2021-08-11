import json
import time

from DataEngine.Data import pro, get_stock_shenwan_classify, get_stock_name


def save_dict(dic, path):
    string = json.dumps(dic, indent=4)
    with open(path, 'w', encoding='utf8') as log:
        log.write(string)


def load_dict(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)

stock_name = get_stock_name()

s1 = pro.index_classify(level='L1', src='SW')
s2 = pro.index_classify(level='L2', src='SW')
s3 = pro.index_classify(level='L3', src='SW')

classify2name = {}
name2classify = {}
classify2stock = {}
stock2classify = {}

for i in s1.index:
    code = s1.loc[i, 'index_code']
    name = s1.loc[i, 'industry_name']
    classify2name[code] = name
    name2classify[name] = code
for i in s2.index:
    code = s2.loc[i, 'index_code']
    name = s2.loc[i, 'industry_name']
    classify2name[code] = name
    name2classify[name] = code

for i in s3.index:
    code = s3.loc[i, 'index_code']
    name = s3.loc[i, 'industry_name']
    classify2name[code] = name
    name2classify[name] = code


def get_classify():
    classify_codes = list(s3['index_code'])
    count = 0
    while count < len(classify_codes):
        i = classify_codes[count]
        try:
            data = get_stock_shenwan_classify(i)
            count += 1
        except Exception as e:
            time.sleep(60)
            continue
        index_code = data['index_code'].to_list()
        con_code = data['con_code'].to_list()
        for i in range(len(index_code)):
            idx = index_code[i]
            cdx = con_code[i]
            if not classify2stock.get(idx):
                classify2stock[idx] = set()
            classify2stock[idx].add(cdx)
            if not stock2classify.get(cdx):
                stock2classify[cdx] = set()
            stock2classify[cdx].add(idx)

        if count % 100 == 0:
            print("\r【%s%s%s】" % (
            '>>' * int(count * 100 // len(classify_codes)),
            int(count * 100 // len(classify_codes)),
            '=' * (100 - int(count // len(classify_codes)))))
            time.sleep(60)


    code1 = classify2stock.keys()
    code2 = stock2classify.keys()

    for i in code1:
        classify2stock[i] = list(classify2stock[i])
    for j in code2:
        stock2classify[j] = list(stock2classify[j])


    # print(classify2stock)
    save_dict(classify2stock, 'classify/classify2stock.txt')
    # print(stock2classify)
    save_dict(stock2classify, 'classify/stock2classify.txt')

def read_classify():
    classify2stock = load_dict('classify/classify2stock.txt')
    stock2classify = load_dict('classify/stock2classify.txt')
    return classify2stock, stock2classify, stock_name, classify2name