from django.db import models

from .shares_name import SharesName
import json

# Create your models here.

# 指数和国债
class DaPan(models.Model):
    max_zhangting = models.FloatField(default=0, help_text="涨停家数")
    max_dieting = models.FloatField(default=0, help_text="跌停家数 ")
    max_lianban = models.FloatField(default=0, help_text="连板数 ")
    date_as = models.DateField()

    class Meta:
        db_table = "mc_dapan"
        # abstract = True

    def __str__(self):
        return json.dumps(vars(self), ensure_ascii=False)

