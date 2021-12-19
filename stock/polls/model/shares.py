from django.db import models
from datetime import datetime
from shares.model.shares import Shares as SharesModels
# Create your models here.
# Create your models here.


class Shares(SharesModels):
    class Meta:
        proxy = True

    def __str__(self):
        return self.name + ":" + datetime.strftime(self.date_as,'%Y-%m-%d')
