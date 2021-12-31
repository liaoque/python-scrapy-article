import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

# from ....polls.models import Question as Poll
from shares.model.shares_name import SharesName
from shares.model.shares_kdj import SharesKdj
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
        print("开始计算-----")
        dateList = self.getAllDates()
        # for item in dateList:
        #     print(item.date_as)
        i = 0
        while i < len(dateList):
            first = dateList[0+i].date_as
            second = dateList[1+i].date_as
            if 5+i >= len(dateList):
                break
            fifth = dateList[3+i].date_as
            result = self.compute1(first, second, fifth)
            slen = len(result)
            print("%s-%s-%s-收益大于3的：%s"%(first, second, fifth, slen))
            for item in result:
                print("%s--%s"%(item.code_id, str(item.rate)))
            print("---------")

            result = self.compute2(first, second, fifth)
            slen = len(result)
            print("%s-%s-%s-收益小于0的：%s"%(first, second, fifth, slen))
            for item in result:
                print("%s--%s" % (item.code_id, str(item.rate)))
            print("---------")
            i = i + 1

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_kdj group by date_as;
            '''
        return SharesKdjCompute.objects.raw(sql)

    def compute1(self, first, second, fifth):
        sql = '''
            SELECT 1 as id, mc_shares_kdj.code_id,(e.p_end / c.p_end) as rate FROM `mc_shares_kdj`
            left join (select p_end,code_id from mc_shares where date_as = %s) c on c.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id from mc_shares where date_as = %s) d on d.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max from mc_shares where date_as = %s) e on e.code_id = mc_shares_kdj.code_id
            where j <16 and date_as = %s and mc_shares_kdj.code_id not in (SELECT code_id FROM `mc_shares_ban` )
            and mc_shares_kdj.code_id not in (SELECT code FROM `mc_shares_name` where name like "%s" )
            and (mc_shares_kdj.code_id < 300000 or mc_shares_kdj.code_id > 600000)
            and mc_shares_kdj.code_id < 800000
            and  ((k - j) > 0 and (d - j) > 0) and ((k - j) <=5 and (d - j) <= 5)
            and c.p_end > d.p_end
            having rate >= 1.03
        '''
        return SharesKdjCompute.objects.raw(sql,params=(second, first, fifth, second,'%ST%',))

    def compute2(self, first, second, fifth):
        sql = '''
            SELECT 1 as id, mc_shares_kdj.code_id,(e.p_end / c.p_end) as rate FROM `mc_shares_kdj`
            left join (select p_end,code_id from mc_shares where date_as = %s) c on c.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id from mc_shares where date_as = %s) d on d.code_id = mc_shares_kdj.code_id
            left join (select p_end,code_id,p_max from mc_shares where date_as = %s) e on e.code_id = mc_shares_kdj.code_id
            where j <16 and date_as = %s and mc_shares_kdj.code_id not in (SELECT code_id FROM `mc_shares_ban` )
            and mc_shares_kdj.code_id not in (SELECT code FROM `mc_shares_name` where name like "%s" )
            and (mc_shares_kdj.code_id < 300000 or mc_shares_kdj.code_id > 600000)
            and mc_shares_kdj.code_id < 800000
            and  ((k - j) > 0 and (d - j) > 0) and ((k - j) <=5 and (d - j) <= 5)
            and c.p_end > d.p_end
            having rate < 0
        '''
        return SharesKdjCompute.objects.raw(sql,params=(second, first, fifth, second,'%ST%',))