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
    p_month = models.IntegerField(default=0, help_text="1 第一季，2 第二季")

    class Meta:
        db_table = "mc_shares_month"
        # abstract = True

    def __str__(self):
        return self.name + ":" + self.p_year + ":" + self.p_month + ":最大-" + self.p_start + ":最小-" + self.p_end
