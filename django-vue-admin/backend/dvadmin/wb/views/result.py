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
from dvadmin.utils.json_response import ErrorResponse,DetailResponse

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
        table1 = table.find_one({}, {"Table1FromJSON": 1})
        if table1 is None:
            return ErrorResponse(msg="table1 is None")

        table2 = table.find_one({}, {"Table": 1})
        data2 = []
        if table2:
            data2 = table2["Table"]
        data1 = table1["Table1FromJSON"]
        data1 = ({item["code"][0:-3]: item for item in data1})

        data2 = gn.gn_merge({item["code"]: item for item in data2})

        # 查昨原因
        history_day_table = self.db['history_day']
        history_day_data = history_day_table.find({"history_day": {"$lt": current_time}},
                                                  sort=[("history_day", -1)]).limit(2)
        history_day_data = list(history_day_data)
        yeasterday_data = {}
        before_yesterday_data = {}
        if len(history_day_data) >= 1:
            yesterday = history_day_data[0]["history_day"]
            yeasterday_data = self.db['d' + yesterday].find_one({}, {"yuan_yin": 1})
        if len(history_day_data) == 2:
            yesterday_day = history_day_data[1]["history_day"]
            before_yesterday_data = self.db['d' + yesterday_day].find_one({}, {"yuan_yin": 1})

        if "yuan_yin" not in yeasterday_data:
            return ErrorResponse(msg="yeasterday yuan_yin is None")

        today_data = (table.find_one({}, {"yuan_yin": 1}))


        # 创业版概念
        chuang_ye_ban_gn = suo_shu_gai_nian.suo_shu_gai_nian(data1, data2, today_data, yeasterday_data)

        #    a= chuang_ye_ban_gn["专精特新"]
        # 补涨前，先合并昨天和前天的首版 到昨天
        if "yuan_yin" in before_yesterday_data and "yuan_yin" in yeasterday_data:
            yeasterday_data["yuan_yin"] = bu_zhang.merge_shou_ban(yeasterday_data["yuan_yin"],
                                                                  before_yesterday_data["yuan_yin"])

        # 主板，创业板 数据
        bu_zhang_data = bu_zhang.bu_zhang(data1, today_data["yuan_yin"], yeasterday_data["yuan_yin"])

        d = {
            "chuang_ye_ban_gn": chuang_ye_ban_gn,
            "bu_zhang_data": bu_zhang_data,
            "qing_xu": jie_guo.qingxu(today_data["yuan_yin"], yeasterday_data["yuan_yin"])
        }

        d2 = biao_shai_xuan.biao_shai_xuan(d, data1)

        d.update(d2)
        result = pi_pei_gai_nian.pi_pei_gai_nian(d)

        # self.client.close()
        result["qing_xu"] = d["qing_xu"]
        result["chuang_ye_ban_gn"] = [ item for key, item in  d["chuang_ye_ban_gn"].items()]
        result["bu_zhang_data"] =d["bu_zhang_data"]
        result["zhu_data"] =[ item for key, item in  d2["zhu_data"].items()]
        result["chuang_data"] =[ item for key, item in  d2["chuang_data"].items()]
        return JsonResponse({"data": result})


