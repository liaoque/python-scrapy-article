from django.db import models
from datetime import datetime
from shares.model.dapan import Dapan as DapanModels


# Create your models here.
# Create your models here.


class Dapan(DapanModels):
    class Meta:
        proxy = True
