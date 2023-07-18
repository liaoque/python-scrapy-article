import requests
import wencai2.common


# 补涨的
def buzhang(today, yeasterday, yeasteryeasterday, concept):
    s = '%s去除ST，去除北交所，去除新股，所属行业，所属概念，%s前10交易日曾经收盘价创250日新高，250交易日涨停次数大于0，%s成交额小于%s成交额，250日涨跌幅降序排序，%s' % (
        today,  today,  yeasterday, yeasteryeasterday,concept
    )
    print(s)
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': wencai2.common.comp_id,
        'page': '1',
        'perpage': '1000',
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

    codes = wencai2.common.toCode(codes2)

    return codes


def codes(today, concept):
    s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，5日涨跌幅<20%%，%s，5日涨跌幅降序,10日内有涨停' % (
        today, today, concept
    )

    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': wencai2.common.comp_id,
        'page': '1',
        'perpage': '1000',
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

    codes = wencai2.common.toCode(codes2)

    return codes
