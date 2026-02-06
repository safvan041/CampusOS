"""
Admin configuration for core users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser.
    """
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'tenant', 'is_staff')
    list_filter = ('tenant', 'role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Tenant Info', {'fields': ('tenant', 'role')}),
        ('Profile', {'fields': ('phone_number', 'profile_image', 'student_id', 'parent_code')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tenant Info', {'fields': ('tenant', 'role')}),
        ('Profile', {'fields': ('phone_number', 'student_id')}),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Role.
    """
    list_display = ('name', 'tenant', 'is_system_role')
    list_filter = ('tenant', 'is_system_role')
    search_fields = ('name',)
