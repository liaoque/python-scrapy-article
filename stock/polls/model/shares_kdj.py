from django.db import models
from .shares_name import SharesName
from shares.model.shares_kdj import SharesKdj as SharesKdjModels
# Create your models here.


# Create your models here.


class SharesKdj(SharesKdjModels):
    class Meta:
        proxy = True

    def __str__(self):
        return self.name
