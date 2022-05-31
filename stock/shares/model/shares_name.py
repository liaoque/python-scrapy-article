from django.db import models


# Create your models here.


class SharesName(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=30)
    temper_tonghuashun = models.IntegerField(default=0)
    temper_dongfangcaifu = models.IntegerField(default=0)
    area_id = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    pb = models.IntegerField(default=0)
    pe = models.IntegerField(default=0)
    code_type = models.IntegerField(default=0, help_text="1股票，2行业板块")
    member_down = models.IntegerField(default=2, help_text="股东人数，1 下降，2 上升")
    macd_up = models.IntegerField(default=1, help_text="macd，1 下降，2 上升")
    finance_up = models.IntegerField(default=1, help_text="macd，1 下降，2 上升")

    class Meta:
        db_table = "mc_shares_name"
        # abstract = True

    def __str__(self):
        return self.name

    class SkillType():
        kdj = 1

        class AccountType():
            intersection_pre = 1
            intersection_today = 2
            turn_tomorrow = 3

