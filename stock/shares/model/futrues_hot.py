from django.db import models


# Create your models here.


class FutruesHot(models.Model):
    code = models.CharField(max_length=20,  help_text="同花顺热门商品编号")
    name = models.CharField(max_length=30,  help_text="名字")
    industry = models.CharField(max_length=30,  help_text="行业")
    today_zdf = models.FloatField(default=0,  help_text="今日涨幅")
    five_zdf = models.FloatField(default=0,  help_text="5日涨幅")
    ten_zdf = models.FloatField(default=0, help_text="10日涨幅")
    twenty_zdf = models.FloatField(default=0, help_text="20日涨幅")
    sixty_zdf = models.FloatField(default=0, help_text="60日涨幅")

    class Meta:
        db_table = "mc_futrues_hot"
        # abstract = True

    def __str__(self):
        return self.name

