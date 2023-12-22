from django.db import models
from shares.model.shares_date import SharesDate as SharesDateModels


# Create your models here.


class SharesDate(SharesDateModels):
    class Meta:
        proxy = True

    def __str__(self):
        return self.date_as
