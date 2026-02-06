"""
Tenant models for multi-tenancy support.
"""
from django.db import models
from django.utils import timezone
import uuid
import re


class Tenant(models.Model):
    """
    Tenant model representing a School/Organization.
    """
    SCHOOL_TYPE_CHOICES = [
        ('primary', 'Primary Only'),
        ('secondary', 'Secondary Only'),
        ('primary_secondary', 'Primary & Secondary'),
        ('higher_secondary', 'Higher Secondary Only'),
        ('coaching', 'Coaching Institute'),
        ('college', 'College'),
    ]

    STUDENT_COUNT_CHOICES = [
        ('<100', 'Less than 100'),
        ('100-300', '100-300'),
        ('300-600', '300-600'),
        ('600+', '600+'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('gu', 'Gujarati'),
        ('hi', 'Hindi'),
        ('other', 'Regional Language'),
    ]

    # Basic Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school_name = models.CharField(max_length=255)
    subdomain = models.SlugField(max_length=20, unique=True, help_text="3-20 lowercase characters, no spaces")
    portal_url = models.URLField(auto_created=True, editable=False, blank=True)

    # Contact Information
    official_email = models.EmailField()
    alternate_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True, null=True)

    # Address
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    # Profile
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES)
    student_count = models.CharField(max_length=10, choices=STUDENT_COUNT_CHOICES)
    language_preference = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')

    # System Generated Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trial_expiry_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.school_name} ({self.subdomain})"

    def save(self, *args, **kwargs):
        """Auto-generate portal URL and validate subdomain."""
        if not self.portal_url:
            self.portal_url = f"https://{self.subdomain}.campusos.test"
        
        # Validate subdomain
        if not self.validate_subdomain_format(self.subdomain):
            raise ValueError("Subdomain must be 3-20 lowercase characters, no spaces")
        
        super().save(*args, **kwargs)

    @staticmethod
    def validate_subdomain_format(subdomain):
        """Validate subdomain format."""
        pattern = r'^[a-z0-9]{3,20}$'
        return re.match(pattern, subdomain) is not None


class TenantSettings(models.Model):
    """
    Additional settings for each tenant.
    """
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='settings')
    
    # Feature toggles
    attendance_enabled = models.BooleanField(default=True)
    payroll_enabled = models.BooleanField(default=True)
    timetable_enabled = models.BooleanField(default=True)
    
    # Customization
    theme_color = models.CharField(max_length=7, default='#1f2937')
    logo = models.ImageField(upload_to='tenant_logos/%Y/%m/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tenant Settings'
        verbose_name_plural = 'Tenant Settings'

    def __str__(self):
        return f"Settings for {self.tenant.school_name}"
