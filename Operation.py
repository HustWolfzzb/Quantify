import tushare as ts

from datetime import datetime, time
from time import sleep
import numpy as np
from Strategy import nihe, f_2

# 程序运行时间在白天8:30 到 15:30  晚上20:30 到 凌晨 2:30
DAY_START = time(9, 30)
DAY_END = time(11, 30)

AFTERNOON_START = time(13, 00)
AFTERNOON_END = time(15, 00)

symbol = ["002164","002517","002457","600723","600918","600720","603187","002271","000759","000735","601933"]
stock_name =["宁波东力","恺英网络","青龙管业","首商股份","中泰证券","祁连山","海容冷链","东方雨虹","中百集团","罗牛山","永辉超市"]
stock_code = { symbol[x]:stock_name[x] for x in range(len(symbol))}
def is_openMartket():
    current_time = datetime.now().time()
    if not ((current_time > DAY_START and current_time < AFTERNOON_END )):
        return -1
    elif not ((current_time > DAY_START and current_time < DAY_END) or (current_time >AFTERNOON_START and current_time < AFTERNOON_END )):
        return 0
    return 1


def main():
    tick_data = {}
    for s in symbol:
        tick_data[s] = []
    while(True):
        time = is_openMartket()
        if time == -1:
            break
        if time == 0:
            sleep(120)
            continue
        sleep(120)
        realtimeData = list(ts.get_realtime_quotes(symbol).price)
        for idx in range(len(realtimeData)):
            data = tick_data[symbol[idx]]
            data.append(realtimeData[idx])
            print(datetime.now().isoformat().replace('T',"  "))
            if len(data) < 8:
                sleep(120//len(symbol))
                continue
            A2, B2, C2 = nihe(data)
            x2 = np.arange(0, len(data) + 20)
            y2 = f_2(x2, A2, B2, C2)
            if max(y2) != y2[-1]:
                print("卖出点在：%s" % max(y2))
            elif min(y2) != y2[-1]:
                print("买入点在：%s"% min(y2))
            else:
                if max(y2) < y2[len(data)]:
                    print("持续下行中！！")
                else:
                    print("持续上升中！！")
    for s in symbol:
        with open('tickData/%s-%s.txt'%(stock_code[s],s), 'a', encoding='utf8') as out:
            out.write("时间：%s\n"%datetime.now().isoformat())
            out.write(", ".join(tick_data[s]))
            out.write("\n")


if __name__ == '__main__':
    main()
