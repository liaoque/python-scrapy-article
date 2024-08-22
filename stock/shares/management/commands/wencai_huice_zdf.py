import requests
import re
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def ask(s):
    # 涨停股票,首次涨停时间从小到大，流通市值，几天几板，连续涨停天数，去除st，涨停原因类别，所属概念

    print(s)
    # s = "半年报预增，所属概念，s去除ST，去除北交所，去除新股"
    url = 'http://www.iwencai.com/gateway/urp/v7/landing/getDataList'
    data = {
        'business_cat': 'soniu',
        'comp_id': 6836372,
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


if __name__ == "__main__":
    start = "20200101"
    end = "20240801"

    # 将日期字符串转换为datetime对象
    date1 = datetime.strptime(start, "%Y%m%d")
    date2 = datetime.strptime(end, "%Y%m%d")

    # 计算两个日期之间的差值
    delta = date2 - date1
    current_date = date1

    # 将差值转换为月份数
    months = (delta.days + delta.seconds // 86400) // 30
    for i in range(0, months):
        # 当前月
        current_month = current_date + relativedelta(months=i)

        # 下个月
        next_month = current_date + relativedelta(months=i + 1)

        # 前50日
        fifty_days_ago = current_month - timedelta(days=51)
        fifty_days_ago_s = fifty_days_ago.strftime("%Y%m%d")

        sixty_days_ago = current_month - timedelta(days=60)
        sixtyone_days_ago = current_month - timedelta(days=61)
        onetwo_days_ago = current_month - timedelta(days=121)

        current_month_s = current_month.strftime("%Y%m%d")
        sixtyone_days_ago_s = sixtyone_days_ago.strftime("%Y%m%d")
        next_month_s = next_month.strftime("%Y%m%d")
        onetwo_days_ago_s = onetwo_days_ago.strftime("%Y%m%d")
        sixty_days_ago_s = sixty_days_ago.strftime("%Y%m%d")
        s = f"""
    {fifty_days_ago_s}到{current_month_s}涨跌幅大于30%,{current_month_s}到{next_month_s}涨跌幅，
    {sixtyone_days_ago_s}到{current_month_s}最低价大于{onetwo_days_ago_s}到{sixty_days_ago_s}最低价,
    {onetwo_days_ago_s}日到{current_month_s}涨跌幅小于100%,{current_month_s}开盘价小于25元,主板和创业板
    """
        data = ask(s)
        for j  in range(len(data)):
            data[j]

