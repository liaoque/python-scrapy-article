from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponse, JsonResponse

from dvadmin.wb.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, \
    biao_shai_xuan
from application.settings import DATABASES
import time
from pymongo import MongoClient
import string

from django.views import View


class YuanYinView(View):

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
        table2["yuan_yin"]['chuang_bai_ri_xin_gao_sort'] = self.convert(table2["yuan_yin"]['chuang_bai_ri_xin_gao_sort'])
        table2["yuan_yin"]['die_ting_sort'] = self.convert(table2["yuan_yin"]['die_ting_sort'])
        table2["yuan_yin"]['lian_zhang_sort'] = self.convert(table2["yuan_yin"]['lian_zhang_sort'])
        table2["yuan_yin"]['shou_ban_sort'] = self.convert(table2["yuan_yin"]['shou_ban_sort'])
        table2["yuan_yin"]['yi_zi_ban_sort'] = self.convert(table2["yuan_yin"]['yi_zi_ban_sort'])
        table2["yuan_yin"]['zha_ban_sort'] = self.convert(table2["yuan_yin"]['zha_ban_sort'])

        return JsonResponse({"data": table2["yuan_yin"]})

    def convert(self, data):
        return [
            {key: [{"code": it2["code"]} for it2 in it] if key == "gai_nian_gu_piao" else it for key, it in
             item.items()} for key, item in data.items()
        ]
