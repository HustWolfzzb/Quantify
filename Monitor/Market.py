import time
from DataEngine.Data import pro, get_pro_stock_basic, get_concept, get_index_basic, \
    get_stock_concepts
import matplotlib.pyplot as plt
import matplotlib
# 设置中文字体和负号正常显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


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
    plt.ylim(min(num_list1) * 1.1, max(num_list1) * 1.1)     # y轴取值范围
    plt.ylabel("涨幅", fontsize=15)
    """
    设置x轴刻度显示值
    参数一：中点坐标
    参数二：显示值
    """
    plt.xticks([index + 0.2 for index in x], label_list)
    plt.xticks(size='small', rotation=90, fontsize=12)

    plt.xlabel(name, fontsize=20)
    plt.title("%s-涨幅"%name, fontsize=len(label_list))
    plt.legend()     # 设置题注
    # 编辑文本
    # for rect in rects1:
    #     height = rect.get_height()
    #     plt.text(rect.get_x() + rect.get_width() / 2, height+1, str(height), ha="center", va="bottom")
    plt.savefig('%s.png'%name)
    plt.show()

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


# index_basic = get_index_basic()

