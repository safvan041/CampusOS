"""
Plugins app configuration.
"""
from django.apps import AppConfig


class PluginsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.plugins'
    verbose_name = 'Plugins'
