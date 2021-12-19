from django.urls import path

from .view.index_view import *

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('<int:pk>/', DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', vote, name='vote'),


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


