from django.apps import AppConfig

class QingXuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dvadmin.qingxu'     # ← 模块路径
    label = 'qingxu'         # ← app_label，和 settings 里的 key 对齐
