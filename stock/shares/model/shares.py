from django.db import models
from .shares_name import SharesName


# Create your models here.


class Shares(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_min = models.IntegerField(default=0)
    p_max = models.IntegerField(default=0)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    p_range = models.IntegerField(default=0)
    p_count = models.IntegerField(default=0)
    p_sum = models.IntegerField(default=0)
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares"

    def __str__(self):
        return self.name + ":" + self.date_as
