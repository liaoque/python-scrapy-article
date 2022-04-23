import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
from shares.model.shares import Shares
from shares.model.shares_kdj_listen import SharesKdjListen
import numpy as np
import talib


class Command(BaseCommand):
    help = '记录每天10以下的kdj股票'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("开始计算-----")
        dateList = self.getAllDates()
        for item in dateList[-15:]:
            self.getkdj10(item.date_as)



    def getkdj10(self, date):
        sql = '''
            select 1 as id, code_id from mc_shares_kdj 
            where date_as = %s  
               and code_id not in ( select code_id from mc_shares_kdj_listen )
               and j < -10
            ;
            '''

        result = SharesKdj.objects.raw(sql, params=(date,))
        print("%s-挑选出-10的股票：%s个" % (date, len(result)))
        print(",".join(["\"" + item.code_id + "\"" for item in result]))
        for item in result:
            listen = SharesKdjListen(
                code_id=item.code_id,
                p_start=item.p_end,
                date_as=item.date_as,
                type=1,
            )
            listen.save()

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_date where date_as >= '2021-12-01' ;
            '''
        return SharesKdjListen.objects.raw(sql)
