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

" /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        # 查找所有股票
        slist = []
        for item in SharesName.objects.filter(status=1, code_type=1):
            if (item.code > '300000' and item.code < '600000') or item.code > '700000':
                continue
            # 查该股所有日期
            for sharesItem in Shares.objects.filter(code_id=item.code).order_by('-date_as')[:1]:
                result = self.macdTodaySearch(item.code, sharesItem.date_as)
                if result:
                    slist.append(item.code)
                    print("today-code：%s" % item.code)
                    break
                result = self.macdYestodaySearch(item.code, sharesItem.date_as)
                if result:
                    slist.append(item.code)
                    print("yestoday-code：%s" % item.code)
                    break
        print(",".join(["\"" + item + "\"" for item in slist]))


    def macdTodaySearch(self, code_id, today):
        # 当天和前 10个工作日 dea 上行
        sql = '''
        select  1 as id, mc_shares_macd.code_id from mc_shares_macd 
            left join (
                select MAX(dea) AS max_dea, code_id from (
                    select dea, code_id from mc_shares_macd where date_as < %s and code_id = %s order by date_as desc limit 10
                ) t) c
                on c.code_id = mc_shares_macd.code_id 
            where mc_shares_macd.date_as = %s and max_dea < mc_shares_macd.dea and mc_shares_macd.code_id = %s
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id, today, code_id,))
        if len(result) == 0:
            return False

        # 检查是否存在交点
        sql = '''
        SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
            left join (select k,d,j,code_id from mc_shares_kdj 
                    where date_as < %s and code_id =%s order by date_as desc limit 1) c 
            on c.code_id = a.code_id
        where c.k > c.j and c.d > c.j and a.k < a.j and a.d < a.j and a.j < 60
        and a.date_as = %s and a.code_id = %s
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id, today, code_id,))
        if len(result) == 0:
            return False
        return True

    def macdYestodaySearch(self, code_id, today):
        # 查前3个交易日
        sql = '''
                select  1 as id, date_as from mc_shares_macd  
                        where date_as <= %s and code_id = %s order by date_as desc limit 4 
                '''
        dateList = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(dateList) < 2:
            return False

        # 上一个交易日
        yesterday = dateList[1].date_as
        # macd：距离交叉 < 11%(dea-diff/dea+ diff) )
        sql = '''
                select  1 as id, a.code_id, (a.dea-a.diff)/(a.dea+ a.diff) as rate from mc_shares_macd a 
                    left join mc_shares_macd b on b.code_id = a.code_id and b.date_as = %s
                    where a.date_as = %s and a.code_id =  %s and a.dea > a.diff 
                    and a.diff >= b.diff
                    having ABS(rate) < 0.11
                '''
        result = SharesKdjCompute.objects.raw(sql, params=(yesterday, today, code_id,))
        print(result)
        if len(result) == 0:
            return False



        targetDateAs = None
        for item in dateList:
            # 检查是否存在交点
            sql = '''
                    SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
                        left join (select k,d,j,code_id from mc_shares_kdj 
                                where date_as < %s and code_id =%s order by date_as desc limit 1) c 
                        on c.code_id = a.code_id
                    where c.k > c.j and c.d > c.j and a.k < a.j and a.d < a.j and a.j < 35
                    and a.date_as = %s and a.code_id = %s
                    '''
            result = SharesKdjCompute.objects.raw(sql, params=(item.date_as, code_id, item.date_as, code_id,))
            if len(result) > 0:
                targetDateAs = item.date_as
                break

        if targetDateAs == None:
            return False
        return True
