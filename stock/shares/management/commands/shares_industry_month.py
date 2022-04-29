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


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '统计每月的 行业 最高和最低'

    def handle(self, *args, **options):
        for item in SharesName.objects.filter(status=1, code_type=2):
            code = item.code
            sharesItem = SharesIndustry.objects.filter(code_id=code).order_by('date_as')[0]
            sharesItemEnd = SharesIndustry.objects.filter(code_id=code).order_by('-date_as')[0]
            p_year = sharesItem.date_as.strftime('%Y')
            p_year_end = sharesItemEnd.date_as.strftime('%Y')
            print(p_year_end)

            while p_year <= p_year_end:
                p_month = 1
                while p_month <= 12:
                    if not ((p_year == 2007 and p_month in [11, 12]) or (
                            p_year == 2008 and p_month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) or (
                                    p_year == 2009 and p_month in [7, 8, 9, 10, 11, 12]) or (p_year == 2010) or (
                                    p_year == 2011) or (
                                    p_year == 2012 and p_month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]) or (
                                    p_year == 2013 and p_month in [3, 4, 5, 6, 9, 10, 11, 12]) or (
                                    p_year == 2014 and p_month in [1, 2, ]) or (
                                    p_year == 2015 and p_month in [6, 7, 8, 9, 10, 11, 12]) or (
                                    p_year == 2016 and p_month in [1]) or (
                                    p_year == 2018 and p_month in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])):
                        # 非熊市
                        continue

                    date_start = p_year + "-" + str(p_month) + "-01"
                    if p_month in [1, 3, 5, 7, 8, 10, 12]:
                        p_month_day_end = "31"
                    elif p_month in [4, 6, 9, 11]:
                        p_month_day_end = "30"
                    else:
                        localtime = time.mktime(time.strptime(p_year + "-03-01", "%Y-%m-%d")) - 1
                        p_month_day_end = time.strftime("%d", time.localtime(localtime))
                    date_end = p_year + "-" + str(p_month) + "-" + str(p_month_day_end)
                    # print(date_start, date_end)
                    time.sleep(1)
                    self.saveMonth(code, p_year, date_start, date_end, p_month)
                    p_month = p_month + 1
                p_year = str(int(p_year) + 1)

    def saveMonth(self, code, p_year, date_start, date_end, p_month):
        halfYearSharesStart = SharesIndustry.objects.filter(code_id=code,
                                                            date_as__gte=date_start,
                                                            date_as__lte=date_end
                                                            )
        if len(halfYearSharesStart) == 0:
            return

        halfYearSharesEnd = SharesIndustry.objects.filter(code_id=code,
                                                          date_as__lte=date_end
                                                          ).order_by('-date_as')[0]

        if SharesIndustryMonth.objects.filter(code_id=code, p_year=int(p_year), p_month=p_month).count():
            return

        halfYear = SharesIndustryMonth(code_id=code, p_start=halfYearSharesStart[0].p_start,
                                       p_end=halfYearSharesEnd.p_end, p_year=int(p_year),
                                       p_month=p_month)
        halfYear.save()
