import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_half_year import SharesHalfYear
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '统计上班年和下班的 最高和最低'

    def handle(self, *args, **options):
        for item in SharesName.objects.filter(status=1, code_type=1):
            code = item.code
            sharesItem = Shares.objects.filter(code_id=code).order_by('date_as')[0]
            sharesItemEnd = Shares.objects.filter(code_id=code).order_by('-date_as')[0]
            p_year = sharesItem.date_as.strftime('%Y')
            p_year_end = sharesItemEnd.date_as.strftime('%Y')
            print(p_year_end)

            while p_year <= p_year_end:
                date_start = p_year + "-01-01"
                date_end = p_year + "-06-30"
                self.saveHalfYear(code, p_year, date_start, date_end, 1)

                date_start = p_year + "-07-01"
                date_end = p_year + "-12-31"
                self.saveHalfYear(code, p_year, date_start, date_end, 2)

                p_year = str(int(p_year) + 1)

    def saveHalfYear(self, code, p_year, date_start, date_end, p_year_half):
        halfYearSharesStart = Shares.objects.filter(code_id=code,
                                                    date_as__gte=date_start,
                                                    date_as__lte=date_end
                                                    )
        if len(halfYearSharesStart) == 0:
            return

        halfYearSharesEnd = Shares.objects.filter(code_id=code,
                                                  date_as__lte=date_end
                                                  ).order_by('-date_as')[0]

        # if SharesHalfYear.objects.filter(code_id=code, p_year=int(p_year), p_year_half=p_year_half).count():
        #     return

        halfYear = SharesHalfYear(code_id=code, p_start=halfYearSharesStart[0].p_end,
                                  p_end=halfYearSharesEnd.p_end, p_year=int(p_year),
                                  p_year_half=p_year_half)
        halfYear.save()
