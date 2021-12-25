from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesBan(models.Model):
    code = models.ForeignKey(SharesName, default=0, on_delete=models.CASCADE)
    remain_avoid_cycle = models.IntegerField(default=0, help_text="剩余回避天数")
    avoid_cycle = models.FloatField(default=0, help_text="回避天数")
    avoid_reason = models.CharField(max_length=20, help_text='原因')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_ban"

    def __str__(self):
        return self.code_id + ":" + self.avoid_reason
