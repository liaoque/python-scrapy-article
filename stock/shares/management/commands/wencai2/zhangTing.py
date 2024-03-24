import requests
import shares.management.commands.wencai2.common


def search(s):
    # x概念且x概念
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': shares.management.commands.wencai2.common.comp_id,
        'page': '1',
        'perpage': '100',
        'query': s,
        'uuid': '24087',

    }
    print(s)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]


def zhangTing(today):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    s = '%s去除ST，%s去除北交所，%s去除新股，%s涨停股票,%s首次涨停时间从小到大，流通市值，%s几天几板，%s连续涨停天数，%s涨停原因类别，所属概念，所属同花顺行业，%s最终涨停时间' % (
        today, today, today, today, today, today, today, today, today
    )
    print(s)
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': shares.management.commands.wencai2.common.comp_id,
        'page': '1',
        'perpage': '100',
        'query': s,
        'uuid': '24087',

    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]
    # return response.json()["answer"]["components"][0]["data"]["meta"]["extra"]["row_count"]


def zhangTingGns(today, i):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    s = '%s同花顺概念指数，涨跌幅从大到小，%s开盘价，%s收盘价，%s最低价，%s最高价' % (
        today, today, today, today, today
    )

    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': 6829723,
        'page': i,
        'perpage': '100',
        'query_type': 'zhishu',
        'query': s,
        'uuid': '24089',
        'uuids[0]': '24089',

    }
    print(data)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]


def infoG(code):
    if code[-3:] == ".SZ":
        code = "0." + code[0:-3]
    else:
        code = "1." + code[0:-3]

    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=%s&cb=&klt=101&fqt=0&lmt=100&end=20500101&iscca=1&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58" % (
        code)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.json()["data"]["klines"]



def Macd(today, end, i):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    s = '去除st,去除北交所,去除科创板,%s到%s涨跌幅>0, %s收盘价:不复权,%s前120日涨跌幅>0' % (
        today, end, end, today
    )

    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': shares.management.commands.wencai2.common.comp_id,
        'page': i,
        'perpage': '100',
        'query': s,
        'uuid': '24087',
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]