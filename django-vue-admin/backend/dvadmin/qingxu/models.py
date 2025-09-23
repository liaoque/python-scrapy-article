# apps/ext_models/models.py
from django.db import models

class MCls(models.Model):
    id = models.AutoField(primary_key=True)
    tid = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    type = models.IntegerField(null=True, blank=True)
    commited = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'm_cls'
        managed = False   # 关键：不让 Django 管理(建表/迁移)
