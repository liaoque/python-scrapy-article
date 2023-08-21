import requests
import shares.management.commands.wencai2.common

def trendFirstDown(today):
    s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，%s开盘价=%s跌停价，%s竞价未匹配大于0，%s竞价未匹配金额，%s涨跌幅降序，5日涨跌幅' % (
        today, today, today, today, today, today,today,
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
        'uuid': '24087'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()["answer"]["components"][0]["data"]["datas"]

    codes = shares.management.commands.wencai2.common.toCode(codes2)

    return codes



def trendNightDown(today):
    s = '%s去除ST，%s去除北交所，%s去除新股，所属行业，所属概念，%s收盘价涨跌幅<%s，5日涨跌幅降序' % (
        today, today, today, today, "-7%"
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
        'uuid': '24087'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    # print(response.json()["answer"]["components"][0]['data']["datas"])
    codes2 = response.json()["answer"]["components"][0]["data"]["datas"]

    codes = shares.management.commands.wencai2.common.toCode(codes2)

    return codes


from collections import defaultdict


