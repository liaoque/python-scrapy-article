from django.db import models

from shares.model.shares_name import SharesName as SharesNameModels
# Create your models here.


class SharesName(SharesNameModels):

    def __str__(self):
        return self.name
