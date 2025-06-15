from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('classic/', views.classic_mode, name='classic_mode'),
    path('cs/', views.cs_mode, name='cs_mode'),
    path('cs/play/', views.cs_play, name='cs_play'),
]