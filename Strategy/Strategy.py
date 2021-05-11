"""
交易策略模型
起码几十种
但是还没想好
怎么对接进去
先不管了睡觉
"""

import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime, timedelta
from DataEngine.Data import get_pro_stock_basic
from DataEngine.Neo4j import get_Graph
from DataEngine.Mysql import get_all_columns_with_label


#直线方程
def f_1(x, a, b):
    return a * x +b

# 二次曲线方程
def f_2(x, A, B, C):
    return A * x * x + B * x + C

# 三次曲线方程
def f_3(x, A, B, C, D ):
    return A * x * x * x + B * x * x + C * x + D

def func_sin(x, A, k, theta):
    """
    数据拟合所用的函数: A*cos(2*pi*k*x + theta)
    """
    return A * np.sin(k * x + theta)


def nihe(data):
    if type(data[0]) == str:
        data = [float(x) for x in data]
    x0 = np.linspace(0, len(data), len(data))
    y0 = data
    func = [f_2, f_3, func_sin]
    offset_min = 10000000
    func_min_offset = -1
    para_min_offset = []
    for f in range(len(func)):
        x2 = np.arange(0, len(data), len(data))
        try:
            para = curve_fit(func[f], x0, y0)[0]
        except Exception as e:
            # print(e)
            return 0,0,-1
        if f == 0:
            A, B, C = para
            y2 = func[f](x2, A, B, C)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 1:
            A, B, C, D = para
            y2 = func[f](x2, A, B, C, D)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 2:
            try:
                A, B, C = para
            except Exception as e:
                print("!!!!!",para,e)
            y2 = func[f](x2, A, B, C)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
        elif f == 3:
            A, B = para
            y2 = func[f](x2, A, B)
            offset = np.sqrt(np.sum(np.square(y0 - y2)))
            if offset < offset_min:
                offset_min = offset
                para_min_offset = para
                func_min_offset = f
    return para_min_offset, func[func_min_offset], func_min_offset



def main():
    # su = simulation_User()
    # user = User(su)
    # pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    # all_data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # ts_code = list(all_data.ts_code)
    # symbol = list(all_data.symbol)


    realtime_Price = [
                      17.70, 17.92, 17.71, 17.84, 17.97,
                      17.91, 17.96, 18.06, 18.11, 18.12,
                      18.18, 18.28, 18.47, 18.45, 18.36,
                      18.45, 18.48, 18.64, 18.69, 18.67,
                      18.56, 18.60, 18.46, 18.46, 18.44,
                      18.35, 18.38, 18.39, 18.31, 18.16,
                      18.16, 18.10, 18.17, 18.29, 18.14,
                      18.23, 18.15, 18.17, 18.24, 18.16,
                      17.99, 17.91, 17.86, 17.89, 17.88,
                    17.70, 17.92, 17.71, 17.84, 17.97,
                    17.91, 17.96, 18.06, 18.11, 18.12,
                    18.18, 18.28, 18.47, 18.45, 18.36,
                    18.45, 18.48, 18.64, 18.69, 18.67,
                    18.56, 18.60, 18.46, 18.46, 18.44,
                    18.35, 18.38, 18.39, 18.31, 18.16,
                    18.16, 18.10, 18.17, 18.29, 18.14,
                    18.23, 18.15, 18.17, 18.24, 18.16,
                    17.99, 17.91, 17.86, 17.89, 17.88
                      ]
    # print(su.position)
    data = realtime_Price[:20]
    para, func, func_min_offset = nihe(data)
    if para == 0:
        return
    x2 = np.arange(0, len(data) + 20)
    y2 = None
    print(para, func_min_offset)
    if func_min_offset == 0:
        A, B, C = para
        y2 = func(x2, A, B, C)
    elif func_min_offset == 1:
        A, B, C, D = para
        y2 = func(x2, A, B, C, D)
    elif func_min_offset == 2:
        A, B, C = para
        y2 = func(x2, A, B, C)

    if max(y2) != y2[-1]:
        max_y2 = max(y2)
        print("Max_y2:%s" % max_y2)
        for x in range(len(y2[-20:])):
            if y2[-20 + x] == max_y2:
                print("卖出点在：%s, 时间为：%s" % (max_y2, datetime.now() + timedelta(minutes=2 * x)))
    elif min(y2) != y2[-1]:
        min_y2 = min(y2)
        print("Min_y2:%s"%min_y2)
        for x in range(len(y2[-20:])):
            if y2[-20 + x] == min_y2:
                print("买入点在：%s, 时间为：%s" % (min_y2, datetime.now() + timedelta(minutes=2 * x)))
    else:
        if max(y2) < y2[len(data)]:
            print("持续下行中！！")
        else:
            print("持续上升中！！")

if __name__ == '__main__':
    main()

