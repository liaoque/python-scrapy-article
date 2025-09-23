# config/db_router.py
from django.conf import settings

class AppRouter:
    mapping = getattr(settings, "DATABASE_APPS_MAPPING", {})

    def db_for_read(self, model, **hints):
        return self.mapping.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return self.mapping.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        db_list = set(self.mapping.values())
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # 你的表已存在，不让 Django 迁移
        if app_label in self.mapping:
            return False
        return None
