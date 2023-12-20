from django.db import models

from .shares_name import SharesName
# Create your models here.


class SharesJoinBlock(models.Model):
    block_code = models.ForeignKey(SharesName, related_name='block_code_id', on_delete=models.CASCADE)
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    code_type = models.IntegerField(default=1, help_text="1.东方，2.同花顺")

    class Meta:
        db_table = "mc_shares_join_block"
        # abstract = True

    def __str__(self):
        return self.block_code_id + "----" + self.code_id


