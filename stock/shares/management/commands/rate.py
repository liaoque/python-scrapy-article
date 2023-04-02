import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_macd import SharesMacd
from shares.model.shares import Shares
from shares.model.shares_kdj_compute import SharesKdjCompute
from shares.model.shares_kdj_compute_detail import SharesKdjComputeDetail
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_join_industry import SharesJoinIndustry

import numpy as np
import talib
import sys


class Command(BaseCommand):
    help = '计算p_rate'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        codeList = SharesName.objects.filter(code_type=2, status=1).all()
        for item in codeList:
            sharesItem5 = SharesIndustry.objects.filter(code_id=item.code).order_by('date_as')
            sharesItem5 = sharesItem5[-60:]
            c = len(sharesItem5)
            for key in range(c):
                if key + 1 >= c:
                    break
                item = sharesItem5[key]
                sharesItem5[key + 1].p_range = (sharesItem5[key + 1].p_end - item.p_end) / item.p_end * 10000
                sharesItem5[key + 1].save()

        codeList = SharesName.objects.filter(code_type=1, status=1).all()
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('date_as')
            sharesItem5 = sharesItem5[-60:]
            c = len(sharesItem5)
            for key in range(c):
                if key + 1 >= c:
                    break
                item = sharesItem5[key]
                sharesItem5[key + 1].p_range = (sharesItem5[key + 1].p_end - item.p_end) / item.p_end * 10000
                sharesItem5[key + 1].save()

        codeList = SharesName.objects.filter(code_type=1, status=1).all()
        for item in codeList:
            sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('date_as')
            sharesItem5 = sharesItem5[-60:]
            c = len(sharesItem5)
            for key in range(c):
                if key + 1 >= c:
                    break
                item = sharesItem5[key]
                sharesItem5[key + 1].p_range = (sharesItem5[key + 1].p_end - item.p_end) / item.p_end * 10000

                # 对应行业指数，跑赢行业指数 1， 否额-1
                sharesItem5[key + 1].p_range_win = 1
                p_range = self.getIndustry(item.code)
                if p_range > sharesItem5[key + 1].p_range:
                    sharesItem5[key + 1].p_range_win = -1
                sharesItem5[key + 1].save()


    def getIndustry(self, code):
        shares = SharesJoinIndustry.objects.filter(code_id=code)
        if len(shares) > 0:
            sharesItem5 = SharesIndustry.objects.filter(code_id=shares[0].industry_code_id).order_by('-date_as')
            return sharesItem5[0].p_range
        return 0;