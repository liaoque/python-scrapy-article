import requests
from datetime import datetime, timedelta


def getData():
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
