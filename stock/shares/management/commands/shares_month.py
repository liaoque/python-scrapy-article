import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_month import SharesMonth
from django.db.models import Avg, Count,Sum
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '统计每月的 最高和最低'

    def handle(self, *args, **options):
        # for item in SharesName.objects.filter(status=1, code_type=1, code__gte='000702'):
        for item in SharesName.objects.filter(status=1, code_type=1):
            code = item.code
            sharesItem = Shares.objects.filter(code_id=code).order_by('date_as')[0]
            sharesItemEnd = Shares.objects.filter(code_id=code).order_by('-date_as')[0]
            p_year = sharesItem.date_as.strftime('%Y')
            p_year_end = sharesItemEnd.date_as.strftime('%Y')
            # print(p_year_end)
            # print(connection.queries)
            # break

            while p_year <= p_year_end:
                p_month = 1
                while p_month <= 12:
                    date_start = p_year + "-" + str(p_month) + "-01"
                    if p_month in [1, 3, 5, 7, 8, 10, 12]:
                        p_month_day_end = "31"
                    elif p_month in [4, 6, 9, 11]:
                        p_month_day_end = "30"
                    else:
                        localtime = time.mktime(time.strptime(p_year + "-03-01", "%Y-%m-%d"))  - 1
                        p_month_day_end = time.strftime("%d", time.localtime(localtime))
                    date_end = p_year + "-" + str(p_month) + "-" + str(p_month_day_end)
                    # print(date_start, date_end)
                    # time.sleep(1)
                    self.saveMonth(code, p_year, date_start, date_end, p_month)
                    p_month = p_month + 1
                p_year = str(int(p_year) + 1)

    def saveMonth(self, code, p_year, date_start, date_end, p_month):
        if SharesMonth.objects.filter(code_id=code, p_year=int(p_year), p_month=p_month).count():
            return

        halfYearSharesStart = Shares.objects.filter(code_id=code,
                                                    date_as__gte=date_start,
                                                    date_as__lte=date_end
                                                    ).order_by('date_as')
        if len(halfYearSharesStart) == 0:
            return

        halfYearSharesEnd = Shares.objects.filter(code_id=code,
                                                  date_as__lte=date_end
                                                  ).order_by('-date_as')[0]

        buy_count = Shares.objects.filter(code_id=code,
                                                    date_as__gte=date_start,
                                                    date_as__lte=date_end
                                                    ).aggregate(buy_count2=Sum('buy_count'))
        # print(buy_count)
        buy_sum = Shares.objects.filter(code_id=code,
                                          date_as__gte=date_start,
                                          date_as__lte=date_end
                                          ).aggregate(buy_sum2=Sum('buy_sum'))
        # print(buy_sum)
        halfYear = SharesMonth(code_id=code, p_start=halfYearSharesStart[0].p_start,
                               p_end=halfYearSharesEnd.p_end, p_year=int(p_year),
                               buy_count=int(buy_count["buy_count"]/10000),buy_sum=int(buy_sum["buy_sum"]/10000),
                               p_month=p_month)
        halfYear.save()
