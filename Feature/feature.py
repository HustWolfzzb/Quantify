import numpy as np

def RSI(data, index, target, num,):
    """
     :param data: tushare获取的数据
    :param target: 指定的列
    :param target: 目标位置
    :param num: 对应的X日参数
    :return:  RSI值
    """
    if target < num:
        return -1
    up = 0
    down = 0
    up = 0
    down = 0
    for i in range(target - num, target):
        if data.loc[i,index] > 0:
            up += data.loc[i,index]
        else:
            down += data.loc[i, index]
    # for i in range(index, len(data))
    #     if data.loc[index, 'change'] > 0:
    #         up = data.loc[index - 1, 'RSI-'+str(period)] * (period -1) + data.loc[index, 'change']
    #     else:
    #         down = data.loc[index - 1, 'RSI-'+str(period)] * (period -1) -  data.loc[index, 'change']
    if down == 0:
        rsi = 50
    else:
        rsi = 100 - 100 / (1 + abs(up / down))
    return rsi

def Average(data,index,target, num):
    """
    :param data: tushare获取的数据
    :param index: 指定的列
    :param target: 目标位置
    :param num: 对应的X日参数
    :return: 根据给定index 在 data数据中 在索引target的num日的平均收盘价
    """
    if target < num:
        return -1
    try:
        return round(sum(data[index][target - num:target]) / num, 2)
    except Exception as e:
        return 0
        print("均值计算出了问题",e)


def Momentum(data,index,target, num):
    """
    :param data: tushare获取的数据
    :param index: 指定的列
    :param target: 目标位置
    :param num: 对应的X日参数
    :return: 根据给定index 在 data数据中 在索引target的num日的动量值
    """
    if target < num:
        return -1
    try:
        return round((data[index][target] - data[index][target-num])/data[index][target-num] * 100, 2)
    except Exception as e:
        return 0
        print("变动率（动量）计算出了问题",e)


def Standard_Deviation(data,index,target, num):
    """
    标准差
    :param data: tushare获取的数据
    :param index: 指定的列
    :param target: 目标位置
    :param num: 对应的X日参数
    :return: 根据给定index 在 data数据中 索引target 的num日的数值残差
    """
    return np.std(data[index][target-num:target])


def Bollingger_Band(data,index,target, num):
    """
    布林线的理论使用原则是：当股价穿越最外面的压力线（支撑线）时,表示卖点（买点）出现。当股价延着压 力线（支撑线）上升（下降）运行,虽然股价并未穿越,但若回头突破第二条线即是卖点或买点。　　
    布林线指标
    （1）股价由下向上穿越下轨线(LOWER)时,可视为买进信号。　　
    （2）股价由下向上穿越中轨时,股价将加速上扬,是加仓买进的信号。　　
    （3）股价在中轨与上轨(UPER)之间波动运行时为多头市场,可持股观望。　　
    （4）股价长时间在中轨与上轨(UPER)间运行后,由上向下跌破中轨为卖出信号。　　
    （5）股价在中轨与下轨(LOWER)之间向下波动运行时为空头市场,此时投资者应持币观望。　　
    （6）布林中轨经长期大幅下跌后转平,出现向上的拐点,且股价在2～3日内均在中轨之上。此时,若股价回调,其回档低点往往是适量低吸的中短线切入点。　　
    （7）对于在布林中轨与上轨之间运作的强势股,不妨以回抽中轨作为低吸买点,并以中轨作为其重要的止盈、止损线。　　　
    （8）飚升股往往股价会短期冲出布林线上轨运行,一旦冲出上轨过多,而成交量又无法持续放出,注意短线高抛了结,如果由上轨外回落跌破上轨,此时也是一个卖点。
    :param data: tushare获取的数据
    :param index: 指定的列
    :param target: 目标位置
    :param num: 对应的X日参数
    :return:
    """
    MA1 = Average(data, index, target, num)
    MO2 = Momentum(data, index, target, num)
    MO1 = Momentum(data, index, target, num//2)
    std = Standard_Deviation(data,index, target, num)
    Uper = MA1 + 2*std
    Lower = MA1 - 2*std
    if data['close'][target-1]<Lower and data['close'][target]>Lower and MO1>MO2 and MO1>0:
        return "Buy"
    if data['close'][target - 1] < MA1 and data['close'][target] > MA1 and MO1>MO2 and MO1>0:
        return "Add"
    if data['close'][target - 1] > MA1 and data['close'][target] < MA1:
        return "Reduce"
    if data['close'][target - 1] < Uper and data['close'][target] > Uper:
        return "Sell"
    else:
        return 'Wait'




