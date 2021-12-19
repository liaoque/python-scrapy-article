from django.contrib import admin

from ..model.shares_name import SharesName


class SharesNameAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')