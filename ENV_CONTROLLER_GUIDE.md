# Environment Controller - Validation Bypass System

The `EnvController` is a configuration system that allows you to toggle various form validations on and off for development, testing, and debugging purposes. This is useful when you want to quickly test features without worrying about strict validation requirements.

## Overview

The environment controller provides boolean flags for controlling validations in different areas:

- **Subdomain Validation**: Control subdomain uniqueness and format checks
- **Email Validation**: Control email uniqueness checks
- **Password Validation**: Control password strength requirements
- **Payment Validation**: Control payment and billing validations
- **Phone Validation**: Control phone number format validation
- **Address Validation**: Make address fields optional

## Quick Start

### 1. Set Environment Variables in `.env` File

Create a `.env` file in the project root:

```env
# Allow development with relaxed validations
BYPASS_SUBDOMAIN_VALIDATION=True
ALLOW_DUPLICATE_SUBDOMAINS=True
BYPASS_EMAIL_VALIDATION=True
ALLOW_DUPLICATE_EMAILS=True
BYPASS_PASSWORD_VALIDATION=True
ALLOW_WEAK_PASSWORD=True
DEBUG_VALIDATIONS=True
```

### 2. Use Management Command to View Settings

```bash
# View all current settings
python manage.py env_settings

# Export current settings as .env format
python manage.py env_settings --export
```

## Configuration Options

### Subdomain Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `BYPASS_SUBDOMAIN_VALIDATION` | `True` | Skip all subdomain validation in dev |
| `ALLOW_DUPLICATE_SUBDOMAINS` | `True` | Allow multiple registrations with same subdomain |
| `ALLOW_INVALID_SUBDOMAIN_FORMAT` | `False` | Accept invalid subdomain formats |

**Use Case**: Testing multiple school registrations, testing validation logic

### Email Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `BYPASS_EMAIL_VALIDATION` | `True` | Skip email validation in dev |
| `ALLOW_DUPLICATE_EMAILS` | `True` | Allow duplicate email registrations |

**Use Case**: Testing without valid email addresses, bulk testing

### Password Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `BYPASS_PASSWORD_VALIDATION` | `True` | Skip all password validation |
| `ALLOW_WEAK_PASSWORD` | `True` | Allow passwords shorter than 8 chars |
| `ALLOW_NO_UPPERCASE` | `True` | Allow passwords without uppercase letters |
| `ALLOW_NO_NUMBERS` | `True` | Allow passwords without numbers |
| `ALLOW_NO_SPECIAL_CHARS` | `True` | Allow passwords without special characters |

**Use Case**: Quick testing with simple passwords like "test", "password123", etc.

### Payment/Billing Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `BYPASS_PAYMENT_VALIDATION` | `True` | Skip payment processing in dev |
| `SKIP_TRIAL_PERIOD` | `True` | Activate subscriptions immediately |
| `ALLOW_FREE_PLANS` | `True` | Allow free plan selection without payment |

**Use Case**: Testing the full registration flow without payment integration

### Phone Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `BYPASS_PHONE_VALIDATION` | `True` | Skip phone number format validation |

**Use Case**: Testing with dummy phone numbers

### Address Validation

| Setting | Default | Purpose |
|---------|---------|---------|
| `MAKE_ADDRESS_OPTIONAL` | `True` | Make address fields optional |

**Use Case**: Quick testing without entering complete address information

### General Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| `DEV_MODE` | `True` | Enable development mode with relaxed validations |
| `DEBUG_VALIDATIONS` | `False` | Log validation bypasses to console |

## Usage Examples

### Example 1: Test Registration with Simple Password

**Enable**:
```env
BYPASS_PASSWORD_VALIDATION=True
ALLOW_WEAK_PASSWORD=True
ALLOW_NO_UPPERCASE=True
ALLOW_NO_NUMBERS=True
ALLOW_NO_SPECIAL_CHARS=True
```

**Result**: Passwords like "test" will be accepted

### Example 2: Test Multiple Registrations with Same Domain

**Enable**:
```env
ALLOW_DUPLICATE_SUBDOMAINS=True
ALLOW_DUPLICATE_EMAILS=True
```

**Result**: You can register multiple schools with the same subdomain and email

### Example 3: Quick Full Flow Testing

**Enable**:
```env
# Subdomain
BYPASS_SUBDOMAIN_VALIDATION=True
ALLOW_DUPLICATE_SUBDOMAINS=True

# Email
BYPASS_EMAIL_VALIDATION=True
ALLOW_DUPLICATE_EMAILS=True

# Password
BYPASS_PASSWORD_VALIDATION=True
ALLOW_WEAK_PASSWORD=True

# Payment
BYPASS_PAYMENT_VALIDATION=True
SKIP_TRIAL_PERIOD=True

# Debug
DEBUG_VALIDATIONS=True
```

