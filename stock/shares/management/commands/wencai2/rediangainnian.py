import requests
import shares.management.commands.wencai2.common


def rdgainian(s):
    """
    查最近10天的热点概念
    :param s:
    :return:
    """
    url = ('http://81.68.241.227:39001/gns?current_time=%s') % (s)

    response = requests.get(url)
    return response.json()


def codes(today, gn, etf):
    """
    查最近10天的热点概念
    :param s:
    :return:
    """
    s = '%s去除ST，%s去除北交所，%s去除新股，所属概念包含%s，属于指数%s, 4日涨跌幅从大到小' % (
        today, today, today, gn, etf
    )
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
