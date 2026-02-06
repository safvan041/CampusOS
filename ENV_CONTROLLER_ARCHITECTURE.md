# Environment Controller Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Registration Form                    │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│            Form Validation Methods                           │
│         (forms.py clean_* methods)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ - clean_subdomain()                                  │  │
│  │ - clean_admin_email()                                │  │
│  │ - clean_admin_password()                             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
       ┌─────────────┐
       │ Check: Is   │
       │ validation  │
       │ bypassed?   │
       └──────┬──────┘
          ┌──┴──┐
       YES│     │NO
         │      │
         ▼      ▼
    ┌────────┐ ┌─────────────────────────────────┐
    │ PASS   │ │  Run Full Validation            │
    │        │ │  (format, uniqueness, etc)      │
    │        │ │                                 │
    │        │ │  If fails: Raise ValidationError│
    │        │ │  If passes: Continue            │
    └────────┘ └─────────────────────────────────┘
         │            │
         └─────┬──────┘
              │
              ▼
    ┌─────────────────────────────┐
    │  Form Submission Success    │
    │  Create Tenant/User/etc     │
    └─────────────────────────────┘
```

## Component Relationship

```
┌──────────────────────────────────┐
│  .env File                       │
│  ┌────────────────────────────┐  │
│  │ BYPASS_SUBDOMAIN_VALIDATION│  │
│  │ ALLOW_DUPLICATE_EMAILS      │  │
│  │ BYPASS_PASSWORD_VALIDATION  │  │
│  │ ... (17 total flags)        │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
              │ (python-dotenv reads)
              ▼
┌──────────────────────────────────┐
│  Django settings/base.py         │
│  (loads .env on startup)         │
└──────────────────────────────────┘
              │ (os.getenv)
              ▼
┌──────────────────────────────────┐
│ EnvController                    │
│ (core/utils/env_controller.py)   │
│  ┌────────────────────────────┐  │
│  │ BYPASS_SUBDOMAIN_VALIDATION│  │
│  │ ALLOW_DUPLICATE_EMAILS      │  │
│  │ BYPASS_PASSWORD_VALIDATION  │  │
│  │ ... (class attributes)       │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ should_validate_*() methods │  │
│  │ is_production() method      │  │
│  │ log_validation_bypass()     │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
              │ (imported by)
              ▼
┌──────────────────────────────────┐
│  Forms (forms.py)                │
│  ┌────────────────────────────┐  │
│  │ clean_subdomain()          │  │
│  │  ↓ calls                   │  │
│  │  EnvController.             │  │
│  │  ALLOW_DUPLICATE_SUBDOMAINS│  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ clean_admin_email()        │  │
│  │  ↓ calls                   │  │
│  │  EnvController.             │  │
│  │  ALLOW_DUPLICATE_EMAILS     │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │ clean_admin_password()     │  │
│  │  ↓ calls                   │  │
│  │  EnvController.             │  │
│  │  BYPASS_PASSWORD_VALIDATION │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## Data Flow: User Registration

```
1. User fills registration form
   ├─ School Name: "My School"
   ├─ Subdomain: "myschool"
   ├─ Email: "admin@myschool.com"
   └─ Password: "test"

2. Form submission → views.py register_view()

3. Form validation triggered:
   
   Subdomain Validation:
   ├─ Check: ALLOW_DUPLICATE_SUBDOMAINS = True?
   │  └─ YES: Skip duplicate check ✓
   ├─ Check: ALLOW_INVALID_SUBDOMAIN_FORMAT = True?
   │  └─ NO: Run format check ✓
   └─ Result: PASS ✓
   
   Email Validation:
   ├─ Check: ALLOW_DUPLICATE_EMAILS = True?
   │  └─ YES: Skip duplicate check ✓
   └─ Result: PASS ✓
   
   Password Validation:
   ├─ Check: BYPASS_PASSWORD_VALIDATION = True?
   │  └─ YES: Skip all checks ✓
   └─ Result: PASS ✓

4. All validations passed → Create records:
   ├─ Create Tenant
   ├─ Create Admin User
   ├─ Create Subscription
   └─ Auto-login ✓

5. Redirect to dashboard ✓
```

## Flag Dependency Chart

```
PASSWORD VALIDATION:
├─ BYPASS_PASSWORD_VALIDATION = True?
│  └─ If YES: Skip everything below
├─ ALLOW_WEAK_PASSWORD (only if bypass = False)
├─ ALLOW_NO_UPPERCASE (only if bypass = False)
├─ ALLOW_NO_NUMBERS (only if bypass = False)
└─ ALLOW_NO_SPECIAL_CHARS (only if bypass = False)

SUBDOMAIN VALIDATION:
├─ BYPASS_SUBDOMAIN_VALIDATION = True?
│  └─ If YES: Skip everything below
├─ ALLOW_DUPLICATE_SUBDOMAINS
└─ ALLOW_INVALID_SUBDOMAIN_FORMAT

EMAIL VALIDATION:
├─ BYPASS_EMAIL_VALIDATION = True?
│  └─ If YES: Skip below
└─ ALLOW_DUPLICATE_EMAILS

PAYMENT VALIDATION:
├─ BYPASS_PAYMENT_VALIDATION = True?
│  └─ If YES: Skip below
├─ SKIP_TRIAL_PERIOD
└─ ALLOW_FREE_PLANS
```

