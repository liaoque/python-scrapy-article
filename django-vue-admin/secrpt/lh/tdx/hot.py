import requests
import json
import os
from datetime import datetime

# https://pul.tdx.com.cn/site/app/gzhbd/tdx-topsearch/page-main.html?pageName=page_topsearch&tabClickIndex=0&subtabIndex=0

def hotStockList(listType = '0', cycle = '0'):
    """
    通达信榜单，
    listType 0 人气榜      cycle  0 最新 1 30分钟 260分钟
    listType 1 关注榜      cycle  0 最新 1 30分钟 260分钟
    listType 2 热搜榜      cycle  0 最新 1 30分钟 260分钟
    listType 3 飙升榜      cycle 无意义
    :return:
    """
    url = 'https://pul.tdx.com.cn/TQLEX?Entry=JNLPSE.hotStockList&RI='
    data = """
        {
            'listType': '%s',
            'cycle': '%s',
        }
        """ % (listType, cycle)

    if listType == '3':
        url = 'https://pul.tdx.com.cn/TQLEX?Entry=JNLPSE.changeStockList&RI='
        data = """
                {
                    'changeType': '1',
                }
                """

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data.encode("utf-8"), headers=headers)
    # print(data, response.json())
    return response.json()


def bkList(subType = '0'):
    """
    通达信榜单，
    subType 0 行业
    subType 1 板块
    :return:
    """
    url = 'https://pul.tdx.com.cn/TQLEX?Entry=JNLPSE.bkList&RI='
    data = """
        {
            'subType': '%s',
        }
        """ % (subType)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data.encode("utf-8"), headers=headers)
    # print(data, response.json())
    return response.json()


def expandList(categoryType = '13'):
    """
    通达信榜单，
    categoryType 12 港股
    categoryType 13 美股
    categoryType 11 期货
    categoryType 3 可转债
    :return:
    """
    url = 'https://pul.tdx.com.cn/TQLEX?Entry=JNLPSE.expandList&RI='
    data = """
        {
            'categoryType': '%s',
        }
        """ % (categoryType)

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.post(url, data=data.encode("utf-8"), headers=headers)
    # print(data, response.json())
    return response.json()