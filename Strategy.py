"""
交易策略模型
起码几十种
但是还没想好
怎么对接进去
先不管了睡觉
"""
from Entity import User,Stock
import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import leastsq


class simulation_User():
    balance = {
                       '资金余额': 100,
                       '可用金额': 4000,
                       '可取金额': 30,
                       '总资产': 5100,
              }
    position = [{
        '证券代码': '600100',
        '可用股份': 400,
        '冻结股份': 200,
        '成本价格': 19.40,
        '市场价': 17.88
    },
        {
            '证券代码': '600220',
            '可用股份': 400,
            '冻结股份': 400,
            '成本价格': 11.79,
            '市场价': 11.28
        }
    ]
    def __index__(self):
        print("初始化一个模拟器")




def func_sin(x, p):
    """
    数据拟合所用的函数: A*cos(2*pi*k*x + theta)
    """
    A, k, theta = p
    return A * np.sin(k * x + theta)

#直线方程
def f_1(x, a, b ):
    return a * x +b


# 二次曲线方程
def f_2(x, A, B, C):
    return A * x * x + B * x + C

# 三次曲线方程
def f_3(x, A, B, C, D ):
    return A * x * x * x + B * x * x + C * x + D

def residuals(p, y, x, fun):
    """
    实验数据x, y和拟合函数之间的差，p为拟合需要找到的系数
    """
    return y - fun(x, p)

def nihe(data):
    if type(data[0]) == str:
        data = [float(x) for x in data]
    x0 = np.linspace(0, len(data), len(data))
    y0 = data
    A2, B2, C2 = curve_fit(f_2, x0, y0)[0]
    x2 = np.arange(0, len(data), len(data))
    y2 = A2 * x2 * x2 + B2 * x2 + C2
    print("偏差值",np.sqrt(np.sum(np.square(y0 - y2))))
    return A2, B2, C2


def main():
    # su = simulation_User()
    # user = User(su)
    # pro = ts.pro_api('4b98f5087a086ac0e0d759ce67daeb8a2de2773e12553e3989b303dd')
    # all_data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    # ts_code = list(all_data.ts_code)
    # symbol = list(all_data.symbol)


    realtime_Price = [17.70,17.92,17.71,17.84,17.97,
                      17.91,17.96,18.06,18.11,18.12,
                      18.18,18.28,18.47,18.45,18.36,
                      18.45,18.48,18.64,18.69,18.67,
                      18.56,18.60,18.46,18.46,18.44,
                      18.35,18.38,18.39,18.31,18.16,
                      18.16,18.10,18.17,18.29,18.14,
                      18.23,18.15,18.17,18.24,18.16,
                      17.99,17.91,17.86,17.89,17.88]
    # print(su.position)
    data = realtime_Price[:50]
    A2, B2, C2 = nihe(data)
    x2 = np.arange(0, len(data) + 10)
    y2 = f_2(x2, A2, B2, C2)
    if max(y2) != y2[-1]:
        print("卖出点在：%s"%max(y2))
    else:
        print("持续上升中！！")
        print(y2)

if __name__ == '__main__':
    main()