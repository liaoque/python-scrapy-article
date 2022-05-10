import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_date import SharesDate
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '股票轮动'

    def handle(self, *args, **options):
        # 过去30个工作日， 涨停股票所属行业
        dates = self.getAllDates()[-30:]
        start = dates[0].date_as;
        end = dates[len(dates) - 1].date_as;
        self.wheel(start, end)

    def wheel(self, start, end):
        sql = """
                   select 1 as id, industry_code_id, industry_name, count(1) as c from (
                       select mc_shares.code_id, (p_end - p_start) / p_start as p_range2, industry_code_id, mc_shares_name.name as industry_name 
                           from mc_shares 
                           left join mc_shares_join_industry on mc_shares_join_industry.code_id = mc_shares.code_id
                           left join mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code
                           where date_as >= %s and date_as <= %s and p_start < p_end
                           having p_range2 >= 0.08
                   ) t
                   group by industry_code_id
                   order by c desc
               """
        result = Shares.objects.raw(sql, params=(start, end,))
        print("当前轮动", result)
        for item in result:
            """
            select 1 as id, count(1) as c from mc_shares 
            left join mc_shares_join_industry on mc_shares_join_industry.code_id = mc_shares.code_id
            where date_as >= %s and date_as <= %s  and  industry_code_id = %s
               """
            result2 = Shares.objects.raw(sql, params=(start, end, item.industry_code_id,))
            print(result2)
            print(item.industry_name, item.industry_code_id, item.c, result2[0].c, item.c / result2[0].c)

    def getAllDates(self):
        sql = '''
                select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01';
                '''
        return Shares.objects.raw(sql)
