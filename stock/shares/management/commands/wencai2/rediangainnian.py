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
              "http://25.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f53&klt=101&fqt=1&beg=0&end=20500101&lmt=1000000&_=1711101890918") % (
              secid)

    response = requests.get(url)
    return response.json()["data"]["klines"]

def zhishu_week(secid):
    """
    zhishu_week
    :param s:
    :return:
    """
    url = (
              "https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=102&fqt=1&end=20500101&lmt=10000&_=1713314412556"
          ) % (
              secid)

    response = requests.get(url)
    return response.json()["data"]["klines"]

def zhishu_month(secid):
    """
    zhishu
    :param s:
    :return:
    """
    url = (
              "https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=%s&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=103&fqt=1&end=20500101&lmt=120&_=1713314412640"
          ) % (
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


def codes(cdate, gn, etf):
    """
    查最近10天的热点概念
    :param s:
    :return:
    """
    today = cdate[0].date_as
    t3 = cdate[3].date_as
    # date_obj = datetime.strptime(today, "%Y%m%d")
    # result_date = date_obj - timedelta(days=20)
    t20 = cdate[19].date_as
    # result_date = date_obj - timedelta(days=185)
    t185 = cdate[124].date_as

    s = '%s去除ST，%s去除北交所，%s去除新股，所属概念包含%s，属于指数%s, %s-%s涨跌幅从大到小，%s-%s跌停次数取反，%s-%s无减持公告，%s-%s无处罚原因，无造假' % (
        today, today, today, gn, etf, t3, today, t20, today, t185, today, t185, today
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
    if "answer" not in response.json():
        print(response.json())
    return response.json()["answer"]["components"][0]['data']["datas"]
