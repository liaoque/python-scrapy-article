from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesDate(models.Model):
    date_as = models.DateField()
    master_buy_sum = models.IntegerField(default=0,help_text="主力流如")
    master_buy_sell = models.IntegerField(default=0,help_text="主力流出")

    class Meta:
        db_table = "mc_shares_date"

    def __str__(self):
        return self.date_as
