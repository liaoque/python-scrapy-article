# apps/ext_models/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MClsViewSet

router = DefaultRouter()
router.register(r'cls', MClsViewSet, basename='mcls')

urlpatterns = [
    path('', include(router.urls)),
]
