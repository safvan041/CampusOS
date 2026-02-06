"""
Plugin/Module models for dynamic module registry system.
"""
from django.db import models
from django.utils import timezone
from core.tenants.models import Tenant
from core.users.models import Role
from django.conf import settings
import importlib.util
from pathlib import Path


class Module(models.Model):
    """
    System-level available modules.
    Represents all modules that exist in the codebase.
    """
    name = models.CharField(max_length=100, help_text="Display name of the module")
    slug = models.SlugField(max_length=50, unique=True, help_text="Unique identifier for the module")
    description = models.TextField(blank=True, help_text="Description of what this module does")
    version = models.CharField(max_length=20, default="1.0.0", help_text="Module version")
    is_active = models.BooleanField(default=True, help_text="Whether this module is available for installation")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier or emoji")
    color = models.CharField(max_length=20, blank=True, help_text="Color theme for the module card")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.slug})"


class TenantModule(models.Model):
    """
    Tenant-level installed modules.
    Tracks which modules are installed for each tenant.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='installed_modules')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='tenant_installations')
    is_installed = models.BooleanField(default=True, help_text="Whether the module is currently installed")
    installed_at = models.DateTimeField(default=timezone.now, help_text="When the module was installed")
    uninstalled_at = models.DateTimeField(null=True, blank=True, help_text="When the module was uninstalled")
    
    # Configuration (can store module-specific settings as JSON)
    config = models.JSONField(default=dict, blank=True, help_text="Module-specific configuration")

    class Meta:
        verbose_name = 'Tenant Module'
        verbose_name_plural = 'Tenant Modules'
        unique_together = [['tenant', 'module']]
        ordering = ['installed_at']

    def __str__(self):
        return f"{self.tenant.school_name} - {self.module.name}"

    def uninstall(self):
        """Mark the module as uninstalled."""
        self.is_installed = False
        self.uninstalled_at = timezone.now()
        self.save()

    def reinstall(self):
        """Reinstall a previously uninstalled module."""
        self.is_installed = True
        self.uninstalled_at = None
        self.save()


class ModulePermission(models.Model):
    """
    Role-based permissions for modules.
    """
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='permissions')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='module_permissions')
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_manage = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Module Permission'
        verbose_name_plural = 'Module Permissions'
        unique_together = ('module', 'role')
        ordering = ['module', 'role']

    def __str__(self):
        return f"{self.module.name} - {self.role.name}"

    @staticmethod
    def _load_plugin_defaults(module):
        """
        Load DEFAULT_PERMISSIONS from a module's plugin.py if available.
        """
        plugin_file = Path(settings.BASE_DIR) / 'modules' / module.slug / 'plugin.py'
        if not plugin_file.exists():
            return None

        try:
            spec = importlib.util.spec_from_file_location(
                f"modules.{module.slug}.plugin",
                plugin_file
            )
            if not spec or not spec.loader:
                return None

            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            return getattr(plugin_module, 'DEFAULT_PERMISSIONS', None)
        except Exception:
            return None

    @staticmethod
    def ensure_default_permissions(tenant, module):
        """
        Ensure default permissions exist for all roles in a tenant for a module.
        """
        legacy_defaults = {
            'Principal': {'can_view': True, 'can_edit': True, 'can_manage': True},
            'Teacher': {'can_view': True, 'can_edit': True, 'can_manage': False},
            'Staff': {'can_view': True, 'can_edit': False, 'can_manage': False},
            'Student': {'can_view': True, 'can_edit': False, 'can_manage': False},
        }

        plugin_defaults = ModulePermission._load_plugin_defaults(module)
        default_permissions = plugin_defaults or legacy_defaults

        for role in Role.objects.filter(tenant=tenant):
            perms = default_permissions.get(role.name, {'can_view': False, 'can_edit': False, 'can_manage': False})
            permission, created = ModulePermission.objects.get_or_create(
                module=module,
                role=role,
                defaults=perms,
            )
            if created:
                continue

            legacy = legacy_defaults.get(role.name, {'can_view': False, 'can_edit': False, 'can_manage': False})
            is_legacy = (
                permission.can_view == legacy['can_view']
                and permission.can_edit == legacy['can_edit']
                and permission.can_manage == legacy['can_manage']
            )
            if is_legacy and legacy != perms:
                permission.can_view = perms['can_view']
                permission.can_edit = perms['can_edit']
                permission.can_manage = perms['can_manage']
                permission.save(update_fields=['can_view', 'can_edit', 'can_manage'])
