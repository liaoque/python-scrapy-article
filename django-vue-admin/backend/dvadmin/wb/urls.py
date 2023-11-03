from django.urls import path

from dvadmin.wb.views.views import IndexView
from dvadmin.wb.views.yuan_yin import YuanYinView
from dvadmin.wb.views.result import ResultView
from dvadmin.wb.views.reset import ResetView

urlpatterns = [
    path('', IndexView.as_view()),
    path('yuan_yin', YuanYinView.as_view()),
    path('result', ResultView.as_view()),
    path('reset', ResetView.as_view()),
]
