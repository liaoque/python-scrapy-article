from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponse, JsonResponse

from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, biao_shai_xuan
from application.settings import DATABASES
import time
from pymongo import MongoClient
import string

from django.views import View
class ResultView(View):


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
        table = self.db['d' + current_time]  # 选择你的数据库
        table2 = (table.find_one({}, {"yuan_yin": 1}))
        return JsonResponse({"data": table2["yuan_yin"]})




