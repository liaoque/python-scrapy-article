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

        five_start = shareDate[:5][4].date_as

        twenty_start = shareDate[:20][19].date_as

        sixty_start = shareDate[:60][59].date_as

        one_hundred_start = shareDate[:120][119].date_as

        for item in SharesName.objects.filter(status=1, code_type=1, ):
            five_day = Shares.objects.filter(date_as__gte=five_start).aggregate(Min('p_end'))

            twenty_day = Shares.objects.filter(date_as__gte=twenty_start).aggregate(Min('p_end'))

            sixty_day = Shares.objects.filter(date_as__gte=sixty_start).aggregate(Min('p_end'))

            one_hundred_day = Shares.objects.filter(date_as__gte=one_hundred_start).aggregate(Min('p_end'))


            SharesName.objects.filter(code=item.code).update(
                five_day=five_day["p_end__min"],
                twenty_day=twenty_day["p_end__min"],
                sixty_day=sixty_day["p_end__min"],
                one_hundred_day=one_hundred_day["p_end__min"],
            )
            break
            pass
