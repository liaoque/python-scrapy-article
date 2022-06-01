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


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '计算公司最低均价'

    def handle(self, *args, **options):
        shareDate = SharesDate.objects.order_by('-date_as')

        five_start = shareDate[:5][4]

        twenty_start = shareDate[:20][19]

        sixty_start = shareDate[:60][59]

        one_hundred_start = shareDate[:120][119]

        for item in SharesName.objects.filter(status=1, code_type=1, ):
            print(five_start)
            five_day = Shares.objects.filter(date_as__gte=five_start).aggregate(Min('p_end'))

            twenty_day = Shares.objects.filter(date_as__gte=twenty_start).aggregate(Min('p_end'))

            sixty_day = Shares.objects.filter(date_as__gte=sixty_start).aggregate(Min('p_end'))

            one_hundred_day = Shares.objects.filter(date_as__gte=one_hundred_start).aggregate(Min('p_end'))
            item.update(
                five_day=five_day,
                twenty_day=twenty_day,
                sixty_day=sixty_day,
                one_hundred_day=one_hundred_day,
            )
            break
            pass
