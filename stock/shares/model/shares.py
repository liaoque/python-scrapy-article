from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.


class Shares(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_min = models.IntegerField(default=0)
    p_max = models.IntegerField(default=0)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    p_range = models.IntegerField(default=0)
    buy_count = models.IntegerField(default=0)
    buy_sum = models.IntegerField(default=0)
    master_buy_sum = models.IntegerField(default=0, help_text="主力流如")
    master_buy_sell = models.IntegerField(default=0, help_text="主力流出")
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares"
        # abstract = True

    def __str__(self):
        return self.name + ":" + str(self.p_start) + ":" + str(self.p_end) + ":" + datetime.strftime(self.date_as, '%Y-%m-%d')
