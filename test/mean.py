import datetime

import numpy as np
import pandas as pd
import quick_stock as quick_stock
import talib
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc


def macd(close_prices):
    # 计算kd指标
    macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=10, fastmatype=1, slowperiod=23,
                                            slowmatype=1,
                                            signalperiod=8, signalmatype=1)
    macd = macd * 2
    return (macdDIFF, macdDEA, macd)


def compute(title, code):
    sz50 = quick_stock.TradeIndexClient().daily(code)  # 深证50
    sz50 = pd.DataFrame(sz50)
    macdDIFF, macdDEA, macdMacd = macd(sz50["end"])

    return {
        "title": title,
        "data": sz50,
        "macd": macdMacd,
        "diff": macdDIFF,
        "dea": macdDEA,
    }


def draw(data, fig, i):
    # sz50 = quick_stock.TradeIndexClient().daily(code)  # 深证50
    sz50 = pd.DataFrame(data["data"])
    # mac, signal, hist = macd(sz50["end"])
    mac = data["macd"]
    hist = data["diff"]
    signal = data["dea"]

    dates = sz50["date_at"][-120:]
    open_prices = sz50["start"][-120:]
    high_prices = sz50["max"][-120:]
    low_prices = sz50["min"][-120:]
    close_prices = sz50["end"][-120:]
    ax1 = fig.add_subplot(7, 2, i)
    i = i + 1
    candlestick_ohlc(ax1, zip(np.arange(1, len(dates)), open_prices, high_prices, low_prices, close_prices), width=0.6,
                     colorup='g',
                     colordown='r')
    ax1.set_title(data["title"])
    ax1.set_ylabel('price')

    ax2 = fig.add_subplot(7, 2, i)
    i = i + 1
    # 绘制MAC柱状图
    mac = mac[-120:]
    signal = signal[-120:]
    hist = hist[-120:]
    ax2.bar(dates, mac, color='#f059c6')
    ax2.set_title('macd')
    ax2.set_xlabel('date')
    ax2.set_ylabel('macd')

    ax3 = ax2.twinx()
    ax3.plot(dates, signal, color='red', label='Histogram')
    ax4 = ax2.twinx()
    ax4.plot(dates, hist, color='#339958', label='Histogram')
    return fig, i


if __name__ == '__main__':
    # indexes = quick_stock.TradeIndexClient().get_all_index()
    # print(indexes[indexes[""] ==""][:20])

    # data = []
    # data.append(compute("sz50", "0.399850"))
    # data.append(compute("a50", "1.000016"))
    # data.append(compute("kc50", "1.000688"))
    # data.append(compute("hs300", "1.000300"))
    # data.append(compute("zz500", "1.000905"))
    # data.append(compute("zz1000", "1.000852"))
    # data.append(compute("zz2000", "2.932000"))
    #
    # fig = plt.figure(figsize=(20, 16), )
    # i = 1
    # for item in data:
    #     fig, i = draw(item, fig, i)
    # plt.tight_layout()
    # plt.show()

    # all_concept = quick_stock.TradeConceptClient().get_all_concept()
    #
    # # 总结macd 特性用来判断反转
    # # macd 向上，但是当天股价下跌。看3天后股价
    # for row in all_concept.itertuples():
    #     df = quick_stock.TradeConceptClient().weekly(row.code)
    #     macdDIFF, macdDEA, macdMacd = macd(df["end"])
    #
    #     if macdDIFF.iloc[-1] > macdDIFF.iloc[-2] and macdMacd.iloc[-1] > macdMacd.iloc[-2]:
    #         print(row)
    #
    # print(11)


    # 指数
    cmax = {}
    for mean in range(12, 13):
        for row in ["1.000688" ]:
            for mean2 in range(11, 12):
            # for row in ["0.399850","1.000016","1.000688","1.000300","1.000905","1.000852","2.932000" ]:

                df = quick_stock.TradeIndexClient().daily(row)
                df = pd.DataFrame(df)
                end = df['end'].rolling(window=mean).mean()
                end2 = df['end'].rolling(window=mean2).mean()
                max = len(end) - 1
                buy = 0
                amount = 0
                buys = 0
                buys2 = 0
                for index, value in enumerate(end):
                    if df["date_at"][index] < '2024-01-01':
                        continue
                    if np.isnan(value):
                        continue
                    # if index +1  > max:
                    #     continue

                    if value < df['end'][index] and buy == 0:
                        print("sell", df["date_at"][index], buy)
                        buy = df["end"][index]

                    if df['end'][index] < end2[index] and buy > 0:

                        # print(macdMacd[index], macdMacd[index + 1], macdMacd[index + 2])
                        buy = df["end"][index] - buy
                        if buy > 0:
                            buys +=1
                        else:
                            buys2 += 1
                        print("sell", df["date_at"][index], buy, end2[index])
                        amount += buy
                        buy = 0
                if row not in cmax:
                    cmax[row] = {"amount":amount, "mean":mean,"mean2":mean2, "row":row }
                elif amount > cmax[row]['amount']:
                    cmax[row] = {"amount":amount, "mean":mean, "mean2":mean2,"row":row }
                print(f"{mean}: {mean2} {row} 总 {max} 买入成功 {buys} 买入失败 {buys2} 总和 {amount}")

    for key,value in cmax.items():
        print(f"{value['mean']}:{value['mean2']} {value['row']} 总 {value['amount']} ")


#
# 5: 0.399850 总 619.2700000000004
# 6: 1.000016 总 6.6000000000008185
# 17: 1.000688 总 -12.940000000000055
# 49: 1.000300 总 212.30000000000018
# 4: 1.000905 总 -177.21000000000095
# 14: 1.000852 总 460.47000000000025
# 10: 2.932000 总 155.50000000000045

#
# 12:50 0.399850 总 532.9099999999999
# 20:4 1.000016 总 174.29999999999973
# 4:12 1.000688 总 48.63000000000011
# 10:51 1.000300 总 236.28999999999996
# 26:17 1.000905 总 351.4999999999991
# 18:16 1.000852 总 502.0600000000004
# 12:5 2.932000 总 191.44999999999936