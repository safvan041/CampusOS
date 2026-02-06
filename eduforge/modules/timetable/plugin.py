"""
Timetable Module Plugin Configuration
"""

PLUGIN_NAME = "Timetable"
SLUG = "timetable"
DESCRIPTION = "Class schedules and timetable management"
VERSION = "1.0.0"
ICON = "🕐"  # Can also be a CSS class or icon identifier
COLOR = "cyan"  # For styling the module card

# Define default role permissions for this module
DEFAULT_PERMISSIONS = {
    'Principal': {'can_view': True, 'can_edit': True, 'can_manage': True},
    'Teacher': {'can_view': True, 'can_edit': True, 'can_manage': False},
    'Staff': {'can_view': True, 'can_edit': False, 'can_manage': False},
    'Student': {'can_view': True, 'can_edit': False, 'can_manage': False},
}
