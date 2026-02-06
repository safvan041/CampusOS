"""
Timetable module URL configuration.
"""
from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_timetable, name='create'),
    path('schedule/', views.view_schedule, name='schedule'),
]
