from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.


class SharesWeekMacds(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    macd = models.FloatField(default=0)
    diff = models.FloatField(default=0)
    dea = models.FloatField(default=0)
    cycle_type = models.IntegerField(default=0, help_text='1.26,12,9')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_macd_weeks"
        # abstract = True

    def __str__(self):
        return self.code_id
