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
        for item in SharesName.objects.filter(status=1, code_type=2, ):
            code = item.code
            sql = '''
            SELECT 1 as id, code_id,MIN(p_min) as p_min ,max(p_max) as p_max,MIN(p_start) as p_start,MAX(p_end) as p_end,MIN(date_as) as date_as,max(date_as) as date_as_end, date_week
FROM (SELECT code_id,p_min, p_max,p_start, p_end,date_as, YEAR(date_as) as date_year, week(date_as, 1) as date_week FROM `mc_shares_industry` where code_id = %s
ORDER BY `mc_shares_industry`.`date_as`  ASC) t GROUP by date_year, date_week;
            '''
            for item in SharesIndustryWeek.objects.raw(sql, params=(code,)):

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












