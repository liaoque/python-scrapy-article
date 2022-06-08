from django.db import models

from .shares_name import SharesName
# Create your models here.


class SharesMembers(models.Model):
    code = models.ForeignKey(SharesName, name='code', on_delete=models.CASCADE)
    members  = models.IntegerField(default=0, help_text="股东人数")
    avg_free_shares  = models.IntegerField(default=0, help_text="人均流通股(股)")
    date_as = models.DateField()
    info = models.CharField(max_length=255)
    price = models.IntegerField(default=0, help_text="股价")

    class Meta:
        db_table = "mc_stock_members"
        # abstract = True

    def __str__(self):
        return self.code + ":" + self.members + ":"  + self.date_as

    class SkillType():
        kdj = 1

        class AccountType():
            intersection_pre = 1
            intersection_today = 2
            turn_tomorrow = 3

