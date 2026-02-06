"""
Timetable app configuration.
"""
from django.apps import AppConfig


class TimetableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.timetable'
    verbose_name = 'Timetable'
