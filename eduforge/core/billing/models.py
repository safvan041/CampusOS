"""
Billing and subscription models.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid


class SubscriptionPlan(models.Model):
    """
    Predefined subscription plans.
    """
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)  # Basic, Standard, Premium
    description = models.TextField(blank=True)
    
    # Pricing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Features
    max_students = models.IntegerField()
    max_staff = models.IntegerField()
    max_classes = models.IntegerField()
    storage_gb = models.IntegerField()  # In GB
    api_calls_per_month = models.IntegerField()
    
    # Modules included
    attendance_module = models.BooleanField(default=True)
    payroll_module = models.BooleanField(default=True)
    timetable_module = models.BooleanField(default=True)
    custom_reports = models.BooleanField(default=False)
    sso_integration = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'
        ordering = ['monthly_price']

    def __str__(self):
        return f"{self.name} Plan"


class Subscription(models.Model):
    """
    Subscription instance for a Tenant.
    """
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLE_CHOICES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Dates
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    trial_expiry = models.DateTimeField(blank=True, null=True)
    next_billing_date = models.DateTimeField(blank=True, null=True)
    
    # Payment info
    auto_renew = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant.school_name} - {self.plan.name}"

    def save(self, *args, **kwargs):
        """Set trial expiry and next billing date on creation."""
        # Use current time for date calculations (start_date will be set by auto_now_add)
        now = timezone.now()
        
        # Always set trial expiry if not already set
        if not self.trial_expiry:
            self.trial_expiry = now + timedelta(days=14)  # 14 days trial
        
        # Set next billing date based on billing cycle
        # Use now() since start_date won't be set until after first save
        if self.billing_cycle == 'monthly':
            self.next_billing_date = now + timedelta(days=30)
        else:  # yearly
            self.next_billing_date = now + timedelta(days=365)
        
        super().save(*args, **kwargs)

    def is_trial_active(self):
        """Check if trial period is active."""
        if not self.trial_expiry:
            return False
        return self.status == 'trial' and self.trial_expiry > timezone.now()


class Invoice(models.Model):
    """
    Invoice records for subscriptions.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    
    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-issued_date']

    def __str__(self):
        return f"Invoice {self.invoice_number}"
