import requests
import numpy as np
from datetime import datetime, timedelta
from collections import OrderedDict

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n, trendDown
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        today = datetime.today().strftime('%Y-%m-%d')
        # today = "2023-08-03"
        codes2 = trend.trendFirst(today)
        concepts_sorted = trend.top(codes2)
        # tomorrow_concept = [item["concept"] for item in concepts_sorted]
        print(concepts_sorted)

        jingjia_up = sum([item["jingjia"] for item in codes2])

        str = "竞价涨停\n"
        for item in concepts_sorted:
            str = str + "%s\n" % (item["concept"])
            for item2 in item["codes2"][:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])
            str = str + "++++++++++\n"

        str = str + "竞价跌停\n"
        codes2 = trendDown.trendFirstDown(today)
        concepts_sorted = trend.top(codes2)
        for item in concepts_sorted:
            str = str + "%s\n" % (item["concept"])
            for item2 in item["codes2"][:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])
            str = str + "++++++++++\n"
        
        jingjia_down = sum([item["jingjia"] for item in codes2])

        file_path = "first.json"
        json_data = common.read_json_file(file_path)
        json_data[today] = {
            "jingjia": {
                "up": jingjia_up,
                "down": jingjia_down,
            }
        }
        json_data = OrderedDict(sorted(json_data.items()))
        json_data = dict(json_data)
        common.write_json_file(file_path, json_data)

        str += "\n情绪：平"
        yeastDayData = common.get_previous_key_value(json_data, today)
        if yeastDayData is not None:
            if yeastDayData["jingjia"]["down"] != 0:
                if json_data[today]["jingjia"]["down"] > yeastDayData["jingjia"]["down"]:
                    str = "情绪：好"
                elif  json_data[today]["jingjia"]["down"] < yeastDayData["jingjia"]["down"]:
                    str = "情绪：差"
            elif yeastDayData["jingjia"]["up"] != 0:
                if json_data[today]["jingjia"]["up"] > yeastDayData["jingjia"]["up"]:
                    str = "情绪：好"
                elif  json_data[today]["jingjia"]["up"] < yeastDayData["jingjia"]["up"]:
                    str = "情绪：差"


        # str = "first：%s\n" % ("\",\"".join(tomorrow_concept))
        send_mail(
            'first %s' % today,
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
