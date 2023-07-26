import requests
import numpy as np
from datetime import datetime, timedelta
from collections import OrderedDict
from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n
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
        # today = "2023-07-17"
        codes2 = trend.trendNight(today)
        concepts_sorted = trend.top(codes2)


        json_data[today] = [{"concept": item["concept"], "codes": item["codes"]} for item in concepts_sorted]
        json_data = OrderedDict(sorted(json_data.items()))
        json_data = dict(json_data)
        common.write_json_file(file_path, json_data)
        # tomorrow_concept = [item["concept"] for item in concepts_sorted]


        str = ""
        for item in concepts_sorted:
            str = str + "%s\n" % (item["concept"])
            for item2 in item["codes2"][:5]:
                str = str + "%s %s\n" % (item2["code"], item2["name"])
            str = str + "++++++++++\n"


        # str = "night：%s\n" % ("\",\"".join(tomorrow_concept))
        print(str)
        send_mail(
            'night %s' % today,
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )


