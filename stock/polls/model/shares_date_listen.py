from django.db import models
from shares.model.shares_date_listen import SharesDateListen as SharesDateListenModels


# Create your models here.


class SharesDateListen(SharesDateListenModels):
    class Meta:
        proxy = True
