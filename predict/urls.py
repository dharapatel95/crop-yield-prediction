from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('logout/', views.user_logout, name='logout'),

    path('history/', views.history, name='historxy'),
    path('help/', views.help_page, name='help'),

    path('hybrid-weather/', views.get_hybrid_weather, name='hybrid_weather'),
    path('harvest-planner/', views.harvest_planner, name='harvest_planner'),
]