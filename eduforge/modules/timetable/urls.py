from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('section/<int:section_id>/', views.section_timetable, name='section_timetable'),
    path('manage/<int:section_id>/', views.manage_timetable, name='manage_timetable'),
    path('slots/', views.manage_time_slots, name='manage_time_slots'),
    path('slots/<int:slot_id>/delete/', views.delete_time_slot, name='delete_time_slot'),
]
