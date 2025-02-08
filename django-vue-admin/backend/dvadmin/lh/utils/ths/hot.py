import requests
import json
import os
from datetime import datetime

# https://eq.10jqka.com.cn/frontend/thsTopRank/index.html#/

def hotStockList(list_type = 'normal'):
    """
    同花顺榜单，
    listType normal 默认
    listType skyrocket 快速飙升
    listType tech 技术交流
    listType value 价值投资
    listType trend 趋势交易
    :return:
    """
    type='day'
    if list_type == 'normal':
        type = 'hour'

    url = """https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock?stock_type=a&type=%s&list_type=%s"""%(type, list_type)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    # print(data, response.json())
    return response.json()


def bkList(type = 'concept'):
    """
    同花顺榜单，
    type industry 行业
    type concept 板块
    :return:
    """
    url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/plate?type='+type

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    # print(data, response.json())
    return response.json()

def etfList():
    """
    同花顺榜单， etf
    :return:
    """
    url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/etf?type='

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url,  headers=headers)
    # print(data, response.json())
    return response.json()



def expandList(categoryType = '13'):
    """
    同花顺榜单，
    categoryType 12 港股
    categoryType 13 美股
    categoryType 11 期货
    categoryType 3 可转债
    categoryType 3 可转债
    categoryType 15 保险
    categoryType 16 热门基金场外
    :return:
    """
    if categoryType == '3':
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/bond'
    elif categoryType == '12':
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock?stock_type=hk&type=day&list_type=normal'
    elif categoryType == '13':
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock?stock_type=usa&type=day&list_type=normal'
    elif categoryType == '11':
        url = 'https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/future'
    elif categoryType == '15':
        url = 'https://baoxian.10jqka.com.cn/insurance/v3/rank/v1/hot_list'
    else:
        url = 'https://ai.iwencai.com/index/urp/getdata/basic?tag=%E5%90%8C%E8%8A%B1%E9%A1%BA%E7%83%AD%E6%A6%9C_%E7%83%AD%E5%9F%BA&userid=0&appName=thsHotList&filter=%7B%22offset%22:0,%22limit%22:100,%22sort%22:[[%22list_rank_1d%22,%22ASC%22]],%22where%22:%7B%22list_rank_1d%22:%7B%22$lte%22:200%7D,%22class_name%22:%7B%22$eq%22:%22%E4%BA%BA%E6%B0%94%22%7D%7D%7D'

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, headers=headers)
    return response.json()