from django.db import models

from .shares_name import SharesName
# Create your models here.
from datetime import datetime

class SharesIndustry(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    p_min = models.IntegerField(default=0)
    p_max = models.IntegerField(default=0)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_industry"
        # abstract = True

    def __str__(self):
        return self.code + ":" + datetime.strftime(self.date_as, '%Y-%m-%d')


