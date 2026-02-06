"""
Authentication and user forms.
"""
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import re

from .models import CustomUser
from core.tenants.models import Tenant, TenantSettings
from core.billing.models import Subscription, SubscriptionPlan
from core.utils.env_controller import EnvController


class SchoolRegistrationForm(forms.Form):
    """
    Multi-step school registration form.
    """
    # STEP 1: Basic School Identity
    school_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter full official school name',
        }),
        required=True
    )

    subdomain = forms.SlugField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., greenvalley',
            'pattern': '[a-z0-9]{3,20}',
        }),
        required=True,
        help_text='3-20 lowercase characters, no spaces'
    )

    # STEP 2: Contact Information
    official_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'official@school.in',
        }),
        required=True
    )

    alternate_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'alternate@school.in',
        }),
        required=False
    )

    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 XXXXX XXXXX',
            'type': 'tel',
        }),
        required=True
    )

    alternate_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91 XXXXX XXXXX',
            'type': 'tel',
        }),
        required=False
    )

    # STEP 3: Address
    street_address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address',
        }),
        required=False
    )

    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        }),
        required=True
    )

    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
        }),
        required=True
    )

    postal_code = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postal code',
        }),
        required=True
    )

    # STEP 4: School Profile
    school_type = forms.ChoiceField(
        choices=Tenant.SCHOOL_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=True
    )

    student_count = forms.ChoiceField(
        choices=Tenant.STUDENT_COUNT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=True
    )

    language_preference = forms.ChoiceField(
        choices=Tenant.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=True,
        initial='en'
    )

    # STEP 5: Subscription Setup
    subscription_plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        required=True,
        label='Select Subscription Plan'
    )

    billing_cycle = forms.ChoiceField(
        choices=Subscription.BILLING_CYCLE_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        required=True,
        initial='monthly'
    )

    # STEP 6: Admin Account
    admin_first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
        }),
        required=True
    )

    admin_last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
        }),
        required=True
    )

    admin_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin@school.in',
        }),
        required=True
    )

    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        required=True,
        help_text='8+ characters, uppercase, lowercase, number, special character'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
        }),
        required=True
    )

    # Terms
    agree_terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        required=True,
        label='I agree to the Terms of Service and Privacy Policy'
    )

    def clean_subdomain(self):
        """Validate subdomain uniqueness and format."""
        subdomain = self.cleaned_data.get('subdomain')
        
        # Check subdomain uniqueness
        if not EnvController.ALLOW_DUPLICATE_SUBDOMAINS:
            if Tenant.objects.filter(subdomain=subdomain).exists():
                raise ValidationError('This subdomain is already taken. Please choose another.')
        
        # Check subdomain format
        if not EnvController.ALLOW_INVALID_SUBDOMAIN_FORMAT:
            if not Tenant.validate_subdomain_format(subdomain):
                raise ValidationError('Subdomain must be 3-20 lowercase characters, no spaces.')
        
        EnvController.log_validation_bypass('SUBDOMAIN', f'Subdomain "{subdomain}" passed with overrides')
        return subdomain

    def clean_admin_email(self):
        """Check if admin email already exists."""
        email = self.cleaned_data.get('admin_email')
        
        # Check email uniqueness
        if not EnvController.ALLOW_DUPLICATE_EMAILS:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError('This email is already registered.')
        
        EnvController.log_validation_bypass('EMAIL', f'Email "{email}" passed with overrides')
        return email

    def clean_admin_password(self):
        """Validate password strength."""
        password = self.cleaned_data.get('admin_password')
        
        # Only validate if not bypassed
        if not EnvController.BYPASS_PASSWORD_VALIDATION:
            if not EnvController.ALLOW_WEAK_PASSWORD and len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            
            if not EnvController.ALLOW_NO_UPPERCASE and not re.search(r'[A-Z]', password):
                raise ValidationError('Password must contain at least one uppercase letter.')
            
            if not EnvController.ALLOW_NO_UPPERCASE and not re.search(r'[a-z]', password):
                raise ValidationError('Password must contain at least one lowercase letter.')
            
            if not EnvController.ALLOW_NO_NUMBERS and not re.search(r'[0-9]', password):
                raise ValidationError('Password must contain at least one digit.')
            
            if not EnvController.ALLOW_NO_SPECIAL_CHARS and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError('Password must contain at least one special character.')
        
        EnvController.log_validation_bypass('PASSWORD', 'Password validation bypassed or relaxed')
        return password

    def clean(self):
        """Validate entire form."""
        cleaned_data = super().clean()
        password = cleaned_data.get('admin_password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class LoginForm(forms.Form):
    """
    User login form.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email or Username',
            'autofocus': True,
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        })
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Remember me'
    )

    def clean(self):
        """Validate credentials."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            # Try authentication with email
            user = authenticate(username=email, password=password)
            
            if user is None:
                # Try with username
                user = authenticate(username=email, password=password)
            
            if user is None:
                raise ValidationError('Invalid email/password combination.')
            
            cleaned_data['user'] = user

        return cleaned_data


class AdminAccountForm(forms.ModelForm):
    """
    Admin account creation during registration.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        }),
        help_text='8+ characters, uppercase, lowercase, number, special character'
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
        }

    def clean_password(self):
        """Validate password strength."""
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one digit.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')
        
        return password

    def clean(self):
        """Validate password confirmation."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        
        if password and confirm and password != confirm:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data
