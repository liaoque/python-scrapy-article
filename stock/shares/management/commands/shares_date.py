import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_date import SharesDate
import time


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
        sql = '''
                select 1 as id, date_as from mc_shares where date_as >= '2022-03-31' group  by date_as ;
                '''
        return Shares.objects.raw(sql)