# EduForge Authentication & Registration System - Setup Guide

## 🎯 Complete Multi-Tenant School Registration & Login System

This guide covers the complete authentication and multi-tenant school registration system implemented in EduForge.

## 📋 Features Implemented

### 1. **Landing Page** (`/`)
- Beautiful welcome page with school statistics
- Feature showcase
- CTAs to login and register
- Responsive design

### 2. **Login Page** (`/login/`)
- Simple email-based login
- "Remember me" functionality
- Link to registration for new schools
- Forgot password placeholder

### 3. **School Registration Form** (`/register/`)
Multi-step registration with 6 sections:

#### Step 1: Basic School Identity
- School Name (required)
- Subdomain (auto-validated for uniqueness, 3-20 chars, lowercase)
- Auto-generated Portal URL display

#### Step 2: Contact Information
- Official Email (required, checked for uniqueness)
- Alternate Email (optional)
- Phone Number (required)
- Alternate Phone (optional)

#### Step 3: School Address
- Street Address (optional)
- City (required)
- State (required)
- Postal Code (required)

#### Step 4: School Profile
- School Type (dropdown: Primary, Secondary, etc.)
- Estimated Student Count (tiered pricing)
- Language Preference (English, Gujarati, Hindi, etc.)

#### Step 5: Subscription Setup
- Plan Selection (Basic, Standard, Premium)
- Billing Cycle (Monthly or Yearly)
- 14-day free trial included

#### Step 6: Admin Account Creation
- Admin First Name
- Admin Last Name
- Admin Email
- Password with strength validation:
  - 8+ characters
  - Uppercase + lowercase
  - Number
  - Special character
- Confirm Password

Terms & Conditions acceptance required

### 4. **Dashboard** (`/dashboard/`)
Post-login dashboard with:
- Subscription info
- Quick module access (Attendance, Payroll, Timetable)
- Account settings
- School information

## 🗄️ Database Models

### 1. **Tenant** (School/Organization)
```python
- UUID primary key
- school_name
- subdomain (unique, validated)
- portal_url (auto-generated)
- Contact information
- Address details
- School type & student count
- Language preference
- Trial expiry date
- Active status
- Created timestamp
```

### 2. **TenantSettings**
```python
- One-to-one with Tenant
- Feature toggles (attendance, payroll, timetable)
- Custom theme color
- Logo upload
```

### 3. **CustomUser** (Extended from Django User)
```python
- UUID primary key
- Tenant (foreign key)
- Role (super_admin, admin, teacher, student, parent, staff)
- Phone number
- Student ID (unique per tenant)
- Parent code (unique per tenant)
- Email verification status
- Created timestamp
```

### 4. **SubscriptionPlan** (Pre-defined Plans)
```python
- UUID primary key
- Name (Basic, Standard, Premium)
- Monthly & yearly prices
- Feature limits (students, staff, classes, storage, API calls)
- Module inclusions
- Is active flag
```

### 5. **Subscription** (Tenant Subscription Instance)
```python
- UUID primary key
- Tenant (one-to-one)
- Plan (foreign key)
- Billing cycle (monthly/yearly)
- Status (trial, active, suspended, cancelled, expired)
- Dates (start, end, trial expiry, next billing)
- Auto-renew flag
```

### 6. **Invoice** (Billing Records)
```python
- UUID primary key
- Subscription (foreign key)
- Invoice number (unique)
- Amount, tax, total
- Status (draft, sent, paid, overdue, cancelled)
- Date tracking
```

##  URLs & Endpoints

### Authentication Routes
```
GET  /                           → Landing page
GET  /login/                     → Login form
POST /login/                     → Process login
GET  /register/                  → Registration form
POST /register/                  → Process registration
GET  /logout/                    → Logout user
GET  /dashboard/                 → Dashboard (protected)

# AJAX Endpoints
GET  /api/check-subdomain/?subdomain=xxx     → Check availability
GET  /api/check-email/?email=xxx             → Check email availability
```

## 🔐 Security Features

1. **CSRF Protection** - All forms include CSRF tokens
2. **Password Strength** - Enforced requirements with validation
3. **Email Verification** - Email uniqueness checks per tenant
4. **Subdomain Validation** - Format and uniqueness validation
5. **Secure Session** - Django session management
6. **Multi-tenant Isolation** - Users scoped to tenants

## 📝 Forms & Validation

### Forms Created:
1. `SchoolRegistrationForm` - Complete registration
2. `LoginForm` - User authentication
3. `AdminAccountForm` - Admin account creation

