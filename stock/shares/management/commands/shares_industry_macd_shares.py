from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_industry import SharesIndustry
from shares.model.shares_join_industry import SharesJoinIndustry
import time
import pandas as pd
import numpy as np
import talib


# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '找板块周期回调比较小的股票'

    def handle(self, *args, **options):
        start = date.today() - timedelta(days=60)
        end = date.today()
        for code in ['BK0425', 'BK0437', 'BK0451', 'BK0482', 'BK0726']:
            result = self.listCode(code, start, end)
            for code_id in result[code]:
                print(code_id, result[code][code_id])
            print("----------")

    def listCode(self, code, start, end):
        l = {}
        sql = """
                    select * from `mc_shares_industry` 
                    where code_id=%s 
                        and date_as >= %s 
                        and date_as <= %s
                        and p_end < p_start
                    """
        SharesIndustryDates = SharesIndustry.objects.raw(sql, params=(code, start, end))
        shares = SharesJoinIndustry.objects.filter(industry_code_id=code)
        if code not in l:
            l[code] = {}
        l[code][code] = len(SharesIndustryDates)
        for shareItem in shares:
            sql = """
                    select * from `mc_shares_industry` 
                    where code_id=%s 
                        and date_as >= %s 
                        and date_as <= %s
                    """
            sharesDates = SharesIndustry.objects.raw(sql, params=(shareItem.code_id, start, end))
            for SharesIndustryDateItem in SharesIndustryDates:
                for sharesDateItem in sharesDates:
                    if sharesDateItem.code_id not in l[code]:
                        l[code][sharesDateItem.code_id] = 0
                    if SharesIndustryDateItem.date_as != sharesDateItem.date_as:
                        continue
                    # 对比回撤幅度
                    # 板块下跌，股票上涨
                    # 板块下跌，股票跌幅 小于
                    if (sharesDateItem.p_start <= sharesDateItem.p_end) or (
                            (sharesDateItem.p_start - sharesDateItem.p_end) / sharesDateItem.p_end <= (
                            SharesIndustryDateItem.p_start - SharesIndustryDateItem.p_end) / SharesIndustryDateItem.p_end
                    ):
                        l[code][sharesDateItem.code_id] += 1
                    break
        print(l)
        return l
