import numpy as np
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_hours import SharesHours
from shares.model.shares_date_listen import SharesDateListen
from shares.model.shares_macd import SharesMacd
from shares.model.shares_industry_kdj import SharesIndustryKdj
from shares.model.shares_industry_macd import SharesIndustryMacd
from shares.model.shares_join_industry import SharesJoinIndustry
from shares.model.shares_buys import SharesBuys
from shares.model.shares_date import SharesDate
import numpy as np
import talib
import math
import sys
from shares.model.shares_industry import SharesIndustry


# 校验的
# 1. 检测当天板块 macd是否上升
# 2. 板块回踩10日均线
# 3. 寻找，该板块的股票下，回踩均线的股票


class Command(BaseCommand):
    help = '记录每天-10以下的kdj股票'

    codeList = []
    dateList = []
    five_start = ''
    twenty_start = ''
    sixty_start = ''
    one_hundred_start = ''
    four_year_start = ''

    date_as = None

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        for item in SharesName.objects.filter(status=1, code_type=2):
            code = item.code
            sharesListSource = SharesIndustry.objects.filter(code_id=code).order_by('date_as')
            i = 0
            between = 0
            up = True
            sharesListSource = np.array(sharesListSource)
            self.defMaxMin(sharesListSource, i + 1, up, between)

    def defMaxMin(self, sharesListSource, i, up, between):
        sharesList = sharesListSource[i * 10:10 + i * 10]
        if len(sharesList) < 10:
            return
        lastIndex = len(sharesList) - 1
        print(sharesList)
        if up:
            p_start = min(sharesList[0].p_end, sharesList[0].p_start)
            if p_start > sharesList[lastIndex].p_end:
                # 趋势反转， 到了压力位
                between = maxIndustryIndex = self.max(sharesListSource, between, 10 + i * 10)
                maxIndustry = sharesListSource[maxIndustryIndex]
                maxIndustry.max_min_flag = -1
                maxIndustry.save()
                # sMaxIndustry = None
                up = False
            self.defMaxMin(sharesListSource, i + 1, up, between)
        else:
            p_start = max(sharesList[0].p_end, sharesList[0].p_start)
            if p_start < sharesList[lastIndex].p_end:
                # 趋势反转， 到了支撑位
                between = minIndustryIndex = self.min(sharesListSource, between, 10 + i * 10)
                minIndustry = sharesListSource[minIndustryIndex]
                minIndustry.max_min_flag = 1
                minIndustry.save()
                # sMaxIndustry = None
                up = True
            self.defMaxMin(sharesListSource, i + 1, up, between)

    def max(self, sharesList, start, end):
        c = end
        max2 = start
        i = start
        while i < c:
            if sharesList[max2].p_end < sharesList[i].p_end:
                max2 = i
            i = i + 1
        return max2

    def min(self, sharesList, start, end):
        # sharesList = sharesList[start:end]
        c = end
        min2 = start
        i = start
        while i < c:
            if sharesList[min2].p_end > sharesList[i].p_end:
                min2 = i
            i = i + 1
        return min2
