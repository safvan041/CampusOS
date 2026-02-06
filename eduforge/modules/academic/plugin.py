"""
Academic Setup Module Plugin Configuration
"""

PLUGIN_NAME = "Academic Setup"
SLUG = "academic"
DESCRIPTION = "Manage academic sessions, classes, sections, and student enrollment"
VERSION = "1.0.0"
ICON = "🎓"
COLOR = "purple"

# Define default role permissions for this module
DEFAULT_PERMISSIONS = {
    'Principal': {'can_view': True, 'can_edit': True, 'can_manage': True},
    'Teacher': {'can_view': False, 'can_edit': False, 'can_manage': False},
    'Staff': {'can_view': False, 'can_edit': False, 'can_manage': False},
    'Student': {'can_view': False, 'can_edit': False, 'can_manage': False},
}
