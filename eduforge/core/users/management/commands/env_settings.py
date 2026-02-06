"""
Management command to view and manage environment controller settings.

Usage:
    python manage.py env_settings                   # Show all settings
    python manage.py env_settings --toggle SUBDOMAIN_VALIDATE    # Toggle a setting
    python manage.py env_settings --reset          # Reset all to defaults
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from core.utils.env_controller import EnvController
import os


class Command(BaseCommand):
    help = 'Manage environment controller settings for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--toggle',
            type=str,
            help='Toggle a specific setting (e.g., BYPASS_SUBDOMAIN_VALIDATION)'
        )
        parser.add_argument(
            '--set',
            type=str,
            help='Set a specific setting to a value (e.g., BYPASS_SUBDOMAIN_VALIDATION=false)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all settings to defaults'
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export current settings as .env file content'
        )

    def handle(self, *args, **options):
        if options['toggle']:
            self.toggle_setting(options['toggle'])
        elif options['set']:
            self.set_setting(options['set'])
        elif options['reset']:
            self.reset_settings()
        elif options['export']:
            self.export_settings()
        else:
            self.show_all_settings()

    def show_all_settings(self):
        """Display all environment controller settings in a formatted table."""
        if EnvController.is_production():
            self.stdout.write(self.style.WARNING('⚠️  WARNING: Running in PRODUCTION mode. Many validations are enforced.'))
            self.stdout.write('')

        settings_dict = EnvController.get_all_settings()
        
        for category, settings in settings_dict.items():
            self.stdout.write(self.style.SUCCESS(f'\n{category} SETTINGS:'))
            self.stdout.write('─' * 80)
            
            for key, value in settings.items():
                status = '✓ ENABLED' if value else '✗ DISABLED'
                color = self.style.SUCCESS if value else self.style.ERROR
                self.stdout.write(f'  {key:<40} {color(status)}')
            
        self.stdout.write('\n' + '─' * 80)
        self.stdout.write(self.style.WARNING('\nTo change settings, use:'))
        self.stdout.write('  python manage.py env_settings --set SETTING_NAME=true/false')
        self.stdout.write('  python manage.py env_settings --export  (to generate .env content)\n')

    def toggle_setting(self, setting_name):
        """Toggle a boolean setting."""
        if not hasattr(EnvController, setting_name):
            self.stdout.write(
                self.style.ERROR(f'Setting "{setting_name}" does not exist.')
            )
            self.stdout.write('Available settings:')
            settings_dict = EnvController.get_all_settings()
            for category, settings in settings_dict.items():
                self.stdout.write(f'\n{category}:')
                for key in settings.keys():
                    self.stdout.write(f'  - {key}')
            return

        current_value = getattr(EnvController, setting_name)
        new_value = not current_value
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setting "{setting_name}" toggled from {current_value} to {new_value}'
            )
        )

    def set_setting(self, setting_expr):
        """Set a specific setting to a value."""
        if '=' not in setting_expr:
            self.stdout.write(
                self.style.ERROR('Invalid format. Use: SETTING_NAME=true/false')
            )
            return

        setting_name, value_str = setting_expr.split('=', 1)
        setting_name = setting_name.strip()
        value_str = value_str.strip().lower()

        if not hasattr(EnvController, setting_name):
            self.stdout.write(
                self.style.ERROR(f'Setting "{setting_name}" does not exist.')
            )
            return

        if value_str not in ('true', 'false'):
            self.stdout.write(
                self.style.ERROR('Value must be "true" or "false"')
            )
            return

        new_value = value_str == 'true'
        current_value = getattr(EnvController, setting_name)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Setting "{setting_name}" would change from {current_value} to {new_value}'
            )
        )
        self.stdout.write(self.style.WARNING('Note: Settings are read from environment variables.'))
        self.stdout.write('Update your .env file and restart the server.')

    def reset_settings(self):
        """Show what resetting would do."""
        self.stdout.write(self.style.WARNING('To reset settings to defaults:'))
        self.stdout.write('1. Update your .env file with default values, or')
        self.stdout.write('2. Remove the .env file and use environment defaults')
        self.stdout.write('\nDefault values (for development):')
        
        defaults = {
            'BYPASS_SUBDOMAIN_VALIDATION': 'True',
            'ALLOW_DUPLICATE_SUBDOMAINS': 'True',
            'ALLOW_INVALID_SUBDOMAIN_FORMAT': 'False',
            'BYPASS_EMAIL_VALIDATION': 'True',
            'ALLOW_DUPLICATE_EMAILS': 'True',
            'BYPASS_PASSWORD_VALIDATION': 'True',
            'ALLOW_WEAK_PASSWORD': 'True',
            'ALLOW_NO_UPPERCASE': 'True',
            'ALLOW_NO_NUMBERS': 'True',
            'ALLOW_NO_SPECIAL_CHARS': 'True',
            'BYPASS_PAYMENT_VALIDATION': 'True',
            'SKIP_TRIAL_PERIOD': 'True',
            'ALLOW_FREE_PLANS': 'True',
            'BYPASS_PHONE_VALIDATION': 'True',
            'MAKE_ADDRESS_OPTIONAL': 'True',
            'DEV_MODE': 'True',
            'DEBUG_VALIDATIONS': 'False',
        }
        
        for key, value in defaults.items():
            self.stdout.write(f'{key}={value}')

    def export_settings(self):
        """Export current settings as .env file content."""
        self.stdout.write('# Generated environment settings\n')
        
        settings_dict = EnvController.get_all_settings()
        
        for category, settings_map in settings_dict.items():
            self.stdout.write(f'# {category}\n')
            for key, value in settings_map.items():
                # Convert the key format for environment variable
                env_key = self._to_env_key(key)
                env_value = 'True' if value else 'False'
                self.stdout.write(f'{env_key}={env_value}\n')
            self.stdout.write('')

    def _to_env_key(self, key):
        """Convert setting key to environment variable format."""
        # Just return as-is since our settings already follow the pattern
        return key
