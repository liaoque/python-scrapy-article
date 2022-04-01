from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.


class SharesHalfYear(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    p_year = models.IntegerField(default=0)
    p_year_half = models.IntegerField(default=0, help_text="1 前半年，2 后半年")

    class Meta:
        db_table = "mc_shares_half_year"
        # abstract = True

    def __str__(self):
        return self.name + ":" + self.p_year  + ":" + self.p_year_half  + ":最大-" + self.p_start  + ":最小-" + self.p_end
