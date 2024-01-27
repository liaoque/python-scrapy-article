import datetime

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

        dateInfo = gp.getToday(current_time)
        current_time = datetime.datetime.strptime(dateInfo["today"], "%Y-%m-%d").strftime("%Y%m%d")

        code_config.CodeConfig().getCodeConfig()
        code_config.CodeConfig().setFd(request.GET.get('fd'))
        code_config.CodeConfig().setFd(request.GET.get('yd'))

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
        for code, item in data.items():
            if code == "002512":
                pass

        # 取跌停股票
        # dieting_table1 = (table.find_one({}, {"YiZiDieTing": 1}))

        yuan_yin = yuan_yin_data.getYuanYin(data)

        # 查昨原因
        # history_day_data = history_day_table.find({"history_day": {"$lt": current_time}},
        #                                           sort=[("history_day", -1)]).limit(2)
        # history_day_data = list(history_day_data)
        yeasterday_data = {}
        before_yesterday_data = {}
        if len(dateInfo["yesterday"]):
            yesterday = datetime.datetime.strptime(dateInfo["yesterday"], "%Y-%m-%d").strftime("%Y%m%d")
            yeasterday_data = self.db['d' + yesterday].find_one({}, {"yuan_yin": 1})
            if yeasterday_data is None:
                yeasterday_data = {}
        if len(dateInfo["before_yesterday"]):
            yesterday_day = datetime.datetime.strptime(dateInfo["before_yesterday"], "%Y-%m-%d").strftime("%Y%m%d")
            before_yesterday_data = self.db['d' + yesterday_day].find_one({}, {"yuan_yin": 1})
            if before_yesterday_data is None:
                before_yesterday_data = {}

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

        # 一字板
        jing_zhang_ting = len(list(filter(lambda x: x[1]["yi_zi_ban"] == 1, data.items())))
        # 一字跌停
        yi_zi_die_ting = len(list(filter(lambda x: x[1]["yi_zi_die_ting"] == 1, data.items())))
        # 炸板
        zha_ban = len(list(filter(lambda x: x[1]["zha_ban"] == 1, data.items())))
        # 漲停
        zhu_chuang_zhang_ting = len(list(filter(lambda x: x[1]["zhu_chuang_zhang_ting"] == 1, data.items())))
        # 跌停
        shou_die_ting = len(list(filter(lambda x: x[1]["dietingfengdane"] > 0, data.items())))
        # 竞价上涨
        jing_shang_zhang = len(list(filter(lambda x: x[1]["jingjiazhangfutoday"] > 0, data.items())))
        # 竞价下跌
        jing_xia_die = len(list(filter(lambda x: x[1]["jingjiazhangfutoday"] < 0, data.items())))
        # 收上涨
        shou_shang_zhang = len(list(filter(lambda x: x[1]["zhangdiefuqianfuquantoday"] > 0, data.items())))
        # 收下跌
        shou_xia_die = len(list(filter(lambda x: x[1]["zhangdiefuqianfuquantoday"] < 0, data.items())))
        result["other"] = {
            "zha_ban_lv": round(zha_ban / zhu_chuang_zhang_ting * 100, 2),
            "jing_zhang_ting": jing_zhang_ting,
            "jing_die_ting": yi_zi_die_ting,
            "shou_zhang_ting": zhu_chuang_zhang_ting,
            "shou_die_ting": shou_die_ting,
            "jing_shang_zhang": jing_shang_zhang,
            "jing_xia_die": jing_xia_die,
            "shou_shang_zhang": shou_shang_zhang,
            "shou_xia_die": shou_xia_die,
            "zhu_xian": d["zhu_xian"]
        }

        result["config"] = code_config.CodeConfig().getCodeConfig()

        return JsonResponse(result)
