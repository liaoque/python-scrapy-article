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

"""


class Command(BaseCommand):
    help = "统计日期在所有当中的上涨和下跌概率"

    etfs = []
    gns = []
    gps = []
    codes = []
    dates = []
    date = ""

    fp = 1
    fp_start = "2000-01-01"
    fp_end = "2024-04-01"
    fp_dates = "2024-04-01"

    stop = False

    data = {
        "a": {},
        "a50": {},
        "hs300": {},
        "zt500": {},
        "zt1000": {},
        "zt2000": {},
    }

    def handle(self, *args, **options):
        self.date = "20240404"
        for code, item in self.data.items():
            data = self.compute(item["week"], True)
            for num in range(1, 7):
                numdata = [item for item in data if item["num"] == num]
                gt = len([item for item in numdata if item["action"] == "gt"])
                lt = len([item for item in numdata if item["action"] == "lt"])
                # print("%s-%s  %s week-%s down: %s up: %s" % (
                #     self.fp_start, self.fp_end, code, num, lt, gt,
                # ))

            data = self.compute(item["month"], False)
            for num in range(1, 13):
                numdata = [item for item in data if item["num"] == num]
                gt = len([item for item in numdata if item["action"]  == "gt"])
                lt = len([item for item in numdata if item["action"]  == "lt"])
                if 6 < num or num < 4:
                    continue
                if gt <= lt:
                    continue
                print("%s-%s  %s month-%s down: %s up: %s" % (
                    self.fp_start, self.fp_end, code, num, lt, gt,
                ))

    def compute(self, item, week=True):
        data = [{
            "date": item.split(",")[0],
            "start": item.split(",")[1],
            "end": item.split(",")[2],
        } for item in item["data"] if self.fp_start <= item.split(",")[0] <= self.fp_end]

        i = 0
        l = len(data)
        while i < l:
            if data[i]["end"] > data[i - 1]["end"]:
                data[i]["action"] = "gt"
            elif data[i]["end"] < data[i - 1]["end"]:
                data[i]["action"] = "lt"
            else:
                data[i]["action"] = "ge"

            if week:
                today = datetime.strptime(data[i]["date"], "%Y-%m-%d")
                # 获取这个月的第一天
                first_day_of_month = today.replace(day=1)
                # 计算第一天是星期几（0=Monday, 6=Sunday）
                first_weekday = first_day_of_month.weekday()
                # 计算今天是这个月的第几天
                day_of_month = today.day
                data[i]["num"] = (day_of_month + first_weekday - 1) // 7 + 1

            else:
                data[i]["num"] = datetime.strptime(data[i]["date"], "%Y-%m-%d").month

            i += 1
        return data

    def __init__(self):
        super().__init__()
        self.data["a"]["week"] = {
            "data": rediangainnian.zhishu_week("1.000001")
        }
        self.data["a"]["month"] = {
            "data": rediangainnian.zhishu_month("1.000001")
        }

        self.data["a50"]["week"] = {
            "data": rediangainnian.zhishu_week("1.000016")
        }
        self.data["a50"]["month"] = {
            "data": rediangainnian.zhishu_month("1.000016")
        }

        self.data["hs300"]["week"] = {
            "data": rediangainnian.zhishu_week("1.000300")
        }
        self.data["hs300"]["month"] = {
            "data": rediangainnian.zhishu_month("1.000300")
        }

        self.data["zt500"]["week"] = {
            "data": rediangainnian.zhishu_week("1.000905")
        }
        self.data["zt500"]["month"] = {
            "data": rediangainnian.zhishu_month("1.000905")
        }

        self.data["zt1000"]["week"] = {
            "data": rediangainnian.zhishu_week("1.000852")
        }
        self.data["zt1000"]["month"] = {
            "data": rediangainnian.zhishu_month("1.000852")
        }

        self.data["zt2000"]["week"] = {
            "data": rediangainnian.zhishu_week("2.932000")
        }
        self.data["zt2000"]["month"] = {
            "data": rediangainnian.zhishu_month("2.932000")
        }
