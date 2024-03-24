import datetime

import requests
from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponse, JsonResponse

from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, \
    biao_shai_xuan, yuan_yin_data
from application.settings import DATABASES
import time
from pymongo import MongoClient
import string

from django.views import View
from dvadmin.wb.config import code_config
from dvadmin.wb.utils import gp


class ZhuXianGnsView(View):

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

        gns = []
        dtgns = []
        dateInfo = gp.getTodayLimit(current_time)
        for date in dateInfo['dates']:
            today = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
            yuan_yin = self.db['d' + today].find_one({}, {"yuan_yin": 1})

            c = [item["c"] for item in yuan_yin["yuan_yin"]["zhu_xian"]]
            c = sorted(list(set(c)), key=lambda x: x, reverse=True)
            minc = min(c[:2])

            for d in yuan_yin["yuan_yin"]["zhu_xian"]:
                if d["c"] < minc:
                    continue
                gns.append(d["gn"])
            for gn, d in yuan_yin["yuan_yin"]["die_ting_sort"].items():
                dtgns.append(gn)
            for gn, d in yuan_yin["yuan_yin"]["zha_ban_sort"].items():
                dtgns.append(gn)

        return JsonResponse({"gn": gns, "dtgn": dtgns})
