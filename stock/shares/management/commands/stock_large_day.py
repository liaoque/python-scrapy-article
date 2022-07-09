import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_industry_month import SharesIndustryMonth
import time
import requests
from shares.model.stock_members import SharesMembers
from shares.model.shares_date import SharesDate
from shares.model.shares_month import SharesMonth

# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = ' 查股票放量'

    def handle(self, *args, **options):
        codeList = SharesName.getCodeList()
        codeLargeList = {
            "date":[],
            "month":[],
        }
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('-date_as')[:5]
            endCount = sharesItem5[0].buy_count
            count4 = sum([ item.buy_count for item in sharesItem5[1:]]) / 4
            if endCount / count4 > 1.8:
                codeLargeList["date"].append(item.code)

            sharesItem6 = SharesMonth.objects.filter(code_id=item.code).order_by('-p_year', '-p_month')[:2]
            if len(sharesItem6) < 2:
                continue
            if sharesItem6[0].buy_count / sharesItem6[1].buy_count > 2:
                codeLargeList["month"].append(item.code)




