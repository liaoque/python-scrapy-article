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
        "Cookie": "device_id=f93428ccc6e79071de4a4ca5c97f434c; s=ch16q0aijy; snbim_minify=true; bid=8ef484bce3b63d26a12f5c4af675f48f_lhat0b77; Hm_lvt_1db88642e346389874251b5a1eded6e3=1689170238; xq_a_token=715ae77c7b72c67549b80e153e894ef2e19f0446; xqat=715ae77c7b72c67549b80e153e894ef2e19f0446; xq_r_token=a1c71f74d5f0fd50f87640a0682c837e5a07f706; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY5MjkyMzcyMSwiY3RtIjoxNjkwMzg3NDQxMDEzLCJjaWQiOiJkOWQwbjRBWnVwIn0.o8JzWoLlHa3zHZL1puHuVgHKcrvZWXfYOAajqmMJPC78Wj9GgtOTuCvf5flMJprhxRCLxSBhSPb16pcNvIxUMWx3lxTAbEIuxiO4gqugkdIlRmN4Nzm2VrVwFoVjvagvFTwbxyptRMi0N3HKpahJFs_f7DndBPSpiBaH6qRU6bCQ7C9PSa5LTSnI4fmRWt2wD3OGEDjw6KCBNnsqfLfVm13JH53r3vhzZIjmNOrNygJz-HVPswvN3Ie6FEhM2z_LeiFezW0aVXDy0_trtjZvdmER0b1qbGLfk2tistz4f4b1AuxK9imtddI4wK6p_oY9ajmurCim5egt9o3RRF70nA; u=941690387441190; is_overseas=0;"
    }

    response = requests.get(url, params=data, headers=headers)
    print(response)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()

    return codes2["data"]["item"]
