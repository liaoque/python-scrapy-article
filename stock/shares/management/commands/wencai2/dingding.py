import requests


def dingding(s):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'https://oapi.dingtalk.com/robot/send?access_token='

    data = {
        'msgtype': 'text',
        'text': {
            "content":s
        }
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]
