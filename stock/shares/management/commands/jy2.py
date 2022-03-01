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
# from ....shares.model.shares_kdj import SharesKdj
# from ....shares.model.shares import Shares
import numpy as np
import talib
import sys


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        dateList = self.getAllDates()
        self.seek(dateList)
        self.seek2(dateList)

    def seek(self, dateList):
        # 当天和前 10个工作日 dea 上行
        # dateList =dateList[:len(dateList)-3]
        slen1 = len(dateList)
        firstDay = dateList[slen1 - 1].date_as
        secondDay = dateList[slen1 - 2].date_as
        today = dateList[slen1 - 3].date_as
        yesterday = dateList[slen1 - 4].date_as
        daysBefore5 = dateList[slen1 - 7].date_as

        # today 放量且放量是前4日均值的2倍，且第二天结束价格没到 today的一半
        sql = '''
        SELECT 1 as id, max(t.buy_count) as max_c, (sum(t.buy_count) - max(t.buy_count))/4 as min_c, t.code_id,c.buy_count 
        FROM mc_shares t 
        LEFT JOIN (SELECT code_id,buy_count,p_start,p_end FROM `mc_shares` WHERE date_as =%s) f on f.code_id = t.code_id 
        LEFT JOIN (SELECT code_id,buy_count,p_start,p_end FROM `mc_shares` WHERE date_as =%s) s on s.code_id = t.code_id 
        LEFT JOIN (SELECT code_id,buy_count,p_start,p_end FROM `mc_shares` WHERE date_as =%s) c on c.code_id = t.code_id 
        LEFT JOIN (SELECT code_id,buy_count,p_start,p_end FROM `mc_shares` WHERE date_as =%s) d on d.code_id = t.code_id 
        where t.date_as >= %s 
        and t.date_as <= %s
        and f.p_end < f.p_start 
        and s.p_end < s.p_start 
        and c.p_end > c.p_start 
        and c.p_start + (c.p_end - c.p_start) / 2 <= f.p_end 
        and t.name not like %s
        and (t.code_id < 300000 or t.code_id > 600000)
        and t.code_id < 680000
        group by t.code_id 
        HAVING c.buy_count = max_c and c.buy_count / min_c > 2;
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(
            firstDay, secondDay, today, yesterday, daysBefore5, today, "ST%",))
        print(result)
        print("%s-%s-通过交易量挑选出股票：%s个" % (today, yesterday, len(result)))

        print(",".join(["\"" + item.code_id + "\"" for item in result]))

    def seek2(self, dateList):
        slen1 = len(dateList)
        today = dateList[slen1 - 1].date_as
        day5 = dateList[slen1 - 5].date_as
        day10 = dateList[slen1 - 10].date_as
        sql = '''
            SELECT t.code_id, max(t.p_end) as p_end
            FROM mc_shares t 
            LEFT JOIN (SELECT code_id,p_end FROM `mc_shares` WHERE date_as =%s) f on f.code_id = t.code_id 
            LEFT JOIN (SELECT code_id,min(p_end) as p_end FROM `mc_shares` WHERE date_as < %s and date_as > %s) m on m.code_id = t.code_id 
            where t.date_as >= %s 
            and t.name not like %s
            and (t.code_id < 300000 or t.code_id > 600000)
            and t.code_id < 680000
            and f.p_end < p_end
            and m.p_end < p_end
            and abs(f.p_end - m.p_end)  / f.p_end < 0.01
            group by t.code_id, t.date_as 
            '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, day5, day10,day5, "ST%",))
        print(result)
        print("%s-%s-5天的调整的股票：%s个" % (today, day5, len(result)))
        print(",".join(["\"" + item.code_id + "\"" for item in result]))

    def getAllDates(self):
        sql = '''
                select 1 as id, date_as from mc_shares_kdj where date_as >= '2021-12-01' group by date_as;
                '''
        return SharesKdjCompute.objects.raw(sql)
