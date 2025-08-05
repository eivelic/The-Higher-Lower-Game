from django.urls import path
from . import views

urlpatterns = [
    path('nickname/', views.nickname_input, name='nickname_input'),
    path('', views.homepage, name='homepage'),
    path('classic/', views.classic_mode, name='classic_mode'),
    path('cs/', views.cs_mode, name='cs_mode'),
    path('cs/play/', views.cs_play, name='cs_play'),
    path('leaderboard/classic/', views.classic_leaderboard, name='classic_leaderboard'),
    path('leaderboard/cs/', views.cs_leaderboard, name='cs_leaderboard'),
    path('nickname/reset/', views.reset_nickname, name='reset_nickname'),
]
