from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.


class SharesMonth(models.Model):
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    p_year = models.IntegerField(default=0)
    buy_count = models.IntegerField(default=0, help_text="交易量， 单位万")
    buy_sum = models.IntegerField(default=0, help_text="交易金额， 单位万")
    p_month = models.IntegerField(default=0, help_text="1 第一季，2 第二季")

    class Meta:
        db_table = "mc_shares_month"
        # abstract = True

    def __str__(self):
        return self.name + ":" + str(self.p_year) + ":" + str(self.p_month) + ":最大-" + str(self.p_start) + ":最小-" + str(self.p_end)
