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


class Command(BaseCommand):
    help = '即将相交的kdj'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        print("开始计算-----")
        dateList = self.getAllDates()
        slen1 = len(dateList)
        first = dateList[slen1 - 2].date_as
        second = dateList[slen1 - 1].date_as
        result = self.compute3(first, second)
        print(result)
        print("%s-%s-挑选出股票：%s个" % (first, second, len(result)))
        print(",".join(["\"" + item.code_id + "\"" for item in result]))

    def getAllDates(self):
        sql = '''
            select 1 as id, date_as from mc_shares_kdj_hours where date_as >= '2022-04-01' group by date_as order by date_as asc;
            '''
        return SharesKdjCompute.objects.raw(sql)

    def compute3(self, yesterday, today):
        sql = '''
        SELECT 1 as id, mc_shares_kdj_hours.code_id FROM `mc_shares_kdj_hours`
left join (select p_end,code_id from mc_shares_hours where date_as = %s) c on c.code_id = mc_shares_kdj_hours.code_id
left join (select p_end,code_id from mc_shares_hours where date_as = %s) d on d.code_id = mc_shares_kdj_hours.code_id
left join (select code_id,industry_code_id from mc_shares_join_industry) f on f.code_id = mc_shares_kdj_hours.code_id
where j <40 and date_as = %s and mc_shares_kdj_hours.code_id not in (SELECT code_id FROM `mc_shares_ban` )
and mc_shares_kdj_hours.code_id not in (SELECT code FROM `mc_shares_name` where name like %s )
and (mc_shares_kdj_hours.code_id < 300000 or mc_shares_kdj_hours.code_id > 600000)
and mc_shares_kdj_hours.code_id < 680000
and  ((k - j) > 0 and (d - j) > 0) and ((k - j) <=5 and (d - j) <= 5)
and c.p_end > d.p_end
and f.industry_code_id in (
    select mc_shares_industry.code_id from mc_shares_industry
    left join (select code_id,p_end from mc_shares_industry where date_as = %s) z on z.code_id = mc_shares_industry.code_id
    where date_as = %s and z.p_end < mc_shares_industry.p_end
    )
and mc_shares_kdj_hours.code_id in (
    SELECT code_id FROM `mc_shares_kdj_hours`
    where  (k - j) > 5 
    and date_as = %s
    )
        '''
        return SharesKdjCompute.objects.raw(sql, params=(
            today, yesterday, today, '%ST%',
            yesterday, today, yesterday,
            yesterday, today,
        ))
