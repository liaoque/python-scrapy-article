import requests
from datetime import datetime, timedelta


def check(today, stock_code):
    data = getData(today, stock_code)
    # data2 = data[::-1]
    for i in range(10):
        i = i + 1
        # 从后往前第一个涨停
        if data[10 - i][7] >= 9.7:

            # 有可能连版，所以往前找第一个涨停
            for j in range(10 - i):
                j = j + 1
                index = 10 - i - j
                if index >= 0 and data[index][7] < 9.7:
                    # 第一个涨停 缩量涨停
                    t = data[index + 1][1] / data[index][1]
                    if t > 1 and t < 1.6:
                        return True
                    return False
    # 对子
    # m = min([item[5] for item in data[:i]])
    # 成交量
    l = sum([item[1] for item in data])
    avg = l / 10 / 2

    # 最后第一天和最后第二天不足 平均成交量的 1/3
    return data[9][1] <= avg and data[8][1] <= avg


def getData(today, stock_code, n=-10):
    url = 'https://69.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=1.000001&ut=&fields1=f1&fields2=f51&klt=101&fqt=1&end=20500101&lmt=300&_=1691403957512'
    data = {
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "http://quote.eastmoney.com/zs000001.html",
    }

    response = requests.get(url, params=data, headers=headers)
    codes2 = response.json()

    return codes2["data"]["klines"]