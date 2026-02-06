"""
Attendance module URL configuration.
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('mark/', views.mark_attendance, name='mark'),
    path('reports/', views.view_reports, name='reports'),
]
