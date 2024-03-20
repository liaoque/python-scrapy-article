from django.urls import path

from .view.index_view import *
from .view.shares import *
from .view.jj import *
from .view.dapan import *
from .view.stro_date import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<int:pk>/', DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', vote, name='vote'),

    path('date/<str:date_today>', shares_date, name='date'),
    path('jj/<str:code>', jj_data, name='jj'),
    path('da_pan', da_pan, name='da_pan'),
    path('date/stor/save', stro_date, name='stro_date')

    # path('shares/', SharesView.as_view(), name='index'),
    # path('mzq/shares/<str:pk>/', SharesView.as_view(), name='shares_name_view'),

    # path('', views.index, name='index'),
    #
    # # 例如: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    #
    # # 例如: /polls/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    #
    # # 例如: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]


