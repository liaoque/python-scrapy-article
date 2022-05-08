from django.db import models


# Create your models here.


class SharesMember(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    members  = models.IntegerField(default=0, help_text="股东人数")
    date_as = models.DateField()
    info = models.CharField(max_length=255)
    price = models.IntegerField(default=0, help_text="股价")

    class Meta:
        db_table = "mc_stock_members"
        # abstract = True

    def __str__(self):
        return self.name

    class SkillType():
        kdj = 1

        class AccountType():
            intersection_pre = 1
            intersection_today = 2
            turn_tomorrow = 3

