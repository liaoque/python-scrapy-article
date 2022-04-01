import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count,Max,Min

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_season import SharesSeason
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '统计4季度 最高和最低'

    def handle(self, *args, **options):
        income = 0
        for item in SharesName.objects.filter(status=1, code_type=1):
            code = item.code
            sharesItem = Shares.objects.filter(code_id=code).order_by('date_as')[0]
            sharesItemEnd = Shares.objects.filter(code_id=code).order_by('-date_as')[0]
            p_year = sharesItem.date_as.strftime('%Y')
            p_year_end = sharesItemEnd.date_as.strftime('%Y')
            print(p_year_end)

            while p_year <= p_year_end:
                date_start = p_year + "-01-01"
                date_end = p_year + "-03-31"
                self.saveHalfYear(code, p_year, date_start, date_end, 1)

                date_start = p_year + "-04-01"
                date_end = p_year + "-06-30"
                self.saveHalfYear(code, p_year, date_start, date_end, 2)

                date_start = p_year + "-07-01"
                date_end = p_year + "-09-30"
                self.saveHalfYear(code, p_year, date_start, date_end, 3)

                date_start = p_year + "-10-01"
                date_end = p_year + "-12-31"
                self.saveHalfYear(code, p_year, date_start, date_end, 4)

                p_year = str(int(p_year) + 1)

    def saveHalfYear(self, code, p_year, date_start, date_end, p_season):
        halfYearSharesStart = Shares.objects.filter(code_id=code,
                                                    date_as__gte=date_start
                                                    )
        if len(halfYearSharesStart) == 0:
            return

        halfYearSharesEnd = Shares.objects.filter(code_id=code,
                                                  date_as__lte=date_end
                                                  ).order_by('-date_as')[0]

        # if SharesSeason.objects.filter(code_id=code, p_year=int(p_year), p_season=p_season).count():
        #     return

        halfYear = SharesSeason(code_id=code, p_start=halfYearSharesStart[0].p_end,
                                  p_end=halfYearSharesEnd.p_end, p_year=int(p_year),
                                  p_season=p_season)
        halfYear.save()