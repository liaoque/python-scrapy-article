from django.db import models
from datetime import datetime
from shares.model.dapan import DaPan as DaPanModels


# Create your models here.
# Create your models here.


class DaPan(DaPanModels):
    class Meta:
        proxy = True
