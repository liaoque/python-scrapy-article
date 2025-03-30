import requests

# from PyQt5.QtSql import password
# from sqlalchemy import except_

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}


def wencai(s):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': 6831800,
        'page': '1',
        'perpage': '100',
        'query': s,
        'uuid': '24088',
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        return response.json()["answer"]["components"][0]['data']["datas"]
    except Exception as e:
        pass
    return []


def jijinTop10(code):
    """
    获取基金前10重仓股票
    :param code:
    :return:
    """
    url = 'https://fund.10jqka.com.cn/web/fund/stockAndBond/' + code
    response = requests.get(url, headers=headers)
    return response.json()['data']['stock']


def jijinTop10All(s):
    """
    获取基金前十所有重仓股票对象
    :param s:
    :return:
    """
    codes = {}
    for item in wencai(s):
        # print(jijinTop10(item['基金代码'][:6]))
        for itemTop2 in jijinTop10(item['基金代码'][:6]):
            if itemTop2['zcCode'] not in codes:
                codes[itemTop2['zcCode']] = 1
            else:
                codes[itemTop2['zcCode']] = codes[itemTop2['zcCode']] + 1


if __name__ == '__main__':
    codes = jijinTop10All("所属中证1000基金, 100日涨跌幅，排除c类基金")

    allSum = sum([value for key, value in codes.items()])
    print(codes.keys())

    # 取雪球聊天记录

    # 取股票信息

    # 计算情绪
