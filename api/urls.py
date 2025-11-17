from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    WaterUnitViewSet, WaterQualityViewSet, MaintenanceViewSet,
    register, LoginMaintainerView, logout, csrf, user_info
)

router = DefaultRouter()
router.register('water-unit', WaterUnitViewSet, basename='water-unit')
router.register('water-quality', WaterQualityViewSet, basename='water-quality')
router.register('maintenance', MaintenanceViewSet, basename='maintenance')
    
urlpatterns = [
    path('register/', register, name="register"),  
    path('login/', LoginMaintainerView.as_view(), name="login"),  
    path('logout/', logout, name="logout"),  
    path('', include(router.urls)),
    path('csrf/', csrf, name="csrf"),
    path('user/', user_info, name="user_info"),
]

