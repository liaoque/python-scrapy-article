from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesKdj(models.Model):
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    k = models.FloatField(default=0)
    d = models.FloatField(default=0)
    j = models.FloatField(default=0)
    cycle_type = models.IntegerField(default=0, help_text='1.9,3,3')
    date_as = models.DateField()

    class Meta:
        db_table = "mc_shares_kdj"
        # abstract = True

    def __str__(self):
        return self.code_id + ":" + self.code.name + "j:" + str(self.j)
