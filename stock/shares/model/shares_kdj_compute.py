from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesKdjCompute(models.Model):
    intersection_pre_num = models.IntegerField(default=0, help_text='交点前一天')
    intersection_num = models.IntegerField(default=0, help_text='交点')
    intersection_total = models.FloatField(default=0, help_text='交点-总')
    turn_num = models.IntegerField(default=0, help_text='转折点')
    turn_total = models.IntegerField(default=0, help_text='转折点-总')
    shill_type = models.IntegerField(default=0, help_text='技术指标：1.kdj')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_compute"
        # abstract = True

    def __str__(self):
        return self.date_as

    class Compute():
        def intersection_total(self, first, second, third):
            sql = '''
            select count(1) as c from (
                          select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                            where date_as in ('%s', '%s', '%s') group by code_id
                      ) a
                      left join  (select k, d,code_id,j from mc_shares_kdj where date_as = '%s') b on a.code_id = b.code_id
                      where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                            and b.k <=b.j and b.d <= b.j
            				and b.j < 30
            '''
            return SharesKdjCompute.object.raw(sql, first, second, third, second)

        # 计算以交点作为买点的数据
        def intersection_pre(self, first, second, third):
            sql = '''
                select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
                              select a.code_id from (
                                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                                    where date_as in ('%s', '%s', '%s') group by code_id
                              ) a
                              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = '%s') b on a.code_id = b.code_id
                              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                                    and b.k <=b.j and b.d <= b.j
                                    and b.j < 30
                ) sa
                  left join  (select p_end,code_id from mc_shares where date_as = '%s') sb on sa.code_id = sb.code_id
                  left join  (select p_end,code_id from mc_shares where date_as = '%s') sc on sa.code_id = sc.code_id
                 where sb.p_end < sc.p_end
                '''
            return SharesKdjCompute.object.raw(sql, first, second, third, second, first, third)

        def intersection_today(self, first, second, third, fourth):
            sql = '''
                select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
                              select a.code_id from (
                                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                                    where date_as in ('%s', '%s', '%s') group by code_id
                              ) a
                              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = '%s') b on a.code_id = b.code_id
                              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                                    and b.k <=b.j and b.d <= b.j
                                    and b.j < 30
                ) sa
                  left join  (select p_end,code_id from mc_shares where date_as = '%s') sb on sa.code_id = sb.code_id
                  left join  (select p_end,code_id from mc_shares where date_as = '%s') sc on sa.code_id = sc.code_id
                 where sb.p_end < sc.p_end
                '''
            return SharesKdjCompute.object.raw(sql, first, second, third, second, second, fourth)

        def turn_total(self, first, second, third):
            sql = '''
            select count(1) as c from (select code_id,j from mc_shares_kdj where date_as = '%s' and j <10) a
                      left join  (select  k, d,code_id,j from mc_shares_kdj where date_as = '%s') b on a.code_id = b.code_id
                      left join  (select code_id,j from mc_shares_kdj where date_as = '%s') c on a.code_id = c.code_id
              where (a.j > b.j and b.j < c.j)
            '''
            return SharesKdjCompute.object.raw(sql, first, second, third, second)

        # 计算以转折做为买点的数据
        def turn_tomorrow(self, first, second, third, fifth):
            sql = '''
            select sa.code_id, (sc.p_end - sb.p_end)/sb.p_end*100 from (
              select a.code_id,a.j from (select code_id,j from mc_shares_kdj where date_as = '%s' and j <10) a
                      left join  (select  k, d,code_id,j from mc_shares_kdj where date_as = '%s') b on a.code_id = b.code_id
                      left join  (select code_id,j from mc_shares_kdj where date_as = '%s') c on a.code_id = c.code_id
              where (a.j > b.j and b.j < c.j)
            ) sa
              left join  (select p_end,code_id from mc_shares where date_as = '%s') sb on sa.code_id = sb.code_id
              left join  (select p_end,code_id from mc_shares where date_as = '%s') sc on sa.code_id = sc.code_id
            where sb.p_end < sc.p_end
            '''
            return SharesKdjCompute.object.raw(sql, first, second, third, third, fifth)

    def saveSharesKdjCompute(self, intersection_pre_num, intersection_num, intersection_total, turn_num, turn_total,
                             shill_type, date_as):
        result = self.objects.filter(date_as=date_as)
        if len(result):
            pass
        else:
            kdjCompute = self(intersection_pre_num=intersection_pre_num,
                              intersection_num=intersection_num,
                              intersection_total=intersection_total,
                              turn_num=turn_num,
                              turn_total=turn_total,
                              shill_type=shill_type,
                              date_as=date_as)
            kdjCompute.save()
