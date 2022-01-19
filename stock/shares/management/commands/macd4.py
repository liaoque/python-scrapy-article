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

" /bin/cp /alidata/python/python-scrapy-article/stock/* /alidata/python/python-scrapy-article-master/stock -rf"


class Command(BaseCommand):
    help = '计算各种指标'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        # 查找所有股票
        bill = 0
        negative = 0
        for item in SharesName.objects.filter(status=1, code_type=1):
            if (item.code > '300000' and item.code < '600000') or item.code > '680000':
                continue
            # 查该股所有日期
            diffTotal = 0
            end_date = None
            total, success, error = 0, 0, 0
            skip = 0
            for sharesItem in Shares.objects.filter(code_id=item.code, date_as__gte='2021-12-01'):
                if end_date and sharesItem.date_as <= end_date:
                    continue
                result = self.macdTodaySearch(item.code, sharesItem.date_as)
                if result:
                    # 计算收益
                    print("%s买入%s" % (sharesItem.date_as, item.code))
                    diff, end_date = self.sell(item.code, sharesItem.date_as)
                    if diff == False:
                        continue
                    print("%s卖出%s" % (end_date, item.code))
                    total += 1
                    diffTotal += diff
                    if diff > 0:
                        success += 1
                    else:
                        error += 1
                    continue

                if skip > 0:
                    # yesterday 卖出后，跳过3个工作日
                    skip -= 1
                    continue

                result = self.macdYestodaySearch(item.code, sharesItem.date_as)
                if result:
                    # 计算收益
                    print("yesterday %s买入%s" % (sharesItem.date_as, item.code))
                    diff, end_date = self.sell(item.code, sharesItem.date_as)
                    if diff == False:
                        continue
                    print("yesterday %s卖出%s" % (end_date, item.code))
                    skip = 2
                    total += 1
                    if diff > 0:
                        success += 1
                    else:
                        error += 1
                    diffTotal += diff
                    continue
            print("code：%s， 总收益：%d， 成功： %d，失败：%d" % (item.code, diffTotal, success, error))
            sys.stdout.flush()
            if diffTotal > 0:
                bill += diffTotal
            elif diffTotal < 0:
                negative += diffTotal
        print("正收益： %d, 负收益：%d" % (bill, negative))

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
        where c.k > c.j and c.d > c.j and a.k < a.j and a.d < a.j and a.j < 35
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
                        where date_as < %s and code_id = %s order by date_as desc limit 3 
                '''
        dateList = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(dateList) < 2:
            return False

        # 上一个交易日
        yesterday = dateList[0].date_as
        # macd：距离交叉 < 11%(dea-diff/dea+ diff) )
        sql = '''
                select  1 as id, a.code_id, (a.dea-a.diff)/(a.dea+ a.diff) as rate from mc_shares_macd a 
                    left join mc_shares_macd b on b.code_id = a.code_id and b.date_as = %s
                    left join mc_shares_kdj x on x.code_id = a.code_id and x.date_as = a.date_as
                    where a.date_as = %s and a.code_id =  %s and a.dea > a.diff 
                    and a.diff >= b.diff and x.j < 60
                    having ABS(rate) < 0.11
                '''
        result = SharesKdjCompute.objects.raw(sql, params=(yesterday, today, code_id,))
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

    def sell(self, code_id, today):
        # 以最高点之后的，转折点作为卖价
        sql = '''
            select 1 as id,p_end from mc_shares  where date_as = %s and code_id =  %s 
            '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        if len(result) == 0:
            return False, False
        start_p = result[0].p_end

        # 往后10个工作日
        sql = '''
        select 1 as id,date_as from mc_shares  where date_as > %s and code_id =  %s order by date_as asc limit 11
        '''
        result = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
        dateLen = len(result)
        if dateLen == 0:
            return False, False

        for key in range(dateLen):
            today = result[key].date_as
            if key + 1 >= dateLen:
                break

            if key > 2:
                sql = '''
                        select  1 as id, a.code_id, (a.dea-a.diff)/(a.dea+ a.diff) as rate, (a.dea-a.diff) as sub1 
                            from mc_shares_macd a 
                            where a.date_as = %s and a.code_id =  %s and a.dea > a.diff 
                            having ABS(rate) < 0.11 or  abs(sub1) < 0.08
                        '''
                result2 = SharesKdjCompute.objects.raw(sql, params=(today, code_id,))
                if len(result2) > 0:
                    sql = '''select 1 as id,p_end from mc_shares  where date_as = %s and code_id =  %s '''
                    result2 = SharesKdjCompute.objects.raw(sql, params=(tomorrow, code_id,))
                    end_p = result2[0].p_end
                    diff = end_p - start_p
                    return diff, today

            tomorrow = result[key + 1].date_as
            # j 下行
            sql = '''
                    SELECT 1 as id, a.code_id FROM `mc_shares_kdj` a
                        left join (select k,d,j,code_id from mc_shares_kdj 
                                where date_as = %s and code_id =%s order by date_as asc limit 1) c 
                        on c.code_id = a.code_id
                    where c.j < a.j
                    and a.date_as = %s and a.code_id = %s
                    '''
            result2 = SharesKdjCompute.objects.raw(sql, params=(tomorrow, code_id, today, code_id,))
            if len(result2) == 0:
                continue
            sql = '''select 1 as id,p_end from mc_shares  where date_as = %s and code_id =  %s '''
            result2 = SharesKdjCompute.objects.raw(sql, params=(tomorrow, code_id,))
            end_p = result2[0].p_end
            diff = end_p - start_p
            return diff, today

        if dateLen < 11:
            print("已遍历完成")

        return False, False
