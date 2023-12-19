from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.

def saveD(d):
    date_obj = datetime.strptime(d["date"], '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    if SharesBlockGns.objects.filter(code_id=d["指数代码"], date_as=formatted_date).count():
        return

    sharesZhangTings = SharesBlockGns(
        code_id=d["指数代码"],
        name=d["指数简称"],
        p_min=d["最低价"],
        p_max=d["最高价"],
        p_start=d["开盘价"],
        p_end=d["收盘价"],
        p_zhang_die_fu=d["涨跌幅"],
        date_as=formatted_date,
    )
    sharesZhangTings.save()


class SharesBlockGns(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_min = models.FloatField(help_text="最小")
    p_max = models.FloatField(help_text="最大")
    p_start = models.FloatField(help_text="开始")
    p_end = models.FloatField(help_text="结束")
    p_zhang_die_fu = models.FloatField(help_text="涨跌幅")
    date_as = models.DateField(help_text="创建时间")

    class Meta:
        db_table = "mc_shares_block_gns"
        # abstract = True

    def __str__(self):
        return self.name + datetime.strftime(self.date_as, '%Y-%m-%d %H:%i:%s')
