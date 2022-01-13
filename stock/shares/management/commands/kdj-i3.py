import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_industry_kdj import SharesIndustryKdj
import numpy as np
import talib



class Command(BaseCommand):
    help = '先查预期的行业。再根据行业查对应股票'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("开始计算-----")
        dateList = self.getAllDates()
        # for item in dateList:
        #     print(item.date_as)
        slen1 = len(dateList)
        first = dateList[slen1 - 2].date_as
        second = dateList[slen1 - 1].date_as
        result = self.compute3(first, second)
        print(result)
        print("%s-%s-挑选出股票：%s个" % (first, second, len(result)))
        for item in result:
            print('%s'% (item.code_id))
        print("---------")

        i = 0
        while i < slen1:
            first = dateList[0 + i].date_as
            second = dateList[1 + i].date_as
            if 4 + i >= len(dateList):
                break
            fifth = dateList[4 + i].date_as
            result = self.compute1(first, second, fifth)

            slen = len(result)
            print("%s-%s-%s-收益大于3的：%s" % (first, second, fifth, slen))
            for item in result:
                print("%s--%s" % (item.code_id, str(item.rate)))
            print("---------")

            result = self.compute2(first, second, fifth)
            slen = len(result)
            print("%s-%s-%s-收益小于0的：%s" % (first, second, fifth, slen))
            for item in result:
                print("%s--%s" % (item.code_id, str(item.rate)))
            print("---------")
            i = i + 1

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_kdj group by date_as;
            '''
        return SharesIndustryKdj.objects.raw(sql)

    def compute1(self, first, second, fifth):
        sql = '''
            SELECT 1 as id, mc_shares_kdj.code_id,(e.p_end / c.p_end) as rate FROM `mc_shares_kdj`
            left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) c on c.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) d on d.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max from mc_shares where date_as = %s) e on e.code_id = mc_shares_kdj.code_id
            left join (select code_id,industry_code_id from mc_shares_join_industry) f on f.code_id = mc_shares_kdj.code_id
            where  j <20  and date_as = %s and mc_shares_kdj.code_id not in (SELECT code_id FROM `mc_shares_ban` )
            and mc_shares_kdj.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
            and (mc_shares_kdj.code_id < 300000 or mc_shares_kdj.code_id > 600000)
            and mc_shares_kdj.code_id < 800000
            and  ((k - j) <= 0 and (d - j) <= 0) 
            and c.p_end > d.p_end
            and f.industry_code_id in (
                 select ikdj.code_id from mc_shares_industry_kdj ikdj
                    left join mc_shares_industry t on t.code_id = ikdj.code_id  and t.date_as = ikdj.date_as
                    left join mc_shares_industry y on y.code_id = ikdj.code_id
                        and y.date_as = DATE_FORMAT(DATE_SUB(ikdj.date_as,INTERVAL 1 DAY), %s)
                    where ikdj.date_as = %s and t.p_end > y.p_end
                    and ikdj.j > ikdj.k and ikdj.j > ikdj.d
            )
          
            and cast(c.p_end AS signed) - cast(c.p_start AS signed) > 5
            having rate >= 1.03
        '''
        return SharesIndustryKdj.objects.raw(sql, params=(second, first, fifth, second, '%ST%', '%Y-%m-%d', second,))

    def compute2(self, first, second, fifth):
        sql = '''
            SELECT 1 as id, mc_shares_kdj.code_id,(e.p_end / c.p_end) as rate FROM `mc_shares_kdj`
            left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) c on c.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) d on d.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max from mc_shares where date_as = %s) e on e.code_id = mc_shares_kdj.code_id
            left join (select code_id,industry_code_id from mc_shares_join_industry) f on f.code_id = mc_shares_kdj.code_id
            where  j <20  and date_as = %s and mc_shares_kdj.code_id not in (SELECT code_id FROM `mc_shares_ban` )
            and mc_shares_kdj.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
            and (mc_shares_kdj.code_id < 300000 or mc_shares_kdj.code_id > 600000)
            and mc_shares_kdj.code_id < 800000
           and  ((k - j) <= 0 and (d - j) <= 0) 
            and c.p_end > d.p_end
            and f.industry_code_id in (
                 select ikdj.code_id from mc_shares_industry_kdj ikdj
                    left join mc_shares_industry t on t.code_id = ikdj.code_id  and t.date_as = ikdj.date_as
                    left join mc_shares_industry y on y.code_id = ikdj.code_id
                        and y.date_as = DATE_FORMAT(DATE_SUB(ikdj.date_as,INTERVAL 1 DAY), %s)
                    where ikdj.date_as = %s and t.p_end > y.p_end
                    and ikdj.j > ikdj.k and ikdj.j > ikdj.d
            )
   
            and cast(c.p_end AS signed) - cast(c.p_start AS signed) > 5
            having rate < 1
        '''
        return SharesIndustryKdj.objects.raw(sql, params=(second, first, fifth, second, '%ST%', '%Y-%m-%d', second,))

    def compute3(self, first, second):
        sql = '''
        SELECT 1 as id, mc_shares_kdj.code_id FROM `mc_shares_kdj`
left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) c on c.code_id = mc_shares_kdj.code_id
left join (select p_end,code_id,p_max,p_start from mc_shares where date_as = %s) d on d.code_id = mc_shares_kdj.code_id
left join (select code_id,industry_code_id from mc_shares_join_industry) f on f.code_id = mc_shares_kdj.code_id
where  j <20 and date_as = %s and mc_shares_kdj.code_id not in (SELECT code_id FROM `mc_shares_ban` )
and mc_shares_kdj.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
and (mc_shares_kdj.code_id < 300000 or mc_shares_kdj.code_id > 600000)
and mc_shares_kdj.code_id < 800000
and  ((k - j) <= 0 and (d - j) <= 0)
and c.p_end > d.p_end
and f.industry_code_id in (
    select ikdj.code_id from mc_shares_industry_kdj ikdj
    left join mc_shares_industry t on t.code_id = ikdj.code_id  and t.date_as = ikdj.date_as
    left join mc_shares_industry y on y.code_id = ikdj.code_id
        and y.date_as = DATE_FORMAT(DATE_SUB(ikdj.date_as,INTERVAL 1 DAY), %s)
    where ikdj.date_as = %s and t.p_end > y.p_end
    and ikdj.j > ikdj.k and ikdj.j > ikdj.d
    ) 

and cast(c.p_end AS signed) - cast(c.p_start AS signed) > 5 '''
        return SharesIndustryKdj.objects.raw(sql, params=(second, first, second, '%ST%', '%Y-%m-%d',second,))
