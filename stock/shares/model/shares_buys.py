from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesBuys(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    buy_date_as = models.DateField(null=True)
    buy_start = models.IntegerField(default=0)
    buy_pre = models.IntegerField(default=0)
    sell_date_as = models.DateField(null=True)
    sell_end = models.IntegerField(default=0)
    sell_pre = models.IntegerField(default=0)


    class Meta:
        db_table = "mc_shares_buys"

    def __str__(self):
        return self.code_id
