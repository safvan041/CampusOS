"""
Authentication views for landing, login, and registration.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse

from .forms import SchoolRegistrationForm, LoginForm
from .models import CustomUser
from core.tenants.models import Tenant, TenantSettings
from core.billing.models import Subscription, SubscriptionPlan


def landing(request):
    """
    Landing page - redirects to login if already authenticated.
    """
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    return render(request, 'auth/landing.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'auth:dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'show_register_link': True,
    }
    return render(request, 'auth/login.html', context)


@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    School registration view - Multi-step registration.
    """
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            try:
                admin_user = None
                with transaction.atomic():
                    # Create Tenant
                    tenant = Tenant.objects.create(
                        school_name=form.cleaned_data['school_name'],
                        subdomain=form.cleaned_data['subdomain'],
                        official_email=form.cleaned_data['official_email'],
                        alternate_email=form.cleaned_data.get('alternate_email', ''),
                        phone_number=form.cleaned_data['phone_number'],
                        alternate_phone=form.cleaned_data.get('alternate_phone', ''),
                        street_address=form.cleaned_data.get('street_address', ''),
                        city=form.cleaned_data['city'],
                        state=form.cleaned_data['state'],
                        postal_code=form.cleaned_data['postal_code'],
                        school_type=form.cleaned_data['school_type'],
                        student_count=form.cleaned_data['student_count'],
                        language_preference=form.cleaned_data['language_preference'],
                    )

                    # Create Tenant Settings
                    TenantSettings.objects.create(tenant=tenant)

                    # Create Admin User
                    admin_user = CustomUser.objects.create_user(
                        username=form.cleaned_data['admin_email'],
                        email=form.cleaned_data['admin_email'],
                        first_name=form.cleaned_data['admin_first_name'],
                        last_name=form.cleaned_data['admin_last_name'],
                        password=form.cleaned_data['admin_password'],
                        tenant=tenant,
                        role='super_admin',
                        is_staff=True,
                        is_superuser=False,  # Not a Django superuser
                    )

                    # Create Subscription
                    plan = form.cleaned_data['subscription_plan']
                    subscription = Subscription.objects.create(
                        tenant=tenant,
                        plan=plan,
                        billing_cycle=form.cleaned_data['billing_cycle'],
                        status='trial',
                    )

                # Auto-login the admin (OUTSIDE transaction to avoid session issues)
                if admin_user:
                    login(request, admin_user)
                    
                messages.success(
                    request, 
                    f'Welcome to CampusOS, {tenant.school_name}! Your account has been created successfully.'
                )
                return redirect('auth:dashboard')

            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return redirect('auth:register')
    else:
        form = SchoolRegistrationForm()
    
    context = {
        'form': form,
        'step': request.GET.get('step', 1),
    }
    return render(request, 'auth/register.html', context)


@require_http_methods(["GET"])
def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('auth:landing')


@login_required(login_url='auth:login')
def dashboard(request):
    """
    Dashboard - main application view after login.
    Shows dynamic module cards based on installed and available modules.
    """
    from core.plugins.models import Module, TenantModule
    
    tenant = request.user.tenant
    
    # Get all active modules
    available_modules = Module.objects.filter(is_active=True)
    
    # Get installed modules for this tenant
    installed_module_ids = TenantModule.objects.filter(
        tenant=tenant,
        is_installed=True
    ).values_list('module_id', flat=True)
    
    # Create a list of modules with installation status
    modules_data = []
    for module in available_modules:
        modules_data.append({
            'module': module,
            'is_installed': module.id in installed_module_ids,
        })
    
    return render(request, 'dashboard/index.html', {
        'tenant': tenant,
        'user': request.user,
        'modules': modules_data,
    })


def check_subdomain_availability(request):
    """
    AJAX endpoint to check if subdomain is available.
    """
    if request.method == 'GET':
        subdomain = request.GET.get('subdomain', '').lower()
        
        if not subdomain or len(subdomain) < 3:
            return JsonResponse({
                'available': False,
                'message': 'Subdomain must be at least 3 characters'
            })
        
        # Check if subdomain exists
        exists = Tenant.objects.filter(subdomain=subdomain).exists()
        
        return JsonResponse({
            'available': not exists,
            'message': 'Available!' if not exists else 'Already taken'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def check_email_availability(request):
    """
    AJAX endpoint to check if email is available for admin account.
    """
    if request.method == 'GET':
        email = request.GET.get('email', '').lower()
        
        if not email:
            return JsonResponse({
                'available': False,
                'message': 'Please enter an email'
            })
        
        # Check if email exists
        exists = CustomUser.objects.filter(email=email).exists()
        
        return JsonResponse({
            'available': not exists,
            'message': 'Available!' if not exists else 'Email already registered'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def install_module(request, module_slug):
    """
    Install a module for the current tenant.
    """
    from core.plugins.models import Module, TenantModule
    
    try:
        # Get the module
        module = Module.objects.get(slug=module_slug, is_active=True)
        tenant = request.user.tenant
        
        # Check if already installed
        tenant_module, created = TenantModule.objects.get_or_create(
            tenant=tenant,
            module=module,
            defaults={'is_installed': True}
        )
        
        if not created and not tenant_module.is_installed:
            # Reinstall if was previously uninstalled
            tenant_module.reinstall()
            messages.success(request, f'{module.name} has been reinstalled successfully!')
        elif created:
            messages.success(request, f'{module.name} has been installed and activated!')
        else:
            messages.info(request, f'{module.name} is already installed.')
        
        # Redirect to the module after installation
        return redirect(f'/{module_slug}/')
        
    except Module.DoesNotExist:
        messages.error(request, 'Module not found or not available.')
    except Exception as e:
        messages.error(request, f'Error installing module: {str(e)}')
    
    return redirect('auth:dashboard')


@login_required(login_url='auth:login')
@require_http_methods(["POST"])
def uninstall_module(request, module_slug):
    """
    Uninstall a module for the current tenant.
    """
    from core.plugins.models import Module, TenantModule
    
    try:
        module = Module.objects.get(slug=module_slug)
        tenant = request.user.tenant
        
        tenant_module = TenantModule.objects.get(
            tenant=tenant,
            module=module
        )
        
        tenant_module.uninstall()
        messages.success(request, f'{module.name} has been uninstalled successfully!')
        
    except Module.DoesNotExist:
        messages.error(request, 'Module not found.')
    except TenantModule.DoesNotExist:
        messages.error(request, 'Module is not installed.')
    except Exception as e:
        messages.error(request, f'Error uninstalling module: {str(e)}')
    
    return redirect('auth:dashboard')