### Validations:
- Subdomain format: `^[a-z0-9]{3,20}$`
- Email uniqueness per system
- Password strength requirements
- Phone number format
- Subdomain uniqueness
- Email confirmation matching

## 🎨 Frontend Features

### HTML Templates:
- `base.html` - Main layout with navbar and footer
- `auth/landing.html` - Welcome page
- `auth/login.html` - Login form
- `auth/register.html` - Multi-step registration
- `dashboard/index.html` - Dashboard

### JavaScript Features:
- Real-time subdomain availability checking
- Email validation on blur
- Password strength indicator
- Password confirmation validation
- Form validation with visual feedback
- Bootstrap-based responsive design

## 📊 Subscription Plans Pre-configured

### Basic Plan
- $99.99/month or $999.99/year
- Up to 100 students
- 20 staff members
- 5 classes
- 10 GB storage
- 10,000 API calls/month

### Standard Plan
- $299.99/month or $2,999.99/year
- Up to 500 students
- 100 staff members
- 25 classes
- 50 GB storage
- 50,000 API calls/month
- Custom reports included

### Premium Plan
- $999.99/month or $9,999.99/year
- Up to 5,000 students
- 500 staff members
- 100 classes
- 500 GB storage
- 500,000 API calls/month
- Custom reports
- SSO integration
- Priority support

## 🚀 Getting Started

### 1. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Run Server
```bash
python manage.py runserver
```

### 3. Access Application
```
http://localhost:8000/
```

### 4. Test Flow
- **Landing Page**: Visit home page
- **Register**: Sign up a new school with all details
- **Login**: Log in with admin credentials
- **Dashboard**: Access the dashboard

## 🧪 Testing

### Test Registration
1. Click "Register School" on landing page
2. Fill out all 6 steps:
   - School name & subdomain
   - Contact info
   - Address
   - School profile
   - Subscription selection
   - Admin account
3. Accept terms & submit
4. Should redirect to dashboard after successful registration

### Test Login
1. Click "Login" on landing page
2. Enter admin email and password
3. Check "Remember me" (optional)
4. Click Login
5. Should redirect to dashboard

### Test AJAX Validations
- Type subdomain → checks availability
- Enter email → checks if registered

## 📁 Project Structure

```
eduforge/
├── config/
│   ├── settings/
│   │   ├── base.py              # Base configuration
│   │   ├── dev.py               # Development settings
│   │   └── prod.py              # Production settings
│   └── urls.py                  # Main URL router
│
├── core/
│   ├── users/
│   │   ├── models.py           # CustomUser model
│   │   ├── forms.py            # Auth forms
│   │   ├── views.py            # Auth views
│   │   ├── urls.py             # Auth URLs
│   │   └── migrations/
│   │
│   ├── tenants/
│   │   ├── models.py           # Tenant models
│   │   ├── apps.py
│   │   └── migrations/
│   │
│   ├── billing/
│   │   ├── models.py           # Subscription models
│   │   ├── apps.py
│   │   └── migrations/
│
├── templates/
│   ├── base.html               # Base template
│   ├── auth/
│   │   ├── landing.html
│   │   ├── login.html
│   │   └── register.html
│   └── dashboard/
│       └── index.html
│
├── db.sqlite3                  # Development database
└── manage.py
```

## 🔄 Registration Workflow

```
User visits landing page
         ↓
Clicks "Register School"
         ↓
Fills registration form (6 steps)
         ↓
System validates all fields
         ↓
Creates Tenant record
         ↓
Creates TenantSettings
         ↓
Creates Admin User (super_admin role)
         ↓
Creates Subscription (trial status)
         ↓
Auto-login admin user
         ↓
Redirect to Dashboard
```

## 💡 Future Enhancements

1. **Email Verification** - Send verification email to school
2. **Password Reset** - Forgot password functionality
3. **OAuth/SSO Integration** - Google, Microsoft login
4. **Advanced Auth** - OTP, Biometric, Student ID login
5. **Payment Integration** - Stripe, PayPal for subscriptions
6. **Audit Logging** - Track all registration and login events
7. **Admin Dashboard** - School management interface
8. **API Keys** - Generate and manage API access tokens

## 🛠️ Technology Stack

- **Backend**: Django 4.2.8
- **Database**: SQLite3 (dev), PostgreSQL (prod)
- **Frontend**: Bootstrap 5, jQuery, JavaScript
- **Forms**: Django Forms with custom validation
- **Authentication**: Django Built-in + Custom User Model
- **API**: Django REST Framework

## 📞 Support

For issues or questions about the authentication system, please refer to the main README.md file.

---

**Version**: 1.0.0  
**Last Updated**: February 6, 2026
