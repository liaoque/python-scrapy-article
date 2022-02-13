from django.db import models


# Create your models here.


class FutruesJoinShares(models.Model):
    code = models.CharField(max_length=20,  help_text="股票编码")
    futrues_id = models.CharField(max_length=20,  help_text="futrues_hot_id")


    class Meta:
        db_table = "mc_futrues_join_shares"
        # abstract = True

    def __str__(self):
        return self.name

