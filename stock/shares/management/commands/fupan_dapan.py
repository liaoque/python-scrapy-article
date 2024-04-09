from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

import talib
import numpy as np
import os
import re

from shares.model.shares_join_block import SharesJoinBlock
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.management.commands.wencai2 import rediangainnian, zhangTing
from shares.model.shares_date import SharesDate
from datetime import datetime, timedelta
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_buys import SharesBuys
from shares.model.shares_zhang_tings import SharesZhangTings
from shares.model.shares import Shares


def time2seconds(time_str):
    time_format = '%H:%M:%S'  # 时间字符串的格式
    time_obj = datetime.strptime(time_str, time_format)
    return timedelta(hours=time_obj.hour, minutes=time_obj.minute, seconds=time_obj.second).total_seconds()


"""
使用macd对大盘复盘
按照波段统计上涨天数和上涨家数
"""


class Command(BaseCommand):
    help = "对每天进行复盘"

    etfs = []
    gns = []
    gps = []
    codes = []
    dates = []
    date = ""

    fp = 1
    fp_start = "2024-01-01"
    fp_end = ""
    fp_dates = "2024-04-01"

    stop = False

    data = {
        "a": [],
        "a50": [],
        "hs300": [],
        "zt500": [],
        "zt1000": [],
        "zt2000": [],
    }

    def computeBoDuan(self, data):
        # print(data)
        macdDIFF, macdDEA, macds = self.macd(data)
        # print(macds)
        i = 0
        j = 0
        boduan = []
        if macds[2] > macds[1] > macds[0]:
            boduan.append({
                "p": "up",
                "d": self.dates[0],
                "next": 0
            })

        else:
            boduan.append({
                "p": "down",
                "d": self.dates[0],
                "next": 0
            })

        for macd in macds:

            if i == 0:
                i = i + 1
                continue
            if macd is None:
                i = i + 1
                continue
            if i + 2 >= len(macds):
                break
            if macds[i] > macds[i - 1]:
                """
                上行波段
                """
                if macds[i] > macds[i - 1] and macds[i] > macds[i + 1] > macds[i + 2]:
                    """
                    顶部反转
                    """
                    boduan.append({
                        "p": "up-down",
                        "macd": macd,
                        "d": self.dates[i],
                        "data": data[i],
                        "next": 0
                    })

                elif macds[i - 1] < 0 and macds[i] > 0:
                    """
                    负转正，二波
                    """
                    boduan.append({
                        "p": "up",
                        "macd": macd,
                        "d": self.dates[i],
                        "data": data[i],
                        "next": 1
                    })

            elif macds[i] < macds[i - 1]:
                """
                下行波段
                """
                if macds[i] < macds[i - 1] and macds[i] < macds[i + 1] < macds[i + 2]:
                    """
                    底部反转
                    """
                    boduan.append({
                        "p": "down-up",
                        "macd": macd,
                        "d": self.dates[i],
                        "data": data[i],
                        "next": 0
                    })

                elif macds[i - 1] > 0 and macds[i] < 0:
                    """
                    正转负，二波
                    """
                    boduan.append({
                        "p": "down",
                        "macd": macd,
                        "d": self.dates[i],
                        "data": data[i],
                        "next": 1
                    })
            i = i + 1
        return boduan

    def handle(self, *args, **options):
        self.date = "20240404"

        boduan = []
        boduan.append({
            "code": "zt2000",
            "data": self.zt2000()
        })

        for item in boduan:
            print(item["code"])
            data = item["data"]

            for i in range(len(item["data"])):
                if i + 1 == len(item["data"]):
                    continue
                sz = xd = p = sz2 = xd2 = p2 = 0
                for j in range(len(self.data[item["code"]])):
                    if j + 1 == len(self.data[item["code"]]):
                        continue
                    d1 = self.data[item["code"]][j].split(",")
                    d2 = self.data[item["code"]][j + 1].split(",")

                    new_date_str = d1[0]
                    # 处于区间内
                    if data[i]['d'] >= new_date_str or new_date_str > data[i + 1]['d']:
                        continue
                    if d2[1] > d1[1]:
                        sz = sz + 1
                    elif d2[1] < d1[1]:
                        xd = xd + 1
                    else:
                        p = 0
                    szs = len(Shares.objects.filter(p_range__gt=0, date_as=new_date_str))
                    xds = len(Shares.objects.filter(p_range__lt=0, date_as=new_date_str))
                    if szs > xds:
                        sz2 = sz2 + 1
                    elif szs < xds:
                        xd2 = xd2 + 1
                    else:
                        p2 = 0

                print(
                    "%s - %s : %s, 价格： 上涨 %s, 下跌 %s, 平 %s， 数量： 上涨 %s, 下跌 %s, 平 %s" % (
                        data[i]['d'], data[i + 1]['d'], data[i]['p'],
                        sz, xd, p,
                        sz2, xd2, p2
                    )
                )

    def macd(self, data):
        # 计算kd指标
        close_prices = np.array([float(item) for item in data])
        # print(close_prices)
        # exit()
        macdDIFF, macdDEA, macd = talib.MACDEXT(close_prices, fastperiod=12, fastmatype=1, slowperiod=26,
                                                slowmatype=1,
                                                signalperiod=9, signalmatype=1)
        macd = macd * 2
        return (macdDIFF, macdDEA, macd)

    def computeMacd(self, data):
        macdDIFF, macdDEA, macd = self.macd(data)
        last = macd[len(macd) - 1]
        last2 = macd[len(macd) - 2]
        last3 = macd[len(macd) - 3]
        if last > 0:
            return True
        elif last < 0:
            if last > last2 > last3:
                return True
            elif last < last2:
                self.stop = True
                return False
        return True

    def a(self):
        """
        对大盘进行复盘
        :return:
        """
        self.stop = False
        data = self.data["a"]
        if len(self.data["a"]) == 0:
            data = self.data["a"] = rediangainnian.zhishu("1.000001")

        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]

        # print(self.dates)
        # exit()
        return self.computeBoDuan(data)

    def etf(self):
        """
        对 中证A50， 沪深300，中证500，中证1000，中证2000
        :return:
        """
        self.etfs = []
        if self.A50():
            self.etfs.append("a50")
        if self.hs300():
            self.etfs.append("hs300")
        if self.zt500():
            self.etfs.append("zt500")
        if self.zt1000():
            self.etfs.append("zt1000")
        if self.zt2000():
            self.etfs.append("zt2000")

    def A50(self):
        """
        对 A50 复盘
        :return:
        """
        data = self.data["a50"]
        if len(self.data["a50"]) == 0:
            data = self.data["a50"] = rediangainnian.zhishu("2.930050")
        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeBoDuan(data)

    def hs300(self):
        """
        对 沪深300 复盘
        :return:
        """
        data = self.data["hs300"]
        if len(self.data["hs300"]) == 0:
            data = self.data["hs300"] = rediangainnian.zhishu("1.000300")
        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeBoDuan(data)

    def zt500(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt500"]
        if len(self.data["zt500"]) == 0:
            data = self.data["zt500"] = rediangainnian.zhishu("1.000905")
        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeBoDuan(data)

    def zt1000(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt1000"]
        if len(self.data["zt1000"]) == 0:
            data = self.data["zt1000"] = rediangainnian.zhishu("1.000852")
        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeBoDuan(data)

    def zt2000(self):
        """
        对中小板复盘
        :return:
        """
        data = self.data["zt2000"]
        if len(self.data["zt2000"]) == 0:
            data = self.data["zt2000"] = rediangainnian.zhishu("2.932000")
        self.dates = [item.split(",")[0] for item in data if
                      item.split(",")[0].replace("-", "") <= self.date]
        # print(self.dates)
        data = [item.split(",")[1] for item in data if
                item.split(",")[0].replace("-", "") <= self.date]
        return self.computeBoDuan(data)
