from django.urls import path

from dvadmin.wb.views.views import IndexView
from dvadmin.wb.views.yuan_yin import YuanYinView
from dvadmin.wb.views.result import ResultView
from dvadmin.wb.views.reset import ResetView
from dvadmin.wb.views.lian_zhang_gu_piao import LianZhangGuPiao
from dvadmin.wb.views.lian_zhang_gai_nian import LianZhangGiNian
from dvadmin.wb.views.config import Config

urlpatterns = [
    path('', IndexView.as_view()),
    path('yuan_yin', YuanYinView.as_view()),
    path('result', ResultView.as_view()),
    path('reset', ResetView.as_view()),
    path('lian_zhang_gu_piao', LianZhangGuPiao.as_view()),
    path('lian_zhang_gai_nian', LianZhangGiNian.as_view()),
    path('config', Config.as_view()),
]
