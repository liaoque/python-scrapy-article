import requests


def dingding(s):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'https://oapi.dingtalk.com/robot/send?access_token=f51bee16742b25506373378cd7a33def2c1ce7d253998c59bfbdff28ffaf15d5'

    data = """
    {
        'msgtype': 'text',
        'text': {
            'content':'%s'
        }
    }
    """%(s)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data.encode("utf-8"), headers=headers)
    print(data, response.json())
    return response.json()
