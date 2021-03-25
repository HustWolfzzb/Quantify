
def Average(data,index,target, num):
    try:
        round(sum(data[index][target - num:target]) / num, 2)
    except Exception as e:
        print("均值计算出了问题",e)


def Momentum(data,index,target, num):
    try:
        round((data[index][target] - data[index][target-num])/data[index][target-num] * 100, 2)
    except Exception as e:
        print("变动率（动量）计算出了问题",e)

