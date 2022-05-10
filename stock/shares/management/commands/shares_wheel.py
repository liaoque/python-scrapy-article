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
        datesOld = self.getAllDates()
        dates = datesOld[-20:]
        start = dates[0].date_as;
        end = dates[len(dates) - 1].date_as;
        result1 = self.convert(self.wheel(start, end))

        dates = datesOld[-40:-20]
        start1 = dates[0].date_as;
        end2 = dates[len(dates) - 1].date_as;
        result2 = self.convert(self.wheel(start1, end2))

        dates = datesOld[-60:-40]
        start3 = dates[0].date_as;
        end3 = dates[len(dates) - 1].date_as;
        result3 = self.convert(self.wheel(start3, end3))

        dates = datesOld[-60:-40]
        start4 = dates[0].date_as;
        end4 = dates[len(dates) - 1].date_as;
        result4 = self.convert(self.wheel(start4, end4))

        result = list(set(
            list(result1.keys()) + list(result2.keys()) + list(result3.keys())
            + list(result4.keys())
        ))

        print("当前轮动", result)
        for industry_code_id in result:
            if industry_code_id is None:
                continue
            if industry_code_id not in result1:
                industry_name = (result2[industry_code_id] and result2[industry_code_id].industry_name) or (
                        result3[industry_code_id] and result3[industry_code_id].industry_name)
                result1[industry_code_id] = {
                    "industry_code_id": industry_code_id,
                    "industry_name": industry_name,
                    "c": 0,
                }
            if industry_code_id not in result2:
                result2[industry_code_id] = {
                    "industry_code_id": industry_code_id,
                    "industry_name": result1[industry_code_id]["industry_name"],
                    "c": 0,
                }

            if industry_code_id not in result3:
                result3[industry_code_id] = {
                    "industry_code_id": industry_code_id,
                    "industry_name": result1[industry_code_id]["industry_name"],
                    "c": 0,
                }

            if industry_code_id not in result4:
                result4[industry_code_id] = {
                    "industry_code_id": industry_code_id,
                    "industry_name": result1[industry_code_id]["industry_name"],
                    "c": 0,
                }

            item = result1[industry_code_id]
            all = (result4[industry_code_id]["c"] + result3[industry_code_id]["c"] +
                   result2[industry_code_id]["c"] + item["c"])
            print("%s 20涨停：%s 比例：%s --- 40涨停：%s 比例：%s --- 60涨停：%s 比例：%s --- 80涨停：%s 比例：%s " % (
                item["industry_name"], item["c"],
                round((item["c"] or 1) / all, 2),
                result2[industry_code_id]["c"],
                round((result2[industry_code_id]["c"] or 1) / all, 2),
                result3[industry_code_id]["c"],
                round((result3[industry_code_id]["c"] or 1) / all, 2),
                result4[industry_code_id]["c"],
                round((result4[industry_code_id]["c"] or 1) / all, 2),
            ))

            # sql = """
            #         select 1 as id, count(1) as c from mc_shares
            #         left join mc_shares_join_industry on mc_shares_join_industry.code_id = mc_shares.code_id
            #         where date_as >= %s and date_as <= %s  and  industry_code_id = %s
            #            """
            # result2 = Shares.objects.raw(sql, params=(start, end, item.industry_code_id,))
            # item.sc = result2[0].c
            # print(item.industry_name, item.industry_code_id, item.c, result2[0].c, item.c / result2[0].c)

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
        return result

    def getAllDates(self):
        sql = '''
                select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01';
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
