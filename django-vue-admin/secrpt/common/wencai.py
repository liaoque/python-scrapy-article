import math

import requests

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


def wencaiRequest(s, page=1):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': 6836372,
        'page': page,
        'perpage': '100',
        'query': s,
        'uuid': '24087',
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        jdata = response.json()
        row_count = jdata["answer"]["components"][0]['data']["meta"]["extra"]["row_count"]
        return {
            "data": jdata["answer"]["components"][0]['data']["datas"],
            "row_count": row_count
        }
    except Exception as e:
        pass
    return {}


def wencai(s, page=1):
    d = wencaiRequest(s, page)
    l = math.ceil(d["row_count"] / 100)
    dall = d["data"]
    i = 2
    while (i < l):
        d = wencai(s, page + 1)
        dall += d["data"]
        l += 1
    return dall
