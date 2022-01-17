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
        for item in SharesName.objects.filter(status=1, code_type=1):
            # 查该股所有日期
            print(item.code)
            for sharesItem in Shares.objects.filter(code_id=item.code)[:1]:
                print(sharesItem.date_as)
                break
                result = self.macdTodaySearch(item.code, sharesItem.date_as)
                if result:
                    print("today-code：%s" % item.code)
                    break
                result = self.macdYestodaySearch(item.code, sharesItem.date_as)
                if result:
                    print("yestoday-code：%s" % item.code)
                    break

    def macdTodaySearch(self, code_id, today):
        # 当天和前 10个工作日 dea 上行
        sql = '''
        select  1 as id, mc_shares_macd.code_id from mc_shares_macd 
            left join (select max(dea) as max_dea, code_id from mc_shares_macd
                        where date_as < %s and code_id = %s order by date_as desc limit 10) c
                on c.code_id = mc_shares_macd.code_id 
            where date_as = %s and max_dea < dea and code_id = %s
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id, today, code_id,))
        if len(result) == 0:
            return False

        # 检查是否存在交点
        sql = '''
        SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
            left join (select k,d,j,code_id from mc_shares 
                    where date_as < %s and code_id =%s order by date_as desc limit 1) c 
            on c.code_id = a.code_id
        where c.k > c.j and c.d > c.j and a.k < a.j and a.d < a.j 
        and a.date_as = %s and a.code_id = %s
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id, today, code_id,))
        if len(result) == 0:
            return False

        print("%s获得股票：%s" % (today, code_id))
        return True

    def macdYestodaySearch(self, code_id, today):
        # macd：距离交叉 < 11%(dea-diff/dea+ diff) )
        sql = '''
                select  1 as id, mc_shares_macd.code_id, (dea-diff)/(dea+ dif) as rate from mc_shares_macd 
                    where date_as = %s and code_id <  %s 
                    having rate < 0.11
                '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(result) == 0:
            return False

        # 查前3个交易日
        sql = '''
        select  1 as id, date_as from mc_shares_macd  
                where date_as = %s and code_id < %s order by date_as desc limit 3 
        '''
        dateList = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(dateList) == 0:
            return False

        targetDateAs = None
        for item in dateList:
            # 检查是否存在交点
            sql = '''
                    SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
                        left join (select k,d,j,code_id from mc_shares 
                                where date_as < %s and code_id =%s order by date_as desc limit 1) c 
                        on c.code_id = a.code_id
                    where c.k > c.j and c.d > c.j and a.k < a.j and a.d < a.j
                    and a.date_as = %s and a.code_id = %s
                    '''
            result = SharesKdjCompute.objects.raw(sql, params=(item.date_as, code_id, item.date_as, code_id,))
            if len(result) > 0:
                targetDateAs = item.date_as
                break

        if targetDateAs == None:
            return False
        print("%s获得股票：%s" % (today, code_id))
        return True

    def sell(self, code_id, today):
        # 以最高点之后的，转折点作为卖价
        sql = '''
            select p_end from mc_shares  where date_as = %s and code_id =  %s 
            '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(result) == 0:
            return False
        start_p = result[0].p_end

        # 往后10个工作日
        sql = '''
        select date_as from mc_shares  where date_as > %s and code_id =  %s order by date_as asc limit 10
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(result) == 0:
            return False

        for key in range(len(result)):
            today = result[key].date_as
            if key + 1 > len(result):
                break
            tomorrow = result[key + 1].date_as
            # j 下行
            sql = '''
                        SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
                            left join (select k,d,j,code_id from mc_shares 
                                    where date_as = %s and code_id =%s order by date_as asc limit 1) c 
                            on c.code_id = a.code_id
                        where c.j < a.j
                        and a.date_as = %s and a.code_id = %s
                        '''
            result = SharesKdjCompute.objects.raw(sql, params=(tomorrow, code_id, today, code_id,))
            if len(result) == 0:
                continue
            sql = '''select p_end from mc_shares  where date_as = %s and code_id =  %s '''
            result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
            end_p = result[0].p_end
            diff = start_p - end_p
            return diff, today
        return False
