from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesKdjCompute(models.Model):
    intersection_pre_num = models.IntegerField(default=0, help_text='交点前一天')
    intersection_num = models.IntegerField(default=0, help_text='交点')
    intersection_total = models.IntegerField(default=0, help_text='交点-总')
    intersection_pre_total_amount = models.FloatField(default=0, help_text='交点前一天-总盈利')
    intersection_total_amount = models.FloatField(default=0, help_text='交点-总盈利')
    turn_num = models.IntegerField(default=0, help_text='转折点')
    turn_total = models.IntegerField(default=0, help_text='转折点-总')
    turn_total_amount = models.FloatField(default=0, help_text='转折点-总盈利')
    shill_type = models.IntegerField(default=0, help_text='技术指标：1.kdj')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_compute"
        # abstract = True

    # def __str__(self):
    #     return self.date_as

    class Compute():
        # 三天股票j值都是上涨的数量
        def intersection_total(first, second, third):
            sql = '''
            select 1 as id,count(1) as c from (
                          select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                            where date_as in (%s, %s, %s) group by code_id
                      ) a
                      left join  (select k, d,code_id,j from mc_shares_kdj where date_as = %s) b on a.code_id = b.code_id
                      where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                            and b.k <=b.j and b.d <= b.j
            				and b.j < 16
            '''
            return SharesKdjCompute.objects.raw(sql, params=(first, second, third, second,))

        # 计算以交点前一天收盘价作为买点的数据，持有2天，以第二天的收盘价作为卖点
        def intersection_pre(first, second, third):
            sql = '''
                select 1 as id,sa.code_id, sb.p_end as buy_amount, sb.date_as as buy_date_as, 
                                sc.p_end as buy_amount_end, sc.date_as as buy_date_as_end from (
                              select a.code_id from (
                                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                                    where date_as in (%s, %s, %s) group by code_id
                              ) a
                              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = %s) b on a.code_id = b.code_id
                              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                                    and b.k <=b.j and b.d <= b.j
                                    and b.j < 16
                ) sa
                  left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sb on sa.code_id = sb.code_id
                  left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sc on sa.code_id = sc.code_id
                 where sb.p_end < sc.p_end
                '''
            return SharesKdjCompute.objects.raw(sql, params=(first, second, third, second, first, third))

        # 计算以交点收盘价作为买点的数据，持有2天，以第二天的收盘价作为卖点
        def intersection_today(first, second, third, fourth):
            sql = '''
                select 1 as id,sa.code_id, sb.p_end as buy_amount, sb.date_as as buy_date_as, 
                                sc.p_end as buy_amount_end, sc.date_as as buy_date_as_end from (
                              select a.code_id from (
                                  select code_id, min(j) as minj, max(j) as maxj from mc_shares_kdj
                                    where date_as in (%s, %s, %s) group by code_id
                              ) a
                              left join  (select k, d,code_id,j from mc_shares_kdj where date_as = %s) b on a.code_id = b.code_id
                              where (a.minj < b.k and b.k < a.maxj)  and (a.minj < b.d and b.d < a.maxj)
                                    and b.k <=b.j and b.d <= b.j
                                    and b.j < 16
                ) sa
                  left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sb on sa.code_id = sb.code_id
                  left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sc on sa.code_id = sc.code_id
                 where sb.p_end < sc.p_end
                '''
            return SharesKdjCompute.objects.raw(sql, params=(first, second, third, second, second, fourth))

        def turn_total(first, second, third):
            sql = '''
            select 1 as id,count(1) as c from (select code_id,j from mc_shares_kdj where date_as = %s and j <10) a
                      left join  (select  k, d,code_id,j from mc_shares_kdj where date_as = %s) b on a.code_id = b.code_id
                      left join  (select code_id,j from mc_shares_kdj where date_as = %s) c on a.code_id = c.code_id
              where (a.j > b.j and b.j < c.j)
              and b.j < 0
            '''
            return SharesKdjCompute.objects.raw(sql, params=(first, second, third))

        # 计算以转折做为买点的数据，持有2天，以第二天的收盘价作为卖点
        def turn_tomorrow(first, second, third, fifth):
            sql = '''
            select 1 as id,sa.code_id,sb.p_end as buy_amount, sb.date_as as buy_date_as, 
                                sc.p_end as buy_amount_end, sc.date_as as buy_date_as_end from (
              select a.code_id,a.j from (select code_id,j from mc_shares_kdj where date_as = %s and j <10) a
                      left join  (select  k, d,code_id,j from mc_shares_kdj where date_as = %s) b on a.code_id = b.code_id
                      left join  (select code_id,j from mc_shares_kdj where date_as = %s) c on a.code_id = c.code_id
              where (a.j > b.j and b.j < c.j)
              and b.j < 0
            ) sa
              left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sb on sa.code_id = sb.code_id
              left join  (select p_end,code_id,date_as from mc_shares where date_as = %s) sc on sa.code_id = sc.code_id
            where sb.p_end < sc.p_end
            '''
            return SharesKdjCompute.objects.raw(sql, params=(first, second, third, third, fifth))

    def saveSharesKdjCompute(intersection_pre_num, intersection_num, intersection_total, turn_num, turn_total,
                             shill_type, date_as, intersection_pre_total_amount,intersection_total_amount,turn_total_amount):
        result = SharesKdjCompute.objects.filter(date_as=date_as)
        if len(result):
            kdjCompute = SharesKdjCompute(id=result[0].id,
                              intersection_pre_num=intersection_pre_num,
                              intersection_num=intersection_num,
                              intersection_total=intersection_total,
                              turn_num=turn_num,
                              turn_total=turn_total,
                              shill_type=shill_type,
                              intersection_pre_total_amount=intersection_pre_total_amount,
                              intersection_total_amount=intersection_total_amount,
                              turn_total_amount=turn_total_amount,
                              date_as=date_as)
        else:
            kdjCompute = SharesKdjCompute(intersection_pre_num=intersection_pre_num,
                              intersection_num=intersection_num,
                              intersection_total=intersection_total,
                              turn_num=turn_num,
                              turn_total=turn_total,
                              shill_type=shill_type,
                              intersection_pre_total_amount=intersection_pre_total_amount,
                              intersection_total_amount=intersection_total_amount,
                              turn_total_amount=turn_total_amount,
                              date_as=date_as)
        return kdjCompute.save()
