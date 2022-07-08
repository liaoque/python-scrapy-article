from django.db import models

from .shares_name import SharesName
# Create your models here.

# 指数和国债
class StockIndex(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    val  = models.FloatField(default=0, help_text="价值")
    pe  = models.FloatField(default=0, help_text="市盈率 ")
    pb  = models.FloatField(default=0, help_text="市净率 ")
    date_as = models.DateField()

    class Meta:
        db_table = "mc_stock_index"
        # abstract = True

    def __str__(self):
        return str(self.code_id) + ":" + str(self.price) + ":"  + str(self.pe)


