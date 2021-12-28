from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesKdjComputeDetail(models.Model):
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    buy_amount = models.FloatField(default=0, help_text='买点')
    buy_date_as = models.FloatField(default=0, help_text='买点日期')
    buy_amount_end = models.FloatField(default=0, help_text='买点结束')
    buy_date_as_end = models.FloatField(default=0, help_text='买点结束日期')
    shill_type = models.IntegerField(default=0, help_text='技术指标：1.kdj')
    # shill_type=1
    #   account_type: 1. 交点前一天, 2. 交点. 3.拐点
    shill_account_type = models.IntegerField(default=0, help_text='具体参考代码注释')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_compute_detail"
        # abstract = True

    def __str__(self):
        return self.code

    def saveSharesKdjComputeDetail(code, buy_amount, buy_date_as, buy_amount_end, buy_date_as_end, shill_type,
                                   shill_account_type, date_as):
        result = SharesKdjComputeDetail.objects.filter(code_id=code, date_as=date_as)
        if len(result):
            kdjComputeDetail = SharesKdjComputeDetail(id=result[0].id,
                                    code_id=code,
                                    buy_amount=buy_amount,
                                    buy_date_as=buy_date_as,
                                    buy_amount_end=buy_amount_end,
                                    buy_date_as_end=buy_date_as_end,
                                    shill_type=shill_type,
                                    shill_account_type=shill_account_type,
                                    date_as=date_as)
        else:
            kdjComputeDetail = SharesKdjComputeDetail(code_id=code,
                                    buy_amount=buy_amount,
                                    buy_date_as=buy_date_as,
                                    buy_amount_end=buy_amount_end,
                                    buy_date_as_end=buy_date_as_end,
                                    shill_type=shill_type,
                                    shill_account_type=shill_account_type,
                                    date_as=date_as)
        return kdjComputeDetail.save()
