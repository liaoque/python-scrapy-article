from django.shortcuts import render
import json
# Create your views here.
from django.http import HttpResponse, JsonResponse

from polls.core import init_data, streak_rise, bu_zhang, suo_shu_gai_nian, pi_pei_gai_nian, gn, jie_guo, biao_shai_xuan
from wb.settings import DATABASES
import time
from pymongo import MongoClient
import string


def index(request):
    # with open('file.json', 'r') as f:
    #     history_data = json.load(f)

    client = MongoClient(DATABASES['wb']['CLIENT']['host'],
                         DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
    db = client['wb']  # 选择你的数据库
    current_timestamp = time.time()
    current_time = time.strftime("%Y%m%d", time.localtime())
    print('d' + current_time)

    current_time = "20230831"

    # 取所有数据
    table = db['d' + current_time]  # 选择你的数据库
    table1 = table.find_one({}, {"Table1FromJSON": 1})
    if table1 is None:
        raise TypeError("Table1FromJSON is empty")

    table2 = table.find_one({}, {"Table": 1})
    data2 = []
    if table2:
        data2 = table2["Table"]

    history_day_table = db['history_day']
    if len(table1) > 0:
        history_day_data = history_day_table.find_one({"history_day": current_time})
        if history_day_data is None:
            history_day_data = {"history_day": current_time}
            history_day_table.insert_one(history_day_data)

    data1 = table1["Table1FromJSON"]
    data1 = gn.gn_merge({item["code"][0:-3]: item for item in data1})

    data2 = gn.gn_merge({item["code"]: item for item in data2})

    # 标记趋势
    data = init_data.step1(data1)

    # 标记炸板
    table1 = (table.find_one({}, {"JinCengZhangTing": 1}))
    data = init_data.step2(table1, data)

    # 标记百日新高
    table1 = (table.find_one({}, {"ChuangBaiRiXinGao": 1}))
    data = init_data.step3(table1, data)

    # 标记一字板
    table1 = (table.find_one({}, {"YiZiBan": 1}))
    data = init_data.step4(table1, data)

    # 标记 首版
    zhuchuang_table1 = (table.find_one({}, {"ZhuChuangZhangTing": 1}))
    data = init_data.step5(zhuchuang_table1, data)

    # 异动
    yidong_table1 = (table.find_one({}, {"YiDong": 1}))
    data = init_data.step6(yidong_table1, data)

    # n10
    n10_table1 = (table.find_one({}, {"N10": 1}))
    data = init_data.step7(n10_table1, data)

    # n20
    n20_table1 = (table.find_one({}, {"N20": 1}))
    data = init_data.step8(n20_table1, data)

    # 取跌停股票
    dieting_table1 = (table.find_one({}, {"YiZiDieTing": 1}))

    lianzhang_code_page = {
        # 取连涨股票
        "lianzhanggupiao": streak_rise.step1(zhuchuang_table1, data),
        # 取跌停股票
        "dietinggupiao": streak_rise.step2(dieting_table1, data),
        # 取炸板股票
        "zhabangupiao": streak_rise.step3(data),
        # 取创百日新高股票
        "chuangbairixingao": streak_rise.step4(data),
        # 取一字板股票
        "yizibangupiao": streak_rise.step5(data),
        # 取首板股票
        "shoubangupiao": streak_rise.step5_1(data),
    }
    return JsonResponse(lianzhang_code_page["shoubangupiao"])
    lianzhang_page = {
        # 生成连涨概念 计算概念出现得次数
        "lianzhanggainian": streak_rise.step6(lianzhang_code_page["lianzhanggupiao"]),

        # 生成跌停概念
        "dietinggainian": streak_rise.step7(lianzhang_code_page["dietinggupiao"]),

        # 生成炸板概念
        "zhabangainian": streak_rise.step8(lianzhang_code_page["zhabangupiao"]),

        # 生成创百日新高概念
        "chuangbairixingaogainnian": streak_rise.step9(lianzhang_code_page["chuangbairixingao"]),

        # 生成一字板概念
        "yizibangainian": streak_rise.step10(lianzhang_code_page["yizibangupiao"]),

        # 生成首板概念
        "shoubangainian": streak_rise.step11(lianzhang_code_page["shoubangupiao"]),
    }

    # 取涨停原因， 匹配涨停概念， 并标记最多的原因得次数
    lianzhang_code_page["lianzhanggupiao"] = streak_rise.step12(lianzhang_code_page["lianzhanggupiao"],
                                                                lianzhang_page["lianzhanggainian"])

    # 取跌停原因
    lianzhang_code_page["dietinggupiao"] = streak_rise.step13(lianzhang_code_page["dietinggupiao"],
                                                              lianzhang_page["dietinggainian"])

    # 取炸板原因
    lianzhang_code_page["zhabangupiao"] = streak_rise.step14(lianzhang_code_page["zhabangupiao"],
                                                             lianzhang_page["zhabangainian"])

    # 取创百日新高原因
    lianzhang_code_page["chuangbairixingao"] = streak_rise.step15(lianzhang_code_page["chuangbairixingao"],
                                                                  lianzhang_page["chuangbairixingaogainnian"])

    # 取一字板原因
    lianzhang_code_page["yizibangupiao"] = streak_rise.step16(lianzhang_code_page["yizibangupiao"],
                                                              lianzhang_page["yizibangainian"])

    # 取首板原因
    lianzhang_code_page["shoubangupiao"] = streak_rise.step17(lianzhang_code_page["shoubangupiao"],
                                                              lianzhang_page["shoubangainian"])

    yuan_yin = {
        # 排列涨停原因，对概念计算竞价未匹配
        "lian_zhang_sort": streak_rise.step18(lianzhang_code_page["lianzhanggupiao"],
                                              lianzhang_page["lianzhanggainian"]),

        # 排列跌停原因
        "die_ting_sort": streak_rise.step19(lianzhang_code_page["dietinggupiao"], lianzhang_page["dietinggainian"]),

        # 排列炸板原因
        "zha_ban_sort": streak_rise.step20(lianzhang_code_page["zhabangupiao"], lianzhang_page["zhabangainian"]),

        # 排列创百日新高原因
        "chuang_bai_ri_xin_gao_sort": streak_rise.step21(lianzhang_code_page["chuangbairixingao"],
                                                         lianzhang_page["chuangbairixingaogainnian"]),

        # 排列一字板原因
        "yi_zi_ban_sort": streak_rise.step22(lianzhang_code_page["yizibangupiao"], lianzhang_page["yizibangainian"]),

        # 排列首板原因
        "shou_ban_sort": streak_rise.step23(lianzhang_code_page["shoubangupiao"], lianzhang_page["shoubangainian"]),

        # 排列竞涨停竞跌停， 可以当作情绪看待
        "jing_jia_sort": streak_rise.step24(lianzhang_code_page["yizibangupiao"], lianzhang_code_page["dietinggupiao"]),

        # 排列5日涨跌幅，取每个概念涨跌幅最高得
        "day_5_sort": streak_rise.step25(data),
    }

    # 查昨原因
    history_day_data = history_day_table.find({"history_day": {"$lt": current_time}}, sort=[("history_day", -1)]).limit(
        2)
    history_day_data = list(history_day_data)
    yeasterday_data = {}
    before_yesterday_data = {}
    if len(history_day_data) == 1:
        yesterday = history_day_data[0]["history_day"][0]
        yeasterday_data = db['d' + yesterday].find_one({}, {"yuan_yin": 1})
    if len(history_day_data) == 2:
        yesterday_day = history_day_data[1]["history_day"][0]
        before_yesterday_data = db['d' + yesterday_day].find_one({}, {"yuan_yin": 1})
    return JsonResponse(yuan_yin)
    if "yuan_yin" not in yeasterday_data:
        j = list(data.values())
        table.update_one({"_id": table1["_id"]}, {
            "$set": {
                "Table1FromJSON": j,
                "yuan_yin": yuan_yin,
            }
        })
        client.close()
        return JsonResponse({})

    today_data = {
        "yuan_yin": yuan_yin
    }

    j = list(data.values())
    table.update_one({"_id": table1["_id"]}, {
        "$set": {
            "Table1FromJSON": j,
            "yuan_yin": yuan_yin,
        }
    })
    client.close()
    # 创业版概念
    chuang_ye_ban_gn = suo_shu_gai_nian.suo_shu_gai_nian(data1, data2, today_data, yeasterday_data)
    return JsonResponse(chuang_ye_ban_gn)

    # 补涨前，先合并昨天和前天的首版 到昨天
    yeasterday_data = bu_zhang.merge_shou_ban(yeasterday_data, before_yesterday_data)


    # 主板，创业板 数据
    bu_zhang_data = bu_zhang.bu_zhang(data, today_data, yeasterday_data)

    d = {
        "chuang_ye_ban_gn": chuang_ye_ban_gn,
        "bu_zhang_data": bu_zhang_data,
        "qing_xu": jie_guo.qingxu(today_data, yeasterday_data)
    }

    d2 = biao_shai_xuan.biao_shai_xuan(d, data1)

    d.update(d2)
    result = pi_pei_gai_nian.pi_pei_gai_nian(d)

    client.close()
    return JsonResponse(result)


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
