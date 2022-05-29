from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.


class SharesFH(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    info = models.CharField(max_length=30)
    amount = models.IntegerField()
    range = models.IntegerField()
    directors_date_as = models.DateField(help_text='董事会日期')
    shareholder_date_as = models.DateField(help_text='股东大会预案公告日期')
    implement_date_as = models.DateField(help_text='实施公告日')
    register_date_as = models.DateField(help_text='A股股权登记日')
    ex_date_as = models.DateField(help_text='A股除权除息日')

    class Meta:
        db_table = "mc_shares_fh"
        # abstract = True

    def __str__(self):
        return self.code + ":" + str(self.title) + ":" + str(self.info) + ":" + self.directors_date_as
