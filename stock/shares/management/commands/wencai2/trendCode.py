
import requests
import shares.management.commands.wencai2.common

def trendCode(today, yeasterday):
    s = '%smacd向上，%s收盘价高于开盘价，%s收盘价高于5日均价，%s回踩5日均线，概念，行业，股票市场类型，%s去除新股，去除ST，去除北交所,10日内有涨停' % (
        today, today, today, yeasterday, today
    )
    # s = '%s去除ST，去除北交所，%s去除新股，所属行业，所属概念，%s开盘价=%s涨停价，%s竞价未匹配金额，%s涨跌幅降序' % (
    #     today, today, today, today, today, today,
    # )

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
    codes = response.json()["answer"]["components"][0]["data"]["datas"]
    return shares.management.commands.wencai2.common.toCode(codes)
