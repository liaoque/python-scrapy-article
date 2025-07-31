from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.





class SharesZhangTings(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    gn = models.TextField(help_text="概念") # 概念
    hy = models.CharField(max_length=50, help_text="行业") # 行业
    first_zhang_ting = models.TimeField(help_text="第一个涨停时间") # 第一个涨停时间
    last_zhang_ting = models.TimeField(help_text="最后一个涨停时间") # 最后一个涨停时间
    n_day_n_zhang_ting = models.CharField(help_text="几天几版",max_length=30) # 几天几版
    continuous_zhang_ting = models.IntegerField(help_text="连续涨停天数") # 连续涨停时间
    liu_tong_shi_zhi = models.BigIntegerField(help_text="流通市值") # 流通市值
    date_as = models.DateField(help_text="创建时间") # 创建时间
    f32 = models.IntegerField(help_text="9点32分钟之前涨停") # 9点32分钟之前涨停
    gao_biao = models.IntegerField(help_text="高标票标记") # 9点32分钟之前涨停
    morning = models.IntegerField(help_text="9点32分钟数据") # 1 是， 2不是


    class Meta:
        db_table = "mc_shares_zhang_tings"
        # abstract = True

    def __str__(self):
        return self.name + datetime.strftime(self.date_as,'%Y-%m-%d %H:%i:%s')

