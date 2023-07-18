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
    url = "https://stock.xueqiu.com/v5/stock/screener/quote/list.json?page=0&size=5000&order=desc&orderby=code&order_by=symbol&market=CN&type=sh_sz"

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
        "begin": "1681816574883",
        "period": "week",
        "type": "normal",
        "count": "-284",
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


def backtest(sheet, code):
    # 获取数据
    data = get_stock_data(code)
    if len(data) < 10:
        return
    diff, dea, macd = get_macd(data)

    # 计算5周均线和10周均线
    close_prices = np.array([item["close"] for item in data])
    ma5 = talib.MA(close_prices, timeperiod=5)
    ma10 = talib.MA(close_prices, timeperiod=10)

    # 初始化交易状态和盈亏统计
    holding = False
    buy_price = 0
    sell_price = 0
    total_profit = 0
    num_wins = 0
    num_losses = 0
    buy_date = ""
    list_data = []
    # 遍历每周数据
    for i in range(len(data)):

        # 当前周数据
        current_data = data[i]
        current_close = current_data["close"]
        current_macd = macd[i]
        current_macd_b = macd[i - 1]
        current_macd_c = macd[i - 2]
        current_ma5 = ma5[i]
        current_ma10 = ma10[i]
        current_ma10_b = ma10[i - 1]

        # 如果当前持仓并且满足卖出条件，则卖出
        if holding and current_close < current_ma5:
            sell_price = current_close
            holding = False
            profit = sell_price - buy_price
            total_profit += profit
            if profit > 0:
                num_wins += 1
            else:
                num_losses += 1
            # 写入卖出数据
            sell_date = current_data["date"].strftime("%Y-%m-%d")
            list_data.append(
                [buy_date, buy_price, sell_date, sell_price, profit, current_ma5, current_ma10, current_macd]
            )
            # sheet.append([buy_date, buy_price, current_data["date"].strftime("%Y-%m-%d"),  sell_price, profit, current_ma5, current_ma10, current_macd])

        # 如果当前未持仓并且满足买入条件，则买入
        if not holding and current_close > current_ma10 and current_macd > current_macd_b and current_macd_b > current_macd_c and current_ma10 > current_ma10_b:
            buy_price = current_close
            holding = True
            buy_date = current_data["date"].strftime("%Y-%m-%d")
            # 写入买入数据
            # sheet.append([current_data["date"].strftime("%Y-%m-%d"), buy_price, "", "", "", current_ma5, current_ma10, current_macd])

    df = pd.DataFrame(list_data, columns=['buy_date', 'buy_price', 'sell_date', 'sell_price', 'profit', 'current_ma5',
                                          'current_ma10', 'current_macd'])

    df['buy_date'] = pd.to_datetime(df['buy_date'])
    df['sell_date'] = pd.to_datetime(df['sell_date'])

    df = df.set_index('buy_date')
    # print(df)
    # print(df.groupby(df.index.year)['profit'])
    # 按年份分组并统计
    yearly_summary = df.groupby(df.index.year)['profit']
    # .agg({'profit>0': lambda x: sum(x > 0), 'profit<0': lambda x: sum(x < 0)})
    # yearly_summary = df.groupby(df.index.year)['profit'].agg({'profit>0': lambda x: sum(x > 0), 'profit<0': lambda x: sum(x < 0), 'profit_ratio': lambda x: sum(x > 0) / sum(x < 0)})
    # annual_summary = yearly_summary.agg({
    # 'profit': [('positive_profit', lambda x: sum(x > 0)), ('negative_profit', lambda x: sum(x < 0))]
    # })
    # df.agg(x=('A', max), y=('B', 'min'), z=('C', np.mean))
    annual_summary = yearly_summary.agg(
        positive_profit=(lambda x: sum(x > 0)),
        negative_profit=(lambda x: sum(x < 0))
    )
    # print(df)
    # print(annual_summary)
    c1 = sum([t for t in annual_summary['positive_profit']])
    c2 = sum([t for t in annual_summary['negative_profit']])
    if c1 - c2 >= 3:
        # print("---------------")
        print(
            code,
            c1 - c2
        )
        # print(df)

        # sheet.append(["", "", "", "", "", "", "", ""])
        # sheet.append([code,c1 - c2 , "", "", "", "", "", ""])
        # for item in list_data:
        # print(item)
        # sheet.append(item)


workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.title = "backtest_result"

# 写入表头
header = ["买入时间", "买入价格", "卖出时间", "卖出价格", "盈利", "5周均线", "10周均线", "MACD"]
worksheet.append(header)

stocks = get_stock()
for stock in stocks:
    # print(stock)
    backtest(worksheet, stock)
#
workbook.save("backtest.xlsx")