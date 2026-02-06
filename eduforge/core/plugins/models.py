"""
Plugin/Module models for dynamic module registry system.
"""
from django.db import models
from django.utils import timezone
from core.tenants.models import Tenant


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