## Environment States

### Development State (Current)
```
.env File:
├─ BYPASS_SUBDOMAIN_VALIDATION=True     ✓ Testing
├─ BYPASS_EMAIL_VALIDATION=True         ✓ Testing
├─ BYPASS_PASSWORD_VALIDATION=True      ✓ Testing
├─ BYPASS_PAYMENT_VALIDATION=True       ✓ Testing
├─ ALLOW_DUPLICATE_EMAILS=True          ✓ Testing
├─ DEBUG_VALIDATIONS=False              ℹ️ Silent
└─ DEV_MODE=True                        ✓ Active

Result: Fast testing, all validations relaxed
```

### Staging State (Testing Production)
```
.env File:
├─ BYPASS_SUBDOMAIN_VALIDATION=False    ⚠️ Enforce
├─ BYPASS_EMAIL_VALIDATION=False        ⚠️ Enforce
├─ BYPASS_PASSWORD_VALIDATION=False     ⚠️ Enforce
├─ ALLOW_WEAK_PASSWORD=False            ⚠️ Enforce
├─ BYPASS_PAYMENT_VALIDATION=False      ⚠️ Enforce
├─ DEBUG_VALIDATIONS=True               ℹ️ Verbose
└─ DEV_MODE=False                       ⚠️ Off

Result: Production-like validation, debugging enabled
```

### Production State
```
Django Settings:
├─ DEBUG=False

Result:
├─ EnvController.is_production() → True
├─ ALL validations ENFORCED regardless of .env
└─ No bypasses possible

(The .env file is completely ignored)
```

## Code Execution Example

```python
# Form receives: clean_admin_password()
password = "test"  # Simple password, normally invalid

# Step 1: Check bypass flag
if not EnvController.BYPASS_PASSWORD_VALIDATION:
    # Step 2: If not bypassed, perform validation
    if not EnvController.ALLOW_WEAK_PASSWORD and len(password) < 8:
        raise ValidationError('Password must be at least 8 characters')
    # ...more checks...
else:
    # Bypassed! Skip all validation
    pass

# Step 3: Log the action
EnvController.log_validation_bypass('PASSWORD', 'Password validation bypassed or relaxed')

# Step 4: Return the password (passes validation)
return password
```

## Management Command Flow

```
$ python manage.py env_settings [options]

Options:
├─ (no args)        → Show all settings with status
├─ --export         → Print .env format configuration
├─ --reset          → Show default configuration
├─ --toggle SETTING → Toggle a boolean setting
├─ --set SETTING=val → Set a setting value
└─ --help           → Show command help

Output Example:
├─ SUBDOMAIN SETTINGS:
│  ├─ BYPASS_SUBDOMAIN_VALIDATION      ✓ ENABLED
│  ├─ ALLOW_DUPLICATE_SUBDOMAINS       ✓ ENABLED
│  └─ ALLOW_INVALID_SUBDOMAIN_FORMAT   ✗ DISABLED
├─ EMAIL SETTINGS:
│  └─ ...
└─ [...]
```

## Files Modified vs. Created

### Created (New Files)
```
✓ core/utils/env_controller.py           Main controller
✓ core/users/management/commands/env_settings.py  CLI tool
✓ .env                                   Configuration
✓ .env.example                           Template
✓ ENV_CONTROLLER_GUIDE.md               Documentation
✓ SETUP_ENV_CONTROLLER.md               Setup guide
✓ ENV_CONTROLLER_ARCHITECTURE.md        This file
```

### Modified (Updated)
```
⚙️  core/users/forms.py                  Added EnvController import + validation logic
⚙️  config/settings/base.py              Added .env loading with python-dotenv
```

### Unchanged (Reference)
```
📋 core/tenants/models.py               (no changes, used by forms)
📋 core/users/views.py                  (no changes, uses forms)
📋 core/users/models.py                 (no changes, used by forms)
```

## Security Model

```
┌─ Production Check ────────────────────────────────┐
│                                                   │
│  Django DEBUG setting = False?                   │
│  ├─ YES → EnvController.is_production()=True    │
│  │       ├─ ALL validations enforced            │
│  │       ├─ .env file ignored                   │
│  │       └─ Bypasses impossible                 │
│  │                                               │
│  └─ NO → EnvController.is_production()=False    │
│         ├─ Check .env flags                    │
│         ├─ Allow bypasses if enabled           │
│         └─ Development validations apply        │
│                                                   │
└───────────────────────────────────────────────────┘

This ensures:
✓ No way to disable validations in production
✓ .env corruption won't break security
✓ Django DEBUG flag is ultimate authority
```

## Testing Workflow

```
1. FAST TESTING (All bypasses ON):
   Register → Validate Forms (all pass) → Create Records
   Time: ~1 second per registration

2. VALIDATION TESTING (Bypasses OFF):
   Register → Validate Forms (strict) → Debug failures
   Time: ~2-3 seconds per validation cycle

3. PRODUCTION TESTING (DEBUG=False):
   Register → Force all validations → Full safety
   Time: ~2-3 seconds per validation cycle
```
