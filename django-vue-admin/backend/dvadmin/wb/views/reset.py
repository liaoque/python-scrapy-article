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
        }))
        data = init_data.tag_all(table1, data)

        # 取跌停股票
        dieting_table1 = (table.find_one({}, {"YiZiDieTing": 1}))

        lianzhang_code_page = {
            # 取连涨股票
            "lianzhanggupiao": streak_rise.lian_zhang_gu_piao(data),
            # 取跌停股票
            "dietinggupiao": streak_rise.die_ting_gu_piao(dieting_table1, data),
            # 取炸板股票
            "zhabangupiao": streak_rise.zha_ban_gu_piao(data),
            # 取创百日新高股票
            "chuangbairixingao": streak_rise.bai_ri_xin_gao_gu_piao(data),
            # 取一字板股票
            "yizibangupiao": streak_rise.yi_zi_ban_gu_piao(data),
            # 取首板股票
            "shoubangupiao": streak_rise.shou_ban_gu_piao(data),
        }

        lianzhang_page = {
            # 生成连涨概念 计算概念出现得次数
            "lianzhanggainian": streak_rise.lian_zhang_gai_nian(lianzhang_code_page["lianzhanggupiao"]),

            # 生成跌停概念
            "dietinggainian": streak_rise.die_ting_gai_nian(lianzhang_code_page["dietinggupiao"]),

            # 生成炸板概念
            "zhabangainian": streak_rise.zha_ban_gai_nian(lianzhang_code_page["zhabangupiao"]),

            # 生成创百日新高概念
            "chuangbairixingaogainnian": streak_rise.chuang_bai_ri_xin_gao_gai_nian(lianzhang_code_page["chuangbairixingao"]),

            # 生成一字板概念
            "yizibangainian": streak_rise.yi_zi_ban_gai_nian(lianzhang_code_page["yizibangupiao"]),

            # 生成首板概念
            "shoubangainian": streak_rise.shou_ban_gai_nian(lianzhang_code_page["shoubangupiao"]),
        }

        # 取涨停原因， 匹配涨停概念， 并标记最多的原因得次数
        lianzhang_code_page["lianzhanggupiao"] = streak_rise.zhang_ting_shi_pei_gu_piao(lianzhang_code_page["lianzhanggupiao"],
                                                                    lianzhang_page["lianzhanggainian"])

        # 取跌停原因
        lianzhang_code_page["dietinggupiao"] = streak_rise.die_ting_shi_pei_gu_piao(lianzhang_code_page["dietinggupiao"],
                                                                  lianzhang_page["dietinggainian"])

        # 取炸板原因
        lianzhang_code_page["zhabangupiao"] = streak_rise.zha_ban_shi_pei_gu_piao(lianzhang_code_page["zhabangupiao"],
                                                                 lianzhang_page["zhabangainian"])

        # 取创百日新高原因
        lianzhang_code_page["chuangbairixingao"] = streak_rise.chuang_bai_ri_xin_gao_shi_pei_gai_nian(lianzhang_code_page["chuangbairixingao"],
                                                                      lianzhang_page["chuangbairixingaogainnian"])

        # 取一字板原因
        lianzhang_code_page["yizibangupiao"] = streak_rise.yi_zi_ban_shi_pei_gu_piao(lianzhang_code_page["yizibangupiao"],
                                                                  lianzhang_page["yizibangainian"])

        # 取首板原因
        lianzhang_code_page["shoubangupiao"] = streak_rise.shou_ban_shi_pei_gu_piao(lianzhang_code_page["shoubangupiao"],
                                                                  lianzhang_page["shoubangainian"])

        yuan_yin = {
            # 排列涨停原因，对概念计算竞价未匹配
            "lian_zhang_sort": streak_rise.zhang_ting_yuan_yin(lianzhang_code_page["lianzhanggupiao"],
                                                  lianzhang_page["lianzhanggainian"]),

            # 排列跌停原因
            "die_ting_sort": streak_rise.die_ting_yuan_yin(lianzhang_code_page["dietinggupiao"], lianzhang_page["dietinggainian"]),

            # 排列炸板原因
            "zha_ban_sort": streak_rise.zha_ban_yuan_yin(lianzhang_code_page["zhabangupiao"], lianzhang_page["zhabangainian"]),

            # 排列创百日新高原因
            "chuang_bai_ri_xin_gao_sort": streak_rise.chuang_bai_ri_xin_gao_yuan_yin(lianzhang_code_page["chuangbairixingao"],
                                                             lianzhang_page["chuangbairixingaogainnian"]),

            # 排列一字板原因
            "yi_zi_ban_sort": streak_rise.yi_zi_ban_yuan_yin(lianzhang_code_page["yizibangupiao"],
                                                 lianzhang_page["yizibangainian"]),

            # 排列首板原因
            "shou_ban_sort": streak_rise.shou_ban_yuan_yin(lianzhang_code_page["shoubangupiao"], lianzhang_page["shoubangainian"]),

            # 排列竞涨停竞跌停， 可以当作情绪看待
            "jing_jia_sort": streak_rise.jing_jia_info(lianzhang_code_page["yizibangupiao"],
                                                lianzhang_code_page["dietinggupiao"]),

            # 排列5日涨跌幅，取每个概念涨跌幅最高得
            "day_5_sort": streak_rise.max_zhang_fu5_gu_piao(data),
        }

        # 查昨原因
        history_day_data = history_day_table.find({"history_day": {"$lt": current_time}},
                                                  sort=[("history_day", -1)]).limit(
            2)
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
            j = list(data.values())
            table.update_one({"_id": table1["_id"]}, {
                "$set": {
                    "Table1FromJSON": j,
                    # "Table": data2.values(),
                    "yuan_yin": yuan_yin,
                }
            })
            self.client.close()
            return JsonResponse({})

        today_data = {
            "yuan_yin": yuan_yin
        }

        j = list(data.values())
        table.update_one({"_id": table1["_id"]}, {
            "$set": {
                "Table1FromJSON": j,
                # "Table": data2.values(),
                "yuan_yin": yuan_yin,
            }
        })
        self.client.close()

        # 创业版概念
        chuang_ye_ban_gn = suo_shu_gai_nian.suo_shu_gai_nian(data1, data2, today_data, yeasterday_data)

        #    a= chuang_ye_ban_gn["专精特新"]
        # 补涨前，先合并昨天和前天的首版 到昨天
        if "yuan_yin" in before_yesterday_data and "yuan_yin" in yeasterday_data:
            yeasterday_data["yuan_yin"] = bu_zhang.merge_shou_ban(yeasterday_data["yuan_yin"],
                                                                  before_yesterday_data["yuan_yin"])

        # 主板，创业板 数据
        bu_zhang_data = bu_zhang.bu_zhang(data, today_data["yuan_yin"], yeasterday_data["yuan_yin"])

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
        return JsonResponse(result)