**Result**: You can quickly register with minimal information and simple credentials

### Example 4: Production Settings

```env
# DISABLE ALL BYPASSES FOR PRODUCTION
BYPASS_SUBDOMAIN_VALIDATION=False
ALLOW_DUPLICATE_SUBDOMAINS=False
ALLOW_INVALID_SUBDOMAIN_FORMAT=False

BYPASS_EMAIL_VALIDATION=False
ALLOW_DUPLICATE_EMAILS=False

BYPASS_PASSWORD_VALIDATION=False
ALLOW_WEAK_PASSWORD=False
ALLOW_NO_UPPERCASE=False
ALLOW_NO_NUMBERS=False
ALLOW_NO_SPECIAL_CHARS=False

BYPASS_PAYMENT_VALIDATION=False
SKIP_TRIAL_PERIOD=False
ALLOW_FREE_PLANS=False

BYPASS_PHONE_VALIDATION=False
MAKE_ADDRESS_OPTIONAL=False

DEV_MODE=False
DEBUG_VALIDATIONS=False
```

## Code Integration

The environment controller is automatically used in these locations:

### Forms (core/users/forms.py)

```python
from core.utils.env_controller import EnvController

class SchoolRegistrationForm(forms.Form):
    def clean_subdomain(self):
        """Subdomain validation with bypass support."""
        subdomain = self.cleaned_data.get('subdomain')
        
        if not EnvController.ALLOW_DUPLICATE_SUBDOMAINS:
            if Tenant.objects.filter(subdomain=subdomain).exists():
                raise ValidationError('This subdomain is already taken.')
        
        if not EnvController.ALLOW_INVALID_SUBDOMAIN_FORMAT:
            if not Tenant._validate_subdomain(subdomain):
                raise ValidationError('Invalid subdomain format.')
        
        return subdomain
```

### Custom Validation in Views

```python
from core.utils.env_controller import EnvController

# In your view logic
if EnvController.should_validate_payment():
    process_payment(...)
else:
    # Skip payment in development
    subscription.status = 'trial'
```

## Helper Methods

The `EnvController` class provides several convenience methods:

```python
from core.utils.env_controller import EnvController

# Check if validation should be enforced
if EnvController.should_validate_subdomain():
    # Run validation
    pass

# Log validation bypasses for debugging
EnvController.log_validation_bypass('PASSWORD', 'Using weak password in dev')

# Check if running in production
if EnvController.is_production():
    # Enforce all validations
    pass

# Get all settings as a dictionary
settings = EnvController.get_all_settings()
```

## Important Notes

### ⚠️ Production Safety

The environment controller has built-in safety mechanisms:

1. **Production Override**: When `settings.DEBUG = False`, ALL validations are enforced regardless of environment variables
2. **No Whitelist**: Validation bypasses are completely disabled in production

### Default Behavior

- In **development** (`DEBUG=True`): Validations are relaxed by default
- In **production** (`DEBUG=False`): All validations are enforced, bypasses are ignored
- Use `.env.example` as a template for your environment configuration

### Monitoring

Enable `DEBUG_VALIDATIONS=True` to log when validations are bypassed:

```bash
# Terminal output example
[VALIDATION BYPASS] SUBDOMAIN: Subdomain "testschool" passed with overrides
[VALIDATION BYPASS] EMAIL: Email "test@example.com" passed with overrides
[VALIDATION BYPASS] PASSWORD: Password validation bypassed or relaxed
```

## File Locations

- **Controller**: `core/utils/env_controller.py`
- **Management Command**: `core/users/management/commands/env_settings.py`
- **Environment File**: `.env` (in project root)
- **Example File**: `.env.example` (provides defaults)

## Troubleshooting

### Validation Not Being Bypassed

1. Confirm the environment variable is set in `.env`
2. Ensure `DEBUG=True` in Django settings
3. Check the console output with `DEBUG_VALIDATIONS=True`
4. Restart the development server

### Changes Not Taking Effect

Environment variables are loaded on server startup:
```bash
# Restart the server for changes to take effect
python manage.py runserver
```

### Production Validation is Too Strict

This is intentional. For production:
1. Use strong, unique passwords
2. Use valid email addresses
3. Use unique subdomains
4. Ensure payment information is correct

## Related Files

- `core/users/forms.py` - Contains form validation logic
- `core/users/views.py` - Contains view logic
- `core/tenants/models.py` - Contains Tenant model and validation
- `.env` - Your environment configuration file
