from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.


def saveD(d):
    date_obj = datetime.strptime(d["date"], '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    if SharesZhangTings.objects.filter(code_id=d["股票代码"], date_as=formatted_date).count():
        return

    sharesZhangTings = SharesZhangTings(
        code_id=d["股票代码"],
        name=d["股票简称"],
        gn=d["所属概念"],
        hy=d["所属同花顺行业"],
        first_zhang_ting=d["首次涨停时间"],
        last_zhang_ting=d["最终涨停时间"],
        n_day_n_zhang_ting=d["几天几板"],
        continuous_zhang_ting=d["连续涨停天数"],
        liu_tong_shi_zhi=int(float(d["a股市值流通市值"])),
        date_as=formatted_date,
        f32=d["f32"],
        gao_biao=d["gao_biao"]
    )
    sharesZhangTings.save()


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


    class Meta:
        db_table = "mc_shares_zhang_tings"
        # abstract = True

    def __str__(self):
        return self.name + datetime.strftime(self.date_as,'%Y-%m-%d %H:%i:%s')

