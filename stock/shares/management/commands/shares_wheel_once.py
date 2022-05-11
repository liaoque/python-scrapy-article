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
        # BK1036
        datesOld = self.getAllDates()
        datesOld = datesOld[-350:]
        i = datesOld[0]
        all = []
        while i < 350:
            dates = datesOld[i:15]
            start = dates[0].date_as;
            end = dates[len(dates) - 1].date_as;
            result1 = self.convert(self.wheel(start, end, 'BK1036'))
            all.append(result1)
            for industry_code_id in ['BK1036']:
                item = result1[industry_code_id]
                print("%s %s %s %s 20涨停：%s " % (
                    start, end,
                    item["industry_code_id"], item["industry_name"], item["c"],
                ))
            i+15

    def wheel(self, start, end, code_id):
        sql = """
                   select 1 as id, industry_code_id, industry_name, count(1) as c from (
                       select mc_shares.code_id, (p_end - p_start) / p_start as p_range2, industry_code_id, mc_shares_name.name as industry_name 
                           from mc_shares 
                           left join mc_shares_join_industry on mc_shares_join_industry.code_id = mc_shares.code_id
                           left join mc_shares_name on mc_shares_join_industry.industry_code_id = mc_shares_name.code
                           where date_as >= %s and date_as <= %s and p_start < p_end and mc_shares.code_id = %s
                           having p_range2 >= 0.08
                   ) t
                   group by industry_code_id
                   order by c desc
               """
        result = Shares.objects.raw(sql, params=(start, end, code_id))
        return result

    def getAllDates(self):
        sql = '''
                select 1 as id, date_as from mc_shares_date where date_as >= '2021-01-01';
                '''
        return Shares.objects.raw(sql)

    def convert(self, list):
        result1 = {}
        for item in list:
            result1[item.industry_code_id] = {
                "industry_code_id": item.industry_code_id,
                "industry_name": item.industry_name,
                "c": item.c,
            }
        return result1
