"""
User authentication URL configuration.
"""
from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('permission-denied/', views.permission_denied, name='permission_denied'),

    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<uuid:user_id>/edit/', views.user_edit, name='user_edit'),
    
    # Module management
    path('modules/install/<slug:module_slug>/', views.install_module, name='install_module'),
    path('modules/uninstall/<slug:module_slug>/', views.uninstall_module, name='uninstall_module'),
    
    # AJAX endpoints
    path('api/check-subdomain/', views.check_subdomain_availability, name='check_subdomain'),
    path('api/check-email/', views.check_email_availability, name='check_email'),
]
