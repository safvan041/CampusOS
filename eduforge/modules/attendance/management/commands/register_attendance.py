"""
Management command to register and install the attendance module.
"""
from django.core.management.base import BaseCommand
from core.plugins.models import Module, TenantModule, ModulePermission
from core.tenants.models import Tenant
from core.users.models import Role


class Command(BaseCommand):
    help = 'Register and install the attendance module for all tenants'

    def handle(self, *args, **options):
        # Create or update the Module
        module, created = Module.objects.update_or_create(
            slug='attendance',
            defaults={
                'name': 'Attendance',
                'description': 'Track student attendance and generate reports',
                'version': '1.0.0',
                'is_active': True,
                'icon': '📋',
                'color': 'blue',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created module: {module.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Updated module: {module.name}'))
        
        # Install for all tenants
        tenants = Tenant.objects.all()
        for tenant in tenants:
            tenant_module, created = TenantModule.objects.get_or_create(
                tenant=tenant,
                module=module,
                defaults={'is_installed': True}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Installed for tenant: {tenant.school_name}'))
            else:
                if not tenant_module.is_installed:
                    tenant_module.reinstall()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Reinstalled for tenant: {tenant.school_name}'))
                else:
                    self.stdout.write(f'  - Already installed for tenant: {tenant.school_name}')
            
            # Ensure permissions exist
            ModulePermission.ensure_default_permissions(tenant, module)
            self.stdout.write(f'  ✓ Permissions configured for: {tenant.school_name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Attendance module registration complete!'))
