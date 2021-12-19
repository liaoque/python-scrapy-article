from django.db import models


# Create your models here.


class SharesName(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    temper_tonghuashun = models.IntegerField(default=0)
    temper_dongfangcaifu = models.IntegerField(default=0)
    area_id = models.IntegerField(default=0)

    class Meta:
        db_table = "mc_shares_name"
        abstract = True

    def __str__(self):
        return self.name
