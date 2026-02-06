"""
Middleware to check if a tenant has access to a module.
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from core.plugins.models import Module, TenantModule, ModulePermission
from core.users.models import Role


class TenantModuleAccessMiddleware:
    """
    Middleware to ensure tenants can only access modules they have installed.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Check module access before view execution.
        """
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None

        # Allow superusers to bypass module permission checks
        if request.user.is_superuser:
            return None
        
        # Skip if no tenant (shouldn't happen but be safe)
        if not hasattr(request.user, 'tenant') or not request.user.tenant:
            return None
        
        # Get the current URL namespace
        try:
            resolved = resolve(request.path)
            namespace = resolved.namespace
        except:
            return None
        
        # Check if this is a module namespace
        if namespace and Module.objects.filter(slug=namespace, is_active=True).exists():
            tenant = request.user.tenant

            # Check if module exists and is installed for this tenant
            try:
                module = Module.objects.get(slug=namespace, is_active=True)
                TenantModule.objects.get(
                    tenant=tenant,
                    module=module,
                    is_installed=True
                )
            except (Module.DoesNotExist, TenantModule.DoesNotExist):
                messages.error(
                    request,
                    f'The {namespace.title()} module is not installed. Please install it from the dashboard.'
                )
                return redirect('auth:dashboard')

            # Ensure the user has a role
            if not request.user.role:
                fallback_name = 'Principal' if request.user.is_staff else 'Student'
                fallback_role = Role.objects.filter(tenant=tenant, name=fallback_name).first()
                if fallback_role:
                    request.user.role = fallback_role
                    request.user.save(update_fields=['role'])
                else:
                    return redirect('auth:permission_denied')

            permission = ModulePermission.objects.filter(module=module, role=request.user.role).first()
            if not permission:
                # Create defaults and retry
                ModulePermission.ensure_default_permissions(tenant, module)
                permission = ModulePermission.objects.filter(module=module, role=request.user.role).first()
            if not permission:
                return redirect('auth:permission_denied')

            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                if not permission.can_view:
                    return redirect('auth:permission_denied')
            else:
                if not permission.can_edit:
                    return redirect('auth:permission_denied')
        
        return None
