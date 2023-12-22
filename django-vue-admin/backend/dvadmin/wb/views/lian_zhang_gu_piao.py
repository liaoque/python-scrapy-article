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
from dvadmin.wb.utils import gp
import datetime

class LianZhangGuPiao(View):

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
        current_time = datetime.datetime.strptime(dateInfo.today, "%Y-%m-%d").strftime("%Y%m%d")

        # 取所有数据
        table = self.db['d' + current_time]  # 选择你的数据库
        table1 = table.find_one({}, {"Table1FromJSON": 1})
        if table1 is None:
            raise TypeError("Table1FromJSON is empty")

        table2 = table.find_one({}, {"Table": 1})
        data2 = []
        if table2:
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

        # 取跌停股票
        # dieting_table1 = (table.find_one({}, {"YiZiDieTing": 1}))

        yuan_yin = yuan_yin_data.getLianZhangGuPiao(data)
        yuan_yin1 = yuan_yin_data.getLianZhangGiNian(yuan_yin)
        yuan_yin["lianzhanggupiao"] = streak_rise.zhang_ting_shi_pei_gu_piao(
            yuan_yin["lianzhanggupiao"],
            yuan_yin1["lianzhanggainian"])

        yuan_yin["chuangbairixingao"] = streak_rise.chuang_bai_ri_xin_gao_shi_pei_gai_nian(
            yuan_yin["chuangbairixingao"],
            yuan_yin1["chuangbairixingaogainnian"])
        # 取一字板原因
        yuan_yin["yizibangupiao"] = streak_rise.yi_zi_ban_shi_pei_gu_piao(
            yuan_yin["yizibangupiao"],
            yuan_yin1["yizibangainian"])

        # 取首板原因
        yuan_yin["shoubangupiao"] = streak_rise.shou_ban_shi_pei_gu_piao(
            yuan_yin["shoubangupiao"],
            yuan_yin1["shoubangainian"])
        yuan_yin['chuangbairixingao'] = [item for key, item in yuan_yin['chuangbairixingao'].items()]
        yuan_yin['dietinggupiao'] = [item for key, item in yuan_yin['dietinggupiao'].items()]
        yuan_yin['lianzhanggupiao'] = [item for key, item in yuan_yin['lianzhanggupiao'].items()]
        yuan_yin['shoubangupiao'] = [item for key, item in yuan_yin['shoubangupiao'].items()]
        yuan_yin['yizibangupiao'] = [item for key, item in yuan_yin['yizibangupiao'].items()]
        yuan_yin['zhabangupiao'] = [item for key, item in yuan_yin['zhabangupiao'].items()]
        # yuan_yin.dietinggupiao = [item for key, item in yuan_yin.dietinggupiao]
        # yuan_yin.lianzhanggupiao = [item for key, item in yuan_yin.lianzhanggupiao]
        # yuan_yin.shoubangupiao = [item for key, item in yuan_yin.shoubangupiao]
        #
        # yuan_yin.yizibangupiao = [item for key, item in yuan_yin.yizibangupiao]
        # yuan_yin.zhabangupiao = [item for key, item in yuan_yin.zhabangupiao]
        self.client.close()
        return JsonResponse(yuan_yin)