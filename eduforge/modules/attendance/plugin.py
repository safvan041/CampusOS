"""
Attendance Module Plugin Configuration
"""

PLUGIN_NAME = "Attendance"
SLUG = "attendance"
DESCRIPTION = "Track student attendance and generate reports"
VERSION = "1.0.0"
ICON = "📋"  # Can also be a CSS class or icon identifier
COLOR = "blue"  # For styling the module card

# Define default role permissions for this module
DEFAULT_PERMISSIONS = {
    'Principal': {'can_view': True, 'can_edit': True, 'can_manage': True},
    'Teacher': {'can_view': True, 'can_edit': True, 'can_manage': False},
    'Staff': {'can_view': True, 'can_edit': False, 'can_manage': False},
    'Student': {'can_view': True, 'can_edit': False, 'can_manage': False},
}
