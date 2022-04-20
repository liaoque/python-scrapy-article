from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesKdjHours(models.Model):
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    k = models.FloatField(default=0)
    d = models.FloatField(default=0)
    j = models.FloatField(default=0)
    cycle_type = models.IntegerField(default=0, help_text='1.9,3,3')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_kdj_hours"
        # abstract = True

    def __str__(self):
        return self.name
