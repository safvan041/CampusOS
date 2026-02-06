"""
Admin configuration for plugins app.
"""
from django.contrib import admin
from .models import Module, TenantModule


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TenantModule)
class TenantModuleAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'module', 'is_installed', 'installed_at']
    list_filter = ['is_installed', 'module', 'installed_at']
    search_fields = ['tenant__school_name', 'module__name']
    readonly_fields = ['installed_at', 'uninstalled_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('tenant', 'module')
