from django.db import models
from .shares_name import SharesName


# Create your models here.


class SharesCache(models.Model):
    title = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    cache = models.TextField(default=0, help_text='缓存')
    created_at = models.DateTimeField()

    class Meta:
        db_table = "mc_shares_cache"
        # abstract = True

    def __str__(self):
        return self.title + ':' + self.context
