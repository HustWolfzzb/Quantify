def spy_price():
    start = True
    # p = get_all_price()
    # price_close = [p[x]['close'] for x in codes]
    # buy_amount = [[] for x in range(len(codes))]
    # sell_amount =[[] for x in range(len(codes))]
    price = [1.431, 1.429, 1.427, 1.425, 1.423, 1.421, 1.419, 1.417, 1.415, 1.413, 1.411, 1.409, 1.407,
             1.405, 1.408, 1.411, 1.414, 1.417, 1.42, 1.423, 1.426, 1.429, 1.432,
             1.435, 1.433, 1.431, 1.429, 1.427, 1.425, 1.423, 1.421, 1.419, 1.417,
             1.415, 1.417, 1.419, 1.421,
             1.421, 1.416, 1.411, 1.406, 1.401, 1.396,
             1.397, 1.398, 1.399, 1.4, 1.401, 1.402, 1.403, 1.404, 1.405, 1.406, 1.407, 1.408, 1.409]
    cou = 0
    price_close = [1.431, 1.196, 1.814, 1.312]
    close_price = price_close[0]
    operate_price = close_price
    use = 5500
    money = operate_price * use
    buy_amount = 100
    sell_amount = 100
    while True:
        if cou >= len(price):
            break
        # p = get_all_price()
        # price_now = [p[x]['now'] for x in codes]
        price_now = [price[cou], ]
        cou += 1
        
        for code_idx in range(len(codes[0:1])):
            code = codes[code_idx]
            now_price = price_now[code_idx]
            gap = change_[code_idx]
            if start:
                start = False
                # print("挂 Sell %s, %s, %s, %s" % (names[code_idx], close_price + gap, 100 , round(now_price / price_close[code_idx], 3)))
                # open_sell[codes[code_idx]].append(user.sell(codes[code_idx], now_price, amount))
                # print("挂 Buy %s, %s, %s, %s" % (names[code_idx], close_price - gap, 100 , round(now_price / price_close[code_idx], 3)))
                # open_sell[codes[code_idx]].append(user.sell(codes[code_idx], now_price, amount))

            if now_price >= operate_price + gap:
                use -= sell_amount
                print("价格：%s, 数量：%s的卖单 成交！" % (operate_price + gap, sell_amount))
                buy_amount = get_amount(now_price, close_price, gap)
                sell_amount = get_amount(now_price + gap, close_price, gap)
                operate_price = now_price
                # open_sell[codes[code_idx]].append(user.sell(codes[code_idx], now_price , amount))
                # print("挂 Sell %s, %s, %s, %s" % (names[code_idx], now_price + gap, sell_amount, round(now_price / price_close[code_idx], 3)))
                #  open_buy.append(user.sell(codes[code_idx], price , pow(2,i) * 100))
                # print("挂 Buy %s, %s, %s, %s" % (names[code_idx], now_price - gap, buy_amount, round(now_price / price_close[code_idx], 3)))
            elif now_price <= operate_price - gap:
                use += buy_amount
                print("价格：%s, 数量：%s的买单单 成交！" % (operate_price - gap, buy_amount))
                buy_amount = get_amount(now_price - gap, close_price, gap)
                sell_amount = get_amount(now_price , close_price, gap)
                operate_price = now_price
                # open_sell[codes[code_idx]].append(user.sell(codes[code_idx], now_price , amount))
                # print("挂 Sell %s, %s, %s, %s" % (names[code_idx], now_price + gap, sell_amount, round(now_price / price_close[code_idx], 3)))
                #  open_buy.append(user.sell(codes[code_idx], price , pow(2,i) * 100))
                # print("挂 Buy %s, %s, %s, %s" % (names[code_idx], now_price - gap, buy_amount, round(now_price / price_close[code_idx], 3)))
    print("现在%s手" % use)