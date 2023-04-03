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
from shares.model.shares_date import SharesDate
from django.db import connection

class Command(BaseCommand):
    help = '计算p_rate2'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        shareDate = SharesDate.objects.order_by('date_as')
        c = len(shareDate)
        for key in range(c):
            if key + 1 >= c:
                break
            start = shareDate[key].date_as
            end = shareDate[key+1].date_as
            self.updateSharesRange(start, end)
            self.updateIndustryRange(start, end)
            self.updateIndustryRange2(start)


    def updateSharesRange(self, start, end):
        sql = '''
        update mc_shares t2 
        left join (select * from mc_shares where date_as =  %s ) t1 
        on t1.code_id = t2.code_id 
        set t2.p_range = (t2.p_end - t1.p_end) / t1.p_end * 10000 
        where t2.date_as =  %s and t1.p_end > 0 and t2.p_end > 0 
        '''
        cursor = connection.cursor()
        return cursor.execute(sql, [start, end])

    def updateIndustryRange(self, start, end):
        sql = '''
        update mc_shares_industry t2 
        left join (select * from mc_shares_industry where date_as =  %s ) t1 
        on t1.code_id = t2.code_id 
        set t2.p_range = (t2.p_end - t1.p_end) / t1.p_end * 10000 
        where t2.date_as =  %s and t1.p_end > 0 and t2.p_end > 0 
        '''
        cursor = connection.cursor()
        print(sql)
        return cursor.execute(sql, [start, end])

    def updateIndustryRange2(self, start):
        sql = ''' 
        update mc_shares t2 
        left join mc_shares_join_industry t3 on t3.code_id =  t2.code_id 
        left join (select * from mc_shares_industry where date_as = %s ) t1 
        on t1.code_id = t3.industry_code_id 
        set t2.p_range_win =     
            CASE
             WHEN t2.p_range > t1.p_range THEN
                 1
             WHEN t2.p_range < t1.p_range THEN
                 -1
             ELSE 0 
            END
        where t2.date_as = %s 
        '''
        cursor = connection.cursor()
        return cursor.execute(sql, [start, start])