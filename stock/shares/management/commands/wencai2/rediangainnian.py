import requests
import shares.management.commands.wencai2.common
from datetime import datetime, timedelta


def zhishu(secid):
    """
    zhishu
    :param s:
    :return:
    """
    url = (
              "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&smplmt=460&lmt=1000000&_=1711101890918") % (
              secid)

    response = requests.get(url)
    return response.json()["data"]["klines"]


def rdgainian(s):
    """
    查最近10天的热点概念
    :param s:
    :return:
    """
    url = ('http://60.204.137.231:39088/api/wb/gns?current_time=%s') % (s)

    response = requests.get(url)
    return response.json()


def codes(today, gn, etf):
    """
    查最近10天的热点概念
    :param s:
    :return:
    """
    date_str = "2024-01-02"
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    result_date = date_obj - timedelta(days=20)
    t20 = result_date.strftime("%Y-%m-%d")
    result_date = date_obj - timedelta(days=185)
    t185 = result_date.strftime("%Y-%m-%d")

    s = '%s去除ST，%s去除北交所，%s去除新股，所属概念包含%s，属于指数%s, %s前4日涨跌幅从大到小，%s-%s跌停次数取反，%s-%s无减持公告，%s-%s无处罚原因，无造假' % (
        today, today, today, gn, etf, today, t20, today, t185, today, t185, today
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
    print(s)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data, headers=headers)
    return response.json()["answer"]["components"][0]['data']["datas"]
