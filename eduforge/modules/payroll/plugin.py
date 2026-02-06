"""
Payroll Module Plugin Configuration
"""

PLUGIN_NAME = "Payroll"
SLUG = "payroll"
DESCRIPTION = "Manage salaries and employee payments"
VERSION = "1.0.0"
ICON = "💰"  # Can also be a CSS class or icon identifier
COLOR = "green"  # For styling the module card

# Define default role permissions for this module
# Payroll is sensitive - only Principal should have access
DEFAULT_PERMISSIONS = {
    'Principal': {'can_view': True, 'can_edit': True, 'can_manage': True},
    'Teacher': {'can_view': False, 'can_edit': False, 'can_manage': False},
    'Staff': {'can_view': False, 'can_edit': False, 'can_manage': False},
    'Student': {'can_view': False, 'can_edit': False, 'can_manage': False},
}
