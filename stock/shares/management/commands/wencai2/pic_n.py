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
    dt = datetime.strptime(today, "%Y-%m-%d")
    parts = stock_code.split('.')
    code = ''.join([parts[1], parts[0]])

    url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json'
    data = {
        'symbol': code,
        'begin': (int(dt.timestamp()) + 86300) * 1000,
        'period': 'day',
        'type': 'before',
        'count': n,
        'indicator': 'kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance'
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://xueqiu.com/",
        "Cookie": "xq_a_token=197a3a870824d1754f6edf083d719bd1a3aabe88; xqat=197a3a870824d1754f6edf083d719bd1a3aabe88; xq_r_token=f3676d47182482b690747de814788450c6d4fcf1; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY5MTYyNzcwNSwiY3RtIjoxNjg5MTcwMTk0OTA4LCJjaWQiOiJkOWQwbjRBWnVwIn0.cCXKN95tZEuqIdo6IQjc6P8thVTmM2KCNemtN64JmI91pO1RTrwV3a4hWCS7za5E5by8zDAuXZ3uxsRlFc1jtcbKFanRvPcT_9gUjzMqJbxyWhWVZOLuWBxm0bJZ8o7x6ljPiu4Qc771OaMQYvNZT6a4SO5CX-WrLeHT-UZf4IbbIungLF2QhBhgvcuZhMlYoV3TMPkGP7RzgKUYo5jn8ZIJRA9k8S4tRWPnvFp1uBl7c_fJ42pH4Af97U0XYk3rBF5MwHzJWu7_ZCADi9VgKdhapB-D6MXHkN9-KxU0cQHwb5jPg6AI8P6e3cXhVrmhttifsAfnAJcb2Ggqz4cZaw;"
    }

    response = requests.get(url, params=data, headers=headers)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()

    return codes2["data"]["item"]
