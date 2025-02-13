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
from django.db import connection
from shares.model.shares_date import SharesDate


class Command(BaseCommand):
    help = "计算股票的涨停，跌停"

    def handle(self, *args, **options):
        shareDate = SharesDate.objects.order_by('date_as')
        c = len(shareDate)
        shareDate = shareDate[c - 10:]
        c = len(shareDate)

        for key in range(c):
            if key + 1 > c:
                break
            date_as = shareDate[key].date_as
            self.zhangting(date_as)
            self.dieting(date_as)
            self.lianban(date_as)
            self.dapan(date_as)

    def dapan(self, date_as):
        # 大盘涨停数， 跌停数，连板数
        sql = "select 0 as id, sum(zhangting) as max_zhangting, sum(dieting) as max_dieting , max(lianban) as max_lianban from mc_shares  where  date_as = %s";
        result = SharesKdjCompute.objects.raw(sql, params=(date_as,))
        for item in result:
            sql = "select id from mc_dapan where date_as = %s"
            result2 = SharesKdjCompute.objects.raw(sql, params=(date_as,))
            if len(result2):
                sql = "UPDATE mc_dapan SET max_zhangting=%s, max_dieting=%s, max_lianban=%s  where id = %s"
                cursor = connection.cursor()
                cursor.execute(sql, [item.max_zhangting, item.max_dieting, item.max_lianban, result2[0].id])
            else:
                sql = "INSERT INTO mc_dapan (max_zhangting, max_dieting, max_lianban, date_as)VALUES(%s, %s, %s, %s)"
                cursor = connection.cursor()
                cursor.execute(sql, [item.max_zhangting, item.max_dieting, item.max_lianban, date_as])

    def zhangting(self, date_as):
        sql = "update mc_shares set zhangting =1 where code_id < '300000' and p_range > 995  and p_range < 1100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set zhangting =1 where code_id < '608000' and code_id >= '600000'  and p_range > 995 and p_range < 1100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set zhangting =1 where code_id < '400000' and code_id >= '300000'  and p_range > 1995 and p_range < 2100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set zhangting =1 where code_id < '600000' and code_id >= '400000'  and p_range > 2995 and p_range < 3100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set zhangting =1 where  code_id >= '680000'  and p_range > 2995 and p_range < 3100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])

    def dieting(self, date_as):
        sql = "update mc_shares set dieting =1,zhangting =0 where code_id < '300000' and p_range < -995  and p_range > -1100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set dieting =1,zhangting =0 where code_id < '608000' and code_id >= '600000'  and p_range < -995 and p_range > -1100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set dieting =1,zhangting =0 where code_id < '400000' and code_id >= '300000'  and p_range < -1995 and p_range > -2100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set dieting =1,zhangting =0 where code_id < '600000' and code_id >= '400000'  and p_range < -2995 and p_range > -3100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])
        sql = "update mc_shares set dieting =1,zhangting =0 where  code_id >= '680000'  and p_range < -2995 and p_range < -3100 and date_as = %s";
        cursor = connection.cursor()
        cursor.execute(sql, [date_as])

    def lianban(self, date_as):
        sql = "select id,code_id from mc_shares  where  zhangting =1 and date_as = %s";
        result = SharesKdjCompute.objects.raw(sql, params=(date_as,))
        for item in result:
            sql = "select id, code_id, lianban,zhangting from mc_shares  where  code_id =%s and  date_as < %s order by date_as desc limit 1";
            result2 = SharesKdjCompute.objects.raw(sql, params=(item.code_id, date_as,))
            sql = "update mc_shares set lianban =%s where  code_id =%s  and date_as = %s";
            if len(result2) > 0:
                item2 = result2[0]
                if item2.zhangting != 1:
                    return
                cursor = connection.cursor()
                cursor.execute(sql, [item2.lianban + 1, item2.code_id, date_as])
            else:
                cursor = connection.cursor()
                cursor.execute(sql, [1, item.code_id, date_as])
