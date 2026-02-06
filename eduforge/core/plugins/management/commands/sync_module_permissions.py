"""
Management command to sync module permissions from plugin.py across all tenants.
"""
from django.core.management.base import BaseCommand
from core.plugins.models import Module, ModulePermission
from core.tenants.models import Tenant
from core.users.models import Role


class Command(BaseCommand):
    help = 'Sync module permissions from plugin configurations across all tenants'

    def handle(self, *args, **options):
        tenants = Tenant.objects.all()
        modules = Module.objects.filter(is_active=True)

        total_updated = 0

        for tenant in tenants:
            for module in modules:
                plugin_defaults = ModulePermission._load_plugin_defaults(module)
                if not plugin_defaults:
                    continue

                for role in Role.objects.filter(tenant=tenant):
                    perms = plugin_defaults.get(
                        role.name,
                        {'can_view': False, 'can_edit': False, 'can_manage': False}
                    )

                    permission, created = ModulePermission.objects.get_or_create(
                        module=module,
                        role=role,
                        defaults=perms,
                    )

                    if not created:
                        # Force update to match plugin defaults
                        if (permission.can_view != perms['can_view'] or
                            permission.can_edit != perms['can_edit'] or
                            permission.can_manage != perms['can_manage']):
                            
                            permission.can_view = perms['can_view']
                            permission.can_edit = perms['can_edit']
                            permission.can_manage = perms['can_manage']
                            permission.save(update_fields=['can_view', 'can_edit', 'can_manage'])
                            total_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Synced permissions for {modules.count()} modules across {tenants.count()} tenants. '
                f'Updated {total_updated} permission records.'
            )
        )
