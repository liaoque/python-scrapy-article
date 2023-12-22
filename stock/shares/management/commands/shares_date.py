import numpy as np
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_date import SharesDate
import time
import requests


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '补充当前的日期'

    def handle(self, *args, **options):
        dateList = self.getAllDates()
        for item in dateList:
            if SharesDate.objects.filter(date_as=item.date_as).count():
                continue
            sharesDate = SharesDate(date_as=item.date_as)
            sharesDate.save()

    def getAllDates(self):
        url = "https://37.push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=1.000001&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&end=20500101&lmt=10&_=1654277588142"
        r = requests.get(url)
        # print(r.json())
        # klines = r.json()["data"]["klines"][0]

        klines = r.json()["data"]["klines"]
        klines = [ SharesDate(date_as=item.split(",")[0]) for item in klines]
        # klines = klines.split(",")[0]
        # print(klines)
        return klines
        # sql = '''
        #         select 1 as id, date_as from mc_shares where date_as >= '2022-03-31' group  by date_as ;
        #         '''
        # return Shares.objects.raw(sql)
