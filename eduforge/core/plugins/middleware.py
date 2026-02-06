"""
Middleware to check if a tenant has access to a module.
"""
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from core.plugins.models import Module, TenantModule


class TenantModuleAccessMiddleware:
    """
    Middleware to ensure tenants can only access modules they have installed.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define module paths that need access control
        self.module_paths = ['attendance', 'payroll', 'timetable']
    
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
        
        # Skip if no tenant (shouldn't happen but be safe)
        if not hasattr(request.user, 'tenant') or not request.user.tenant:
            return None
        
        # Get the current URL namespace
        try:
            resolved = resolve(request.path)
            namespace = resolved.namespace
        except:
            return None
        
        # Check if this is a module path
        if namespace in self.module_paths:
            tenant = request.user.tenant
            
            # Check if module is installed for this tenant
            try:
                module = Module.objects.get(slug=namespace, is_active=True)
                tenant_module = TenantModule.objects.get(
                    tenant=tenant,
                    module=module,
                    is_installed=True
                )
            except (Module.DoesNotExist, TenantModule.DoesNotExist):
                # Module not installed for this tenant
                messages.error(
                    request,
                    f'The {namespace.title()} module is not installed. Please install it from the dashboard.'
                )
                return redirect('auth:dashboard')
        
        return None
