"""
Attendance module URL configuration.
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.index, name='index'),
    path('select-class/', views.select_class, name='select_class'),
    path('mark/<str:class_id>/', views.mark_attendance, name='mark_attendance'),
    path('edit/<uuid:class_id>/', views.edit_attendance, name='edit_attendance'),
    path('student/<uuid:student_id>/', views.student_summary, name='student_summary'),
    path('student/', views.student_summary, name='my_attendance'),
    path('reports/', views.class_report, name='class_report'),
    path('reports/<uuid:class_id>/', views.class_report, name='class_report_detail'),
    path('export/<uuid:class_id>/', views.export_report_csv, name='export_csv'),
]
