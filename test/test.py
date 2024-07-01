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

if __name__ == '__main__':
    # indexes = quick_stock.TradeIndexClient().get_all_index()
    # print(indexes[indexes[""] ==""][:20])
    sz50 = quick_stock.TradeIndexClient().daily("0.399850") # 深证50
    sz50 = pd.DataFrame(sz50)
    macd, signal, hist = macd(sz50["end"])

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

    dates = sz50["date_at"][-120:]
    open_prices = sz50["start"][-120:]
    high_prices = sz50["max"][-120:]
    low_prices = sz50["min"][-120:]
    close_prices = sz50["end"][-120:]
    fig, (ax1, ax2) = plt.subplots(2, sharex=True, figsize=(10, 8))
    candlestick_ohlc(ax1, zip(np.arange(1, len(dates))  , open_prices, high_prices, low_prices, close_prices), width=0.6, colorup='g',
                     colordown='r')
    ax1.set_title('股价K线图')
    ax1.set_ylabel('价格')

    # 绘制MAC柱状图
    macd = macd[-120:]
    signal = signal[-120:]
    hist = hist[-120:]
    ax2.bar(dates, macd, color='b')
    ax2.set_title('MAC柱状图')
    ax2.set_xlabel('日期')
    ax2.set_ylabel('MAC值')
    plt.show()

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
