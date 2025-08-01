from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.




class SharesBlockGns(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_min = models.FloatField(help_text="最小")
    p_max = models.FloatField(help_text="最大")
    p_start = models.FloatField(help_text="开始")
    p_end = models.FloatField(help_text="结束")
    p_zhang_die_fu = models.FloatField(help_text="涨跌幅")
    date_as = models.DateField(help_text="创建时间")
    morning = models.IntegerField(help_text="9点32分钟数据")  # 1 是， 2不是

    class Meta:
        db_table = "mc_shares_block_gns"
        # abstract = True

    def __str__(self):
        return self.name + datetime.strftime(self.date_as, '%Y-%m-%d %H:%i:%s')
