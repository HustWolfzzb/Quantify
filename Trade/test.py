def abs_reduce(x, y):
    if x > y:
        return x - y
    else:
        return y - x



def test_600036():
    money = 100000
    amount = 0
    operate_price = 0
    gap = 0
    buy_amount_base = 100
    sell_amount_base = 100
    close = 0
    with open('../招行.txt','r') as f:
        start = 0
        for line in f.readlines():
            date, data = line.split(':')
            price =  [float(x) for x in data[1:-2].strip().split(', ')]
            # print(len(price))
            if start == 0:
                amount = 2000
                money -= amount * price[0]
                operate_price = price[0]
                start = 1
                gap = operate_price * 0.01
                close = price[-1]
            print('\n============' + date + '============')
            for price_now in price:
                if amount == 0:
                    buy_price = round(price_now, 3)
                    # buy_amount = buy_amount_base
                    buy_amount =  1000
                    if money < price_now * buy_amount:
                        continue
                    money -= price_now * buy_amount
                    amount += buy_amount
                    operate_price = buy_price
                    print("- Buy Price:%s, amount:%s. Stock:%s, Money:%s, Position: %s" % (
                    price_now, buy_amount, amount, money, money + amount * price_now))
                    continue

                if price_now < operate_price - gap:
                    buy_price = round(operate_price - gap, 3)
                    # buy_amount = buy_amount_base
                    buy_amount = buy_amount_base * int(abs_reduce(price_now, close) // (gap * 3) + 1)
                    if money < price_now * buy_amount:
                        continue
                    money -= price_now * buy_amount
                    amount += buy_amount
                    operate_price = buy_price
                    print(" Buy Price:%s, amount:%s. Stock:%s, Money:%s, Position: %s" % (price_now, buy_amount, amount, money, money + amount * price_now ))

                if price_now > operate_price + gap * 1.5:
                    sell_price = round(operate_price + gap, 3)
                    sell_amount = sell_amount_base * int(abs_reduce(price_now, close) // (gap * 3) + 1)
                    if amount < sell_amount:
                        continue
                    money += price_now * sell_amount
                    amount -= sell_amount
                    operate_price = sell_price
                    print("Sell Price:%s, amount:%s. Stock:%s, Money:%s, Position: %s" % (price_now, sell_amount, amount, money, money + amount * price_now ))

            close = price[-1]
            gap = close *  0.02
        print(money + amount * close)

if __name__ == '__main__':
    test_600036()