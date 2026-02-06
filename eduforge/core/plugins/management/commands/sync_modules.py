"""
Django management command to discover and sync modules.
Usage: python manage.py sync_modules
"""
from django.core.management.base import BaseCommand
from core.plugins.loader import module_loader


class Command(BaseCommand):
    help = 'Discover and synchronize modules from the modules/ directory'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting module discovery...'))
        
        try:
            synced_count = module_loader.sync_to_database()
            
            if synced_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully synced {synced_count} module(s)')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No modules found to sync')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing modules: {e}')
            )
            raise
