import numpy as np
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db import connection

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares import Shares
from shares.model.shares_half_year import SharesHalfYear
import time


# import numpy as np
# import talib
# import sys

# 统计上班年和下班的 最高和最低


class Command(BaseCommand):
    help = '打印每半年，季度，月都的涨幅概率'

    def handle(self, *args, **options):
        self.half_year()
        self.season()

    def half_year(self):
        sql = """
                SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
        from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 and p_end > p_start GROUP BY code_id) t1
        LEFT JOIN 
            (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 1 GROUP BY code_id) t2 
        on t1.code_id = t2.code_id
        where t1.code_id not in (SELECT code from mc_shares_name where name like "%s"  )
        HAVING rang > 0.7 and rang < 1) c;
                """ % "ST%"
        print(sql)
        slist = SharesHalfYear.objects.raw(sql, params=())
        print(slist)
        print("上半年---start")
        print(",".join(["\"" + item + "\"" for item in slist]))
        print("上半年---end")
        sql = """
                        SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
                from (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 2 and p_end > p_start GROUP BY code_id) t1
                LEFT JOIN 
                    (SELECT COUNT(1) as c, code_id FROM `mc_shares_half_year` where  p_year_half = 2 GROUP BY code_id) t2 
                on t1.code_id = t2.code_id
                where t1.code_id not in (SELECT code from mc_shares_name where name like "%s" )
                HAVING rang > 0.7 and rang < 1) c;
                        """ % "ST%"
        print(sql)
        slist = SharesHalfYear.objects.raw(sql, params=())
        print(slist)
        print("\n下半年---start\n")
        print(",".join(["\"" + item + "\"" for item in slist]))
        print("下半年---end\n")

    def season(self):
        for season in [1, 2, 3, 4]:
            sql = """
                            SELECT code_id FROM (SELECT t1.code_id,  t1.c / t2.c as rang 
                    from (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = %s and p_end > p_start GROUP BY code_id) t1
                    LEFT JOIN 
                        (SELECT COUNT(1) as c, code_id FROM `mc_shares_season` where  p_season = %s GROUP BY code_id) t2 
                    on t1.code_id = t2.code_id
                    where t1.code_id not in (SELECT code from mc_shares_name where name like "%s"  )
                    HAVING rang > 0.7 and rang < 1) c;
                            """ % season, season, "ST%"
            print(sql)
            slist = SharesHalfYear.objects.raw(sql, params=())
            print("\n%s季度---start\n" % season)
            print(",".join(["\"" + item + "\"" for item in slist]))
            print("\n%s季度---end\n" % season)
