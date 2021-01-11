from DataEngine.Data import *
# from DataEngine.Mysql import *

if __name__ == '__main__':
    # data = get_tick_price('002558', '15')
    data = get_tick_price('600104','15')
    cost = 0
    amount = 0

    use_able = amount
    money = 80000
    start = data[0][1][0]
    all_price = []
    d_gap = 0.97
    u_gap = 1.03
    op = []
    flag = True
    for x in data:
        time = x[0]
        price = x[1]
        for p in price:
            if p <= start * d_gap or flag:
                if flag:
                    flag = False
                if money > pow(2, len(op)) * p:
                    print(time)
                    op.append(pow(2, len(op)) * 100)
                    start = p
                    cost = (cost * amount + start * op[-1]) / (amount + op[-1])
                    amount += op[-1]
                    print('Buy:', start, round(cost, 2), amount)
                    money -= start * op[-1]
                    print(time , op, round(money,1), '\n-------')
            if p >= start * u_gap:
                if len(op) > 1:
                    print(time)
                    start = p
                    cost = (cost * amount - start * op[-1]) / (amount - op[-1])
                    money += start * op[-1]
                    amount -= op[-1]
                    op = op[:-1]
                    print('Sell:', start, round(cost, 2), amount)
                    print(time , op, round(money,1), '\n-------')
                elif len(op) == 1:
                    start = p
                    print("卖光了都！\n--------")
                    continue
            # print("\n===========\n")
            # all_price.append(p)
    print(money +  data[-1][-1][-1] * amount)

    print(fund_basic())


