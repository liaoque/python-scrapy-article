import requests
import numpy as np
from datetime import datetime, timedelta
from collections import OrderedDict
from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n, trendDown, concept1, concept2
from django.core.management.base import BaseCommand, CommandError

from django.core.mail import send_mail


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        file_path = "data.json"
        json_data = common.read_json_file(file_path)
        today = datetime.today().strftime('%Y-%m-%d')
        # today = "2023-08-03"

        codes2 = trend.trendFirst(today)

        codes3 = trend.trendNight(today)
        codes2 = codes3 + codes2
        codes2 = list({d['code']: d for d in codes2}.values())

        concepts_sorted = trend.top(codes2)

        json_data[today] = [{"concept": item["concept"], "codes": item["codes"]} for item in concepts_sorted]
        json_data = OrderedDict(sorted(json_data.items()))
        json_data = dict(json_data)
        common.write_json_file(file_path, json_data)
        # tomorrow_concept = [item["concept"] for item in concepts_sorted]

        str = "补涨概念：\n"
        for item in concepts_sorted:
            str = str + "%s\n" % (item["concept"])
            for item2 in item["codes2"][:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])
            str = str + "++++++++++\n"

        str = str + "=================================\n"
        str = str + "补涨选股\n"

        data = pic_n.getData(datetime.today().strftime('%Y-%m-%d'), "000001.SZ", -10)
        days = data

        yeasterday = days[len(days) - 2]
        yeasteryeasterday = days[len(days) - 3]
        print(yeasterday, yeasteryeasterday, )
        for item in concepts_sorted:
            # 打印概念和龙头
            print(item["concept"], "-----龙头:", item["codes2"][0]["name"], item["codes2"][0]["code"],
                  item["codes2"][0]["concept"])

            str = str + "%s, %s, %s, %s\n" % (
                item["concept"], "-----龙头:", item["codes2"][0]["name"], item["codes2"][0]["code"],)
            # 查该概念的符合的股票集合
            codes2 = acodes.buzhang(today, yeasterday, yeasteryeasterday, item["concept"])

            intersection2 = []
            for codes3 in codes2:
                if codes3["code"] in item["codes"]:
                    continue
                if codes3["code"] > "680000":
                    continue
                # 匹配概念，跟龙头， 记录跟龙头的匹配度
                intersection = list(set(codes3["concept"]) & set(item["codes2"][0]["concept"]))
                intersection2.append({
                    "code": codes3["code"],
                    "name": codes3["name"],
                    "c": len(intersection),
                    "intersection": intersection,
                })

            # 匹配度排序
            intersection2 = sorted(intersection2, key=lambda x: x['c'], reverse=True)
            for item2 in intersection2[:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])

        str = str + "\n+++++++++++\n"
        str = str + "下跌趋势\n"
        codes2 = trendDown.trendNightDown(today)
        concepts_sorted = trend.top(codes2)
        for item in concepts_sorted:
            str = str + "%s\n" % (item["concept"])
            for item2 in item["codes2"][:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])
            str = str + "++++++++++\n"

        codes4 = trend.trendNight(today, False)

        str = str + "concept1：\n"
        str = str + joinCode(concept1.conceptCom(codes4))
        str = str + "concept2：\n"
        str = str + joinCode(concept2.conceptCom(codes4))

        send_mail(
            'night %s' % today,
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )


def joinCode(concepts_sorted):
    str = ""
    for item in concepts_sorted:
        str = str + "%s\n" % (item["concept"])
        for item2 in item["codes2"][:5]:
            str = str + "%s %s\n" % (item2["code"], item2["name"])
        str = str + "++++++++++\n"
    return str
