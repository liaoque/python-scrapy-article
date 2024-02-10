from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponse, JsonResponse

from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, \
    biao_shai_xuan
from application.settings import DATABASES
import time
from pymongo import MongoClient
import re

from django.views import View
from dvadmin.utils.json_response import ErrorResponse, DetailResponse
from dvadmin.wb.config import code_config
from dvadmin.wb.utils import gp
import datetime


class BaseView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = MongoClient(DATABASES['wb']['CLIENT']['host'],
                                  DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
        self.db = self.client['wb']  # 选择你的数据库

    def __del__(self):
        self.client.close()

    def get(self, request, *args, **kwargs):
        current_time = request.GET.get('current_time')
        if current_time is None or current_time == "":
            return JsonResponse({"error": "current_time must"})

        dateInfo = gp.getToday(current_time)
        current_time = datetime.datetime.strptime(dateInfo["today"], "%Y-%m-%d").strftime("%Y%m%d")

        code_config.CodeConfig().getCodeConfig()
        code_config.CodeConfig().setFd(request.GET.get('fd'))
        code_config.CodeConfig().setYd(request.GET.get('yd'))

        # 取所有数据
        table = self.db['d' + current_time]  # 选择你的数据库
        table1 = table.find_one({}, {"Table1FromJSON": 1})
        if table1 is None:
            raise TypeError("Table1FromJSON is empty")

        table2 = table.find_one({}, {"Table": 1})
        data2 = []
        if table2 and "Table" in table2:
            data2 = table2["Table"]

        # history_day_table = self.db['history_day']
        # if len(table1) > 0:
        #     history_day_data = history_day_table.find_one({"history_day": current_time})
        #     if history_day_data is None:
        #         history_day_data = {"history_day": current_time}
        #         history_day_table.insert_one(history_day_data)

        data1 = table1["Table1FromJSON"]

        # table1 合并概念
        data1 = gn.gn_merge({item["code"][0:-3]: item for item in data1})

        # table2 合并概念
        data2 = gn.gn_merge({item["code"]: item for item in data2})

        # 标记涨停和跌停， 炸板， 创百日新高， 一字板， 首板， N10, N20
        data = init_data.tag_zhangting_dieting(data1)

        #  标记 炸板， 创百日新高， 一字板， 首板， N10, N20
        table1 = (table.find_one({}, {
            "JinCengZhangTing": 1,
            "ChuangBaiRiXinGao": 1,
            "YiZiBan": 1,
            "ZhuChuangZhangTing": 1,
            "YiDong": 1,
            "N10": 1,
            "N20": 1,
            "YiZiDieTing": 1,
            "ZhuXianYuan": 1,
        }))
        data = init_data.tag_all(table1, data)

        return JsonResponse({
            "jin_ceng_zhang_ting": [],
            "jin_ceng_die_ting": [],
            "zuo_ceng_zhang_ting": [],
            "zuo_ceng_die_ting": [],
            "duan_ban": [],
            "fan_bao": [],
            "chuang_bai_ri_xin_gao": [item for key, item in data.items() if item["chuang_bai_ri_xin_gao"] == 1],
            "chuang_bai_ri_xin_di": [],
            "zhu_chuang_zhang_ting": [item for key, item in data.items() if item["zhu_chuang_zhang_ting"] == 1],
            "yi_dong": [item for key, item in data.items() if item["yi_dong"] == 1],
            "yi_zi_ban": [item for key, item in data.items() if item["yi_zi_ban"] == 1],
            "yi_zi_die_ting": [item for key, item in data.items() if item["yi_zi_die_ting"] == 1],
            "n10": [item for key, item in data.items() if item["n10"] == 1],
            "n20": [item for key, item in data.items() if item["n20"] == 1],
            "zhu_xian_yuan": [item for key, item in data.items() if item["zhu_xian_yuan"] == 1],
            "table": data2,
        })
