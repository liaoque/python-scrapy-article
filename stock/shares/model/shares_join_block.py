from django.db import models

from .shares_name import SharesName
# Create your models here.


class SharesJoinBlock(models.Model):
    block_code = models.ForeignKey(SharesName, related_name='block_code_id', on_delete=models.CASCADE)
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)

    class Meta:
        db_table = "mc_shares_join_block"
        # abstract = True

    def __str__(self):
        return self.block_code + "----" + self.code


