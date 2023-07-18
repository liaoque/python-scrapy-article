3
import tushare as ts
import pandas as pd
import datetime
import openpyxl
import requests
import json
import talib
import numpy as np

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://xueqiu.com/",
    "Cookie": "xq_a_token=173d1b86b97861e4a0ecbe2d031fbd057d337248; xqat=173d1b86b97861e4a0ecbe2d031fbd057d337248; xq_r_token=ee8e80a187bf70af8a22704223d871770297dd64; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY4Mzg1MTMyOSwiY3RtIjoxNjgxNjkyMTI1Nzc1LCJjaWQiOiJkOWQwbjRBWnVwIn0.YYxbgrNTAxhUqD-Hiae0ggVAu6zjEhvJX5CFLXR9eLpAppGGDej83Kcav4jZ16TciEJhDvn-H-tAAZeucxgr-Nprfx8UvllIj8J1Yz2ckfVTWebAMw_2TfW--OTv7OstzuiLYzKhnZ9EMaXfKS87fw-0qZ5qA2nptz0L088Ej7FbVnQu40xcYFcZW5Avw_x4-9cR0ZpVhrLqQ-EakMkTCJbWU5YDkWFC-GMK8AxQGsW6rm9utEbtP9Hd9tc-ozJ3XaFTjNRgBD7cuTw7yQC1H4vcku6NMaW84M7878vYFSTJ2WiFOJ9D5E99mLKs5gQ1RLs9_J7MsuhbbEE-WniYTg; u=841681692171760; device_id=f93428ccc6e79071de4a4ca5c97f434c; s=ch16q0aijy;"
}


def get_stock():
    url = "https://stock.xueqiu.com/v5/stock/screener/fund/list.json?type=18&parent_type=1&order=desc&order_by=percent&page=1&size=1000"

    response = requests.get(url, headers=headers)
    data = json.loads(response.content.decode("utf-8"))

    klines = data['data']['list']  # 获取K线数据
    weekly_data = []
    for i in range(len(klines)):
        weekly_data.append(klines[i]['symbol'])
    return weekly_data


def get_stock_data(code):
    url = "https://stock.xueqiu.com/v5/stock/chart/kline.json"
    params = {
        "symbol": code,
        "begin": "1682512601154",
        "period": "day",
        "type": "normal",
        "count": "-10000",
        "indicator": "kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    }

    response = requests.get(url, params=params, headers=headers)
    data = json.loads(response.content.decode("utf-8"))
    if 'item' not in data['data']:
        return []
    klines = data['data']['item']  # 获取K线数据
    weekly_data = []
    for i in range(len(klines)):
        weekly_data.append({
            "date": datetime.datetime.fromtimestamp(klines[i][0] / 1000),
            "start": klines[i][2],
            "close": klines[i][5],
        })
    return weekly_data


def get_macd(data):
    # data = get_stock_data(code)  # 使用之前编写的方法获取数据
    close_prices = np.array([item["close"] for item in data])  # 获取收盘价序列
    macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1,
                                            signalperiod=9, signalmatype=1)  # 计算MACD值
    macd = macd * 2

    return macdDIFF, macdDEA, macd


def get_signal(macd_data):
    signals = []
    for i in range(1, len(macd_data)):
        if macd_data[i - 1]["diff"] < macd_data[i - 1]["dea"] and macd_data[i]["diff"] > macd_data[i]["dea"]:
            signals.append({
                "action": "buy",
                "macd": macd_data[i],
            })
        elif macd_data[i - 1]["diff"] > macd_data[i - 1]["dea"] and macd_data[i]["diff"] < macd_data[i]["dea"]:
            signals.append({
                "action": "sell",
                "macd": macd_data[i],
            })
        else:
            signals.append({
                "action": "hold"
            })
    return signals


def execute_trades(stock_data, signals):
    position = 0
    balance = 0
    for i in range(len(signals)):
        st = stock_data[i + 1]
        if signals[i]["action"] == "buy" and position == 0:
            position = 1
            balance -= st["start"]
            print(
                f"Buy at {st['start']} on day {signals[i]['macd']['current_data']} macd:{signals[i]['macd']['macd']}")
        elif signals[i]["action"] == "sell" and position == 1:
            position = 0
            balance += st["close"]
            print(
                f"Sell at {st['close']} on day  {signals[i]['macd']['current_data']} macd:{signals[i]['macd']['macd']}")
    if position == 1:
        balance += stock_data[-1]["close"]
        print(f"Sell at {stock_data[-1]['close']} on last day")
    return balance


def backtest(sheet, code):
    # 获取数据
    data = get_stock_data(code)
    if len(data) < 10:
        return
    diff, dea, macd = get_macd(data)
    macd_data = []
    for i in range(len(diff)):
        macd_data.append({
            "current_data": data[i]["date"].strftime("%Y-%m-%d"),
            "diff": float(diff[i]), "dea": float(dea[i]), "macd": float(macd[i])

        })
    signals = get_signal(macd_data)
    execute_trades(data, signals)


workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "backtest_result"

# 写入表头
header = ["买入时间", "买入价格", "卖出时间", "卖出价格", "盈利", "5周均线", "10周均线", "MACD"]
worksheet.append(header)

# stocks = get_stock()
stocks = ["SH603799"]
for stock in stocks:
    print(stock)
    backtest(worksheet, stock)
#
# workbook.save("backtest.xlsx")
