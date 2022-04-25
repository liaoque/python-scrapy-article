from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesDateListen(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    p_start = models.IntegerField(default=0)
    type = models.IntegerField(default=0, help_text="1.kdj-10的股票")
    buy_start = models.IntegerField(default=0)
    buy_pre = models.IntegerField(default=0)
    buy_date_as = models.DateField(null=True)
    date_as = models.DateField()


    class Meta:
        db_table = "mc_shares_date_listen"

    def __str__(self):
        return self.name
