from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesDate(models.Model):
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_date"

    def __str__(self):
        return self.date_as
