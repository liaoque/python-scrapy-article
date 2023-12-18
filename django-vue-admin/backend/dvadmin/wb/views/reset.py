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


class ResetView(View):

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

        # 取所有数据
        table = self.db['d' + current_time]  # 选择你的数据库
        table1 = table.find_one({}, {"Table1FromJSON": 1})
        if table1 is None:
            raise TypeError("Table1FromJSON is empty")

        table2 = table.find_one({}, {"Table": 1})
        data2 = []
        if table2:
            data2 = table2["Table"]

        history_day_table = self.db['history_day']
        if len(table1) > 0:
            history_day_data = history_day_table.find_one({"history_day": current_time})
            if history_day_data is None:
                history_day_data = {"history_day": current_time}
                history_day_table.insert_one(history_day_data)

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
        for code, item in data.items():
            if code == "002512":
                pass


        # 取跌停股票
        # dieting_table1 = (table.find_one({}, {"YiZiDieTing": 1}))

        yuan_yin = yuan_yin_data.getYuanYin(data)

        # 查昨原因
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
            table.update_one({"_id": table1["_id"]}, {
                "$set": {
                    # "Table1FromJSON": j,
                    # "Table": data2.values(),
                    "yuan_yin": yuan_yin,
                }
            })
            self.client.close()
            return JsonResponse({})

        today_data = {
            "yuan_yin": yuan_yin
        }

        # j = list(data.values())
        table.update_one({"_id": table1["_id"]}, {
            "$set": {
                # "Table1FromJSON": j,
                # "Table": data2.values(),
                "yuan_yin": yuan_yin,
            }
        })
        self.client.close()

        # 创业版概念， 生成所属概念
        chuang_ye_ban_gn = suo_shu_gai_nian.suo_shu_gai_nian(data1, data2, today_data, yeasterday_data)

        #    a= chuang_ye_ban_gn["专精特新"]
        # 补涨前，先合并昨天和前天的首版 到昨天
        if "yuan_yin" in before_yesterday_data and "yuan_yin" in yeasterday_data:
            yeasterday_data["yuan_yin"] = bu_zhang.merge_shou_ban(yeasterday_data["yuan_yin"],
                                                                  before_yesterday_data["yuan_yin"])

        # 主板，创业板 数据
        bu_zhang_data = bu_zhang.bu_zhang(data, chuang_ye_ban_gn, today_data["yuan_yin"], yeasterday_data["yuan_yin"])

        d = {
            "chuang_ye_ban_gn": chuang_ye_ban_gn,
            "zhu_xian": yuan_yin["zhu_xian"],
            "bu_zhang_data": bu_zhang_data,
            "qing_xu": jie_guo.qingxu(today_data["yuan_yin"], yeasterday_data["yuan_yin"])
        }

        d2 = biao_shai_xuan.biao_shai_xuan(d, data1)
        d["chuang_data"] = d2["chuang_data"]
        d["zhu_data"] = d2["zhu_data"]

        # d.update(d2)
        result = pi_pei_gai_nian.pi_pei_gai_nian(d)

        self.client.close()
        result["chuang_ye_ban_gn"] = [item for key, item in d['chuang_ye_ban_gn'].items()]
        result["qing_xu"] = d["qing_xu"]
        result["bu_zhang"] = d["bu_zhang_data"]
        result["biao_shai_xuan"] = d2["biao_shai_xuan"]
        result["gn"] = d2["gn"]

        jing_zhang_ting = len(list(filter(lambda x: x[1].yi_zi_ban == 1, data1.items())))
        yi_zi_die_ting = len(list(filter(lambda x: x[1].yi_zi_die_ting == 1, data1.items())))
        zha_ban = len(list(filter(lambda x: x[1].zha_ban == 1, data1.items())))
        zhu_chuang_zhang_ting = len(list(filter(lambda x: x[1].zhu_chuang_zhang_ting == 1, data1.items())))
        shou_die_ting = len(list(filter(lambda x: x[1].dietingfengdane > 0, data1.items())))
        jing_shang_zhang = len(list(filter(lambda x: x[1].jingjiazhangfutoday > 0, data1.items())))
        jing_xia_die = len(list(filter(lambda x: x[1].jingjiazhangfutoday < 0, data1.items())))
        shou_shang_zhang = len(list(filter(lambda x: x[1].zhangdiefuqianfuquantoday > 0, data1.items())))
        shou_xia_die = len(list(filter(lambda x: x[1].zhangdiefuqianfuquantoday < 0, data1.items())))
        result["other"] = {
            "zha_ban_lv": zha_ban / zhu_chuang_zhang_ting,
            "jing_zhang_ting": jing_zhang_ting,
            "jing_die_ting": yi_zi_die_ting,
            "shou_zhang_ting": zhu_chuang_zhang_ting,
            "shou_die_ting": shou_die_ting,
            "jing_shang_zhang": jing_shang_zhang,
            "jing_xia_die":jing_xia_die,
            "shou_shang_zhang": shou_shang_zhang,
            "shou_xia_die": shou_xia_die
        }

        return JsonResponse(result)
