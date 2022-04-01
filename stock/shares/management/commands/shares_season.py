import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '统计上班年和下班的 最高和最低'

    def handle(self, *args, **options):
        income = 0
        for item in SharesName.objects.filter(status=1, code_type=1):
            code = item.code
            sharesItem = Shares.objects.filter(code_id=code).order_by('date_as')[0]
            sharesItemEnd = Shares.objects.filter(code_id=code).order_by('-date_as')[0]
            p_year = sharesItem['date_as'].strftime('%Y')
            p_year_end = sharesItemEnd['date_as'].strftime('%Y')
            print(p_year_end)


            while p_year <= p_year_end:
                date_start = p_year + "-01-01"
                date_end = p_year + "-03-31"
                for item in Shares.objects.filter(code_id=code,
                                                  date_as__gte=date_start,
                                                  date_as__lte=date_end
                                                  ).select_related('min(p_start),min(p_end)'):
                    print(item)

                # sql = '''
                #     select min() from mc_shares_kdj where date_as >= '2021-12-01' group by date_as;
                #     '''
                # return SharesKdjCompute.objects.raw(sql)

