from django.db import models

from .shares_name import SharesName
# Create your models here.


class SharesIndustry(models.Model):
    industry_code = models.ForeignKey(SharesName, related_name='industry_code_id', on_delete=models.CASCADE)
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)

    class Meta:
        db_table = "mc_shares_industry"
        # abstract = True

    def __str__(self):
        return self.industry_code_id + "----" + self.code


