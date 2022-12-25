from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_industry_week import SharesIndustryWeek
import time
import pandas as pd
import numpy as np
import talib


# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '看周线周期趋势'

    def handle(self, *args, **options):
        for item2 in SharesName.objects.filter(status=1, code_type=2, ):
            code = item2.code
            sql = '''
            SELECT 1 as id, code_id,MIN(p_min) as p_min ,max(p_max) as p_max,MIN(p_start) as p_start,MAX(p_end) as p_end,MIN(date_as) as date_as,max(date_as) as date_as_end, date_week
FROM (SELECT code_id,p_min, p_max,p_start, p_end,date_as, YEAR(date_as) as date_year, week(date_as, 1) as date_week FROM `mc_shares_industry` where code_id = %s
ORDER BY `mc_shares_industry`.`date_as`  ASC) t GROUP by date_year, date_week;
            '''
            for item in SharesIndustryWeek.objects.raw(sql, params=(code,)):
                break
                sharesKdjList = SharesIndustryWeek.objects.filter(code_id=code, date_as=item.date_as)
                if len(sharesKdjList):
                    continue

                b = SharesIndustryWeek(code_id=code,
                                       p_min=item.p_min,
                                       p_max=item.p_max,
                                       p_start=item.p_start,
                                       p_end=item.p_end,
                                       date_as=item.date_as,
                                       date_as_end=item.date_as_end,
                                       date_week=item.date_week,
                )
                b.save()

            sharesList = SharesIndustryWeek.objects.filter(code_id=code).order_by('-date_as')
            self.pRate(sharesList, item2)


            sharesListSource = SharesIndustryWeek.objects.filter(code_id=code).order_by('date_as')
            i = 0
            between = 0
            up = True
            sharesListSource = np.array(sharesListSource)
            self.defMaxMin(sharesListSource, i + 1, up, between)


    def pRate(self, sharesList, item):
        if len(sharesList) == 0:
            return
        sharesList = np.array(sharesList)

        i = 0;
        # c = len(sharesList)
        c = 2
        while i < c:
            # 按比例归一
            sharesIndustry = sharesList[i]
            if sharesIndustry.avg_p_min_rate != 0:
                i = i + 1
                continue
            sharesIndustry.avg_p_min_rate = sharesIndustry.p_min / item.four_year_day
            sharesIndustry.avg_p_max_rate = sharesIndustry.p_max / item.four_year_day

            sharesIndustry.save()
            i = i + 1


    def defMaxMin(self, sharesListSource, i, up, between):
        if len(sharesListSource) < 5:
            return
        sharesList = sharesListSource[i * 5:5 + i * 5]
        if len(sharesList) < 5:
            return
        lastIndex = len(sharesList) - 1
        print(sharesList)
        if up:
            p_start = min(sharesList[0].p_end, sharesList[0].p_start)
            if p_start > sharesList[lastIndex].p_end:
                # 趋势反转， 到了压力位
                between = maxIndustryIndex = self.max(sharesListSource, between, 5 + i * 5)
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
                between = minIndustryIndex = self.min(sharesListSource, between, 5 + i * 5)
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





