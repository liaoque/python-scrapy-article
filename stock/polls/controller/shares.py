from django.contrib import admin

from ..model.shares_name import SharesName


class SharesNameAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ('code', 'name')