from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('calendar/', views.calendar_view, name='calendar'),
]
