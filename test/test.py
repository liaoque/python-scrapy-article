import datetime

import numpy as np
import pandas as pd
import quick_stock as quick_stock
import talib
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
def macd(close_prices):
    # 计算kd指标
    macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26,
                                            slowmatype=1,
                                            signalperiod=9, signalmatype=1)
    macd = macd * 2
    return (macdDIFF, macdDEA, macd)


def compute(title,code):
    sz50 = quick_stock.TradeIndexClient().daily(code)  # 深证50
    sz50 = pd.DataFrame(sz50)
    mac, signal, hist = macd(sz50["end"])
    return {
        "title": code,
        "data": sz50,
        "macd": macd,
        "signal": signal,
        "hist": hist,
    }
def draw(title, fig, code, i):
    sz50 = quick_stock.TradeIndexClient().daily(code)  # 深证50
    sz50 = pd.DataFrame(sz50)
    mac, signal, hist = macd(sz50["end"])

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
    ax1.set_title(title)
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
    return fig,i


if __name__ == '__main__':
    # indexes = quick_stock.TradeIndexClient().get_all_index()
    # print(indexes[indexes[""] ==""][:20])

    data = []
    data.append(compute("sz50", "0.399850"))
    data.append(compute("a50", "1.000016"))
    data.append(compute("kc50", "1.000688"))
    data.append(compute("hs300", "1.000300"))
    data.append(compute("zz500", "1.000905"))
    data.append(compute("zz1000", "1.000852"))
    data.append(compute("zz2000", "2.932000"))

    # for i range 10:
    #
    # i = 1
    fig = plt.figure(figsize=(20, 16),)
    fig,i = draw('sz50',fig, "0.399850", i)
    fig,i = draw('a50',fig, "1.000016", i)
    fig,i = draw('kc50',fig, "1.000688", i)
    fig,i = draw('hs300',fig, "1.000300", i)
    fig,i = draw('zz500',fig, "1.000905", i)
    fig,i = draw('zz1000',fig, "1.000852", i)
    fig,i = draw('zz2000',fig, "2.932000", i)
    plt.show()
    # sz50 = quick_stock.TradeIndexClient().daily("0.399850") # 深证50
    # sz50 = pd.DataFrame(sz50)
    # macd, signal, hist = macd(sz50["end"])

    # sz50 = quick_stock.TradeIndexClient().daily("1.000016") # 上证50
    # macd, signal, hist = macd(sz50["end"])
    #
    # kc50 = quick_stock.TradeIndexClient().daily("1.000688") # 科创50
    # macd, signal, hist = macd(kc50["end"])
    #
    # hs300 = quick_stock.TradeIndexClient().daily("1.000300") # 沪深300
    # macd, signal, hist = macd(hs300["end"])
    #
    # zz500 = quick_stock.TradeIndexClient().daily("1.000905") # 中证500
    # macd, signal, hist = macd(zz500["end"])
    #
    # zz1000 = quick_stock.TradeIndexClient().daily("1.000852") # 中证1000
    # macd, signal, hist = macd(zz1000["end"])
    #
    # zz2000 = quick_stock.TradeIndexClient().daily("2.932000") # 中证2000
    # macd, signal, hist = macd(zz2000["end"])

    # dates = sz50["date_at"][-120:]
    # open_prices = sz50["start"][-120:]
    # high_prices = sz50["max"][-120:]
    # low_prices = sz50["min"][-120:]
    # close_prices = sz50["end"][-120:]
    # fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(10, 8))
    # candlestick_ohlc(ax1, zip(np.arange(1, len(dates)) , open_prices, high_prices, low_prices, close_prices), width=0.6, colorup='g',
    #                  colordown='r')
    # ax1.set_title('sz50')
    # ax1.set_ylabel('price')
    #
    # # 绘制MAC柱状图
    # macd = macd[-120:]
    # signal = signal[-120:]
    # hist = hist[-120:]
    # ax2.bar(dates, macd, color='#f059c6')
    # ax2.set_title('macd')
    # ax2.set_xlabel('date')
    # ax2.set_ylabel('macd')
    #
    # ax3 = ax2.twinx()
    # ax3.plot(dates, signal, color='red', label='Histogram')
    # ax4 = ax2.twinx()
    # ax4.plot(dates, hist, color='#339958', label='Histogram')



    # fig, ax1 = plt.subplots()
    # d = sz50['date_at'][-10:]
    # e = sz50['end'][-10:]
    # ax1.plot(d, e, color='blue', label='Close')
    # ax1.set_ylabel('Price')
    #
    # ax2 = ax1.twinx()
    # e = hist[-10:]
    # ax2.bar(d, e, color='red', label='Histogram')
    # ax2.set_ylabel('MACD')
    #
    # fig.legend(loc='upper left')
    # plt.show()
