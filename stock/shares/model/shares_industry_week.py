from django.db import models

from .shares_name import SharesName
# Create your models here.
from datetime import datetime
#
# SELECT code_id,MIN(p_min),max(p_max),MIN(p_start),MAX(p_end),MIN(date_as),max(date_as), date_week
# FROM (SELECT code_id,p_min, p_max,p_start, p_end,date_as, YEAR(date_as) as date_year, week(date_as, 1) as date_week FROM `mc_shares_industry` where code_id = 'BK0420'
# ORDER BY `mc_shares_industry`.`date_as`  ASC) t
# where code_id = 'BK0420' GROUP by date_year, date_week;
class SharesIndustryWeek(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    p_min = models.IntegerField(default=0)
    p_max = models.IntegerField(default=0)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    macd = models.IntegerField(default=0)
    # avg10 = models.FloatField(default=0)
    # avg20 = models.FloatField(default=0)
    # avg10_rate = models.FloatField(default=0)
    # avg20_rate = models.FloatField(default=0)
    avg_p_min_rate = models.FloatField(default=0)
    avg_p_max_rate = models.FloatField(default=0)
    max_min_flag = models.IntegerField(default=0)
    # avg30 = models.FloatField(default=0)
    # avg60 = models.FloatField(default=0)
    # avg120 = models.FloatField(default=0)
    # avg200 = models.FloatField(default=0)
    # avg30_rate = models.FloatField(default=0)
    # avg60_rate = models.FloatField(default=0)
    # avg120_rate = models.FloatField(default=0)
    # avg200_rate = models.FloatField(default=0)

    date_as = models.DateField()
    date_as_end = models.DateField()
    date_week = models.IntegerField(default=0)

    class Meta:
        db_table = "mc_shares_industry_week"
        # abstract = True

    def __str__(self):
        return self.code_id + ":" + datetime.strftime(
            self.date_as, '%Y-%m-%d') + ":开始-" + str(self.p_start) + ":结束-" + str(self.p_end)
