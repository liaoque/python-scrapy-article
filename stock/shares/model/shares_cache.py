from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesCache(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    cache = models.TextField(default=0, help_text='缓存')
    created_at = models.DateTimeField()

    class Meta:
        db_table = "mc_shares_cache"
        # abstract = True

    def __str__(self):
        return self.title + ':' + self.context
