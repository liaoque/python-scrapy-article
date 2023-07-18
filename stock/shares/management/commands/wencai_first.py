import requests
import numpy as np
from datetime import datetime, timedelta

from shares.management.commands.wencai2 import trend, trendCode, acodes, common, pic_n
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        today = datetime.today().strftime('%Y-%m-%d')
        # today = "2023-07-17"
        codes2 = trend.trendNight(today)
        concepts_sorted = trend.top(codes2)
        tomorrow_concept = [item["concept"] for item in concepts_sorted]
        # print(tomorrow_concept)

        str = "first：%s\n" % ("\",\"".join(tomorrow_concept))
        send_mail(
            'first %s' % today,
            str,
            'lovemeand1314@163.com',
            ['844596330@qq.com'],
            fail_silently=False,
        )
