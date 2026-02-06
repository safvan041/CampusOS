"""
User models for eduforge.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Role(models.Model):
    """
    Role model for tenant-specific roles.
    """
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        unique_together = ('tenant', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.tenant.school_name})"

    @staticmethod
    def create_default_roles(tenant):
        """
        Create default roles for a tenant.
        """
        default_roles = [
            ('Principal', 'School principal with full access.'),
            ('Teacher', 'Teacher with teaching responsibilities.'),
            ('Staff', 'Non-teaching staff member.'),
            ('Student', 'Student user with limited access.'),
        ]

        created_roles = {}
        for role_name, description in default_roles:
            role, _ = Role.objects.get_or_create(
                tenant=tenant,
                name=role_name,
                defaults={
                    'description': description,
                    'is_system_role': True,
                }
            )
            created_roles[role_name] = role

        return created_roles


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Multi-tenant aware with role-based access.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    phone_number = models.CharField(max_length=20, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    profile_image = models.ImageField(upload_to='profile_images/%Y/%m/', blank=True, null=True)
    
    # For students
    student_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # For parents
    parent_code = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        unique_together = ('email', 'tenant')  # Email unique per tenant

    def __str__(self):
        role_name = self.role.name if self.role else 'No Role'
        return f"{self.get_full_name() or self.username} ({role_name})"

    def is_admin_user(self):
        """Check if user is admin or super admin."""
        return bool(self.role and self.role.name == 'Principal')

    def save(self, *args, **kwargs):
        if self.tenant and self.role is None:
            default_role = Role.objects.filter(tenant=self.tenant, name='Student').first()
            if default_role:
                self.role = default_role
        super().save(*args, **kwargs)
