import requests
import json
import os
from datetime import datetime
from lh.dfcf import decode

# https://guba.eastmoney.com/rank/
headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

def hotStockList(listType = '0', type = '0', page = '0', v=''):
    """
    东方财富榜单，
    listType 0 人气榜      type  0 a股 1 港股 2 美股   page 分页  v 日期
    listType 3 飙升榜      type  0 a股 1 港股 2 美股   page 分页  v 日期
    :return:
    """
    sort = '0'
    if listType == '3':
        sort = '1'

    if v == '':
        v= '2025_2_7_4_0'

    url = """
    https://gbcdn.dfcfw.com/rank/popularityList.js?type=%s&sort=%s&page=%s&v=%s
    """%(type, sort, page, v)


    response = requests.get(url,  headers=headers)
    t = response.content.decode("utf-8")[20:-1]
    ts = decode.cbcDecode(t)
    return ts


def bkList(subType = '0'):

    return []


def expandList(categoryType = '13'):
    """
    东方财富榜单，
    categoryType 12 港股
    categoryType 13 美股
    categoryType 11 期货
    categoryType 3 可转债
    :return:
    """
    if categoryType == '13':
        return hotStockList(listType = '0', type = '2', page = '0', v='')
    elif categoryType == '12':
        return hotStockList(listType='0', type='1', page='0', v='')
    return  []


def rankToday(code, v):
    """
    人气排名
    :param code:
    :param v:
    :return:
    """
    url = "https://gbcdn.dfcfw.com/rank/today/%s.js?type=0&v=%s"%(code, v)
    response = requests.get(url, headers=headers)
    t = response.content.decode("utf-8")[15:-1]
    ts = decode.cbcDecode(t)
    return ts

def rankHistory(code, v):
    """
    历史趋势
    :param code:
    :param v:
    :return:
    """
    url = "https://gbcdn.dfcfw.com/rank/history/year/%s.js?type=0&v=%s"%(code, v)
    response = requests.get(url, headers=headers)
    t = response.content.decode("utf-8")[17:-1]
    ts = decode.cbcDecode(t)
    return ts

def fansToday(code, v):
    """
    新晋粉丝：近30日内，仅在近5日发生过上述行为的用户
    粉丝特征根据东方财富端内海量用户对该股票的浏览行为与股吧互动行为统计得出
    :param code:
    :param v:
    :return:
    """
    url = "https://gbcdn.dfcfw.com/rank/fanstoday/%s.js?v=%s"%(code, v)
    response = requests.get(url, headers=headers)
    t = response.content.decode("utf-8")[19:-1]
    ts = decode.cbcDecode(t)
    return ts

def fansHistory(code, v):
    """
    铁杆粉丝：近30日内，不仅在近5日发生过上述行为的用户
    :param code:
    :param v:
    :return:
    """
    url = "https://gbcdn.dfcfw.com/rank/fanshistory/year/%s.js?v=%s"%(code, v)
    response = requests.get(url, headers=headers)
    t = response.content.decode("utf-8")[21:-1]
    ts = decode.cbcDecode(t)
    return ts

# hotStockList()