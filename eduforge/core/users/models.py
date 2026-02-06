"""
User models for eduforge.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Multi-tenant aware with role-based access.
    """
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
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
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def is_admin_user(self):
        """Check if user is admin or super admin."""
        return self.role in ['super_admin', 'admin']
