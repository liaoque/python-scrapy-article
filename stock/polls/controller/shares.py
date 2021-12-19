from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from ..model.shares_name import SharesName


class SharesNameAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('code', 'name', )
    # 表单模版
    change_form_template = "shares/detail.html"

    class Meta():
        fields = ('name', 'code','shares' )

