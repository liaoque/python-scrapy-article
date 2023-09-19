from django.db import models
from .shares_name import SharesName
from datetime import datetime

# Create your models here.


class SharesWeeks(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_min = models.IntegerField(default=0)
    p_max = models.IntegerField(default=0)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    date_as = models.DateTimeField()

    class Meta:
        db_table = "mc_shares_weeks"
        # abstract = True

    def __str__(self):
        return self.name + ":" + datetime.strftime(self.date_as,'%Y-%m-%d %H:%i:%s')
