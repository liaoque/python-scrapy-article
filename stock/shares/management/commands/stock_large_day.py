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
from shares.model.shares_month import SharesMonth

# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = ' 查股票放量'

    def handle(self, *args, **options):
        codeList = self.getCodeList()
        codeLargeList = {
            "date":[],
            "month":[],
        }
        for item in codeList:
            # sharesItem5 = Shares.objects.filter(code_id=item.code).order_by('-date_as')[:5]
            # endCount = sharesItem5[0].buy_count
            # count4 = sum([ item.buy_count for item in sharesItem5[1:]]) / 4
            # if endCount / count4 > 1.8:
            #     codeLargeList["date"].append(item.code)

            sharesItem6 = SharesMonth.objects.filter(code_id=item.code).order_by('-p_year').order_by('-p_month')[:2]
            print(sharesItem6)
            if sharesItem6[0].buy_count / sharesItem6[1].buy_count > 2:
                codeLargeList["month"].append(item.code)
            # print(item.code, endCount.buy_count, count4)
            # break
        print(codeLargeList)

    # 基本面向好的公司
    def getCodeList(self):

        # 找公司 行业成长性，或者收入成长 比较靠谱的公司
        sql = """
        SELECT n.code ,n.gpm,t.gpm as tgpm FROM (SELECT * FROM `mc_shares_name` where code_type =  1 and (gpm_ex > 4000 or npmos_ex > 4000))  n
left join mc_shares_join_industry as i on n.code = i.code_id
left JOIN (SELECT * FROM `mc_shares_name` where code_type =  2 and gpm_ex > 1500) t on t.code = i.industry_code_id
where ( n.gpm_ex > t.gpm_ex or  n.npmos_ex > t.npmos_ex)  and n.name not like %s  and n.npmos > 0 and n.member_up =1 
        and t.gpm != 0
        """
        codeList = SharesName.objects.raw(sql, params=('%ST%',))
        # codeList = [item for item in codeList]
        #  公司毛利率不能低于行业毛利率的 30%
        return list(filter(lambda n: (n.gpm >= n.tgpm or (n.gpm / n.tgpm > 0.3)), codeList))

