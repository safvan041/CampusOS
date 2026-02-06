# EduForge - Multi-tenant Educational Management System

A scalable, modular Django-based educational management platform with multi-tenancy support, plugin architecture, and a comprehensive API gateway.

## Project Structure

```
eduforge/
├── manage.py                   # Django management script
├── config/                     # Django project configuration
│   ├── settings/
│   │   ├── base.py            # Base settings
│   │   ├── dev.py             # Development settings
│   │   └── prod.py            # Production settings
│   ├── urls.py                # Project URL routing
│   ├── asgi.py                # ASGI config (Async)
│   └── wsgi.py                # WSGI config (Production)
│
├── core/                       # Core engine (never tenant-specific)
│   ├── tenants/               # Multi-tenant logic
│   ├── users/                 # Authentication & roles
│   ├── plugins/               # Plugin loader system
│   ├── billing/               # Subscription management
│   ├── permissions/           # Permission system
│   └── utils/                 # Utility functions
│
├── modules/                    # Pluggable modules/features
│   ├── attendance/            # Attendance tracking
│   ├── payroll/               # Payroll management
│   └── timetable/             # Class scheduling
│
├── api/                       # REST API gateway
│   ├── v1/                    # API v1 endpoints
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── serializers.py
│   └── router.py              # Automatic route registration
│
├── marketplace/               # Developer/service marketplace
├── static/                    # Static files (CSS, JS, images)
├── templates/                 # HTML templates
├── requirements/              # Python dependencies
│   ├── base.txt              # Core dependencies
│   ├── dev.txt               # Development dependencies
│   └── prod.txt              # Production dependencies
├── docker/                    # Docker configuration
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── .env.example              # Environment variables template
└── pytest.ini                # Testing configuration
```

## Features

- **Multi-tenancy**: Support for multiple schools/organizations
- **Plugin Architecture**: Modular plugin system for extensibility
- **REST API**: Comprehensive API for all operations
- **User Management**: Role-based access control
- **Subscription Management**: Built-in billing system
- **Docker Ready**: Complete Docker & Docker Compose setup
- **Development Friendly**: Separate dev/prod configurations
- **School Registration**: Complete multi-step registration with validation
- **User Authentication**: Secure login system with session management

## 🔐 Authentication & Registration

EduForge includes a complete multi-tenant school registration and authentication system:

- **Landing Page** - Beautiful welcome page with features showcase
- **School Registration** - 6-step registration form:
  - Basic school identity (name, subdomain)
  - Contact information
  - Address
  - School profile (type, student count, language)
  - Subscription selection (trial available)
  - Admin account creation with password validation
- **Login System** - Secure email-based authentication
- **Dashboard** - Post-login dashboard with quick access to modules
- **Real-time Validation** - AJAX-based subdomain and email availability checks

**See [AUTHENTICATION.md](AUTHENTICATION.md) for detailed setup and usage guide.**

## Prerequisites

- Python 3.11+
- PostgreSQL 13+ (for production)
- Docker & Docker Compose (optional)

## Quick Start

### 1. Setup Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# For development
pip install -r requirements/dev.txt

# For production
pip install -r requirements/prod.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

### 4. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Docker Setup

### Using Docker Compose

```bash
cd docker

# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

### Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **nginx**: Reverse proxy (port 80)

## Configuration

### Development Settings

Edit `config/settings/dev.py` for development-specific configuration:
- Debug mode enabled
- SQLite database by default
- CORS all origins allowed
- Django Debug Toolbar enabled

### Production Settings

Edit `config/settings/prod.py` for production configuration:
- Debug mode disabled
- PostgreSQL required
- Secure settings enabled
- Static files configuration

### Environment Variables

Create a `.env` file with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.dev
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

## API Documentation

API endpoints are organized under `/api/v1/`:

```
GET    /api/v1/users/            # List users
POST   /api/v1/users/            # Create user
GET    /api/v1/users/{id}/       # Retrieve user
PUT    /api/v1/users/{id}/       # Update user
DELETE /api/v1/users/{id}/       # Delete user
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_users.py

# Run with coverage
pytest --cov=core --cov=api --cov=modules
```

## Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Sort imports
isort .
```

## Modules

### Attendance Module
Track student/staff attendance with customizable policies.

### Payroll Module
Manage salary, deductions, and payroll processing.

### Timetable Module
Schedule classes and manage academic calendars.

## Creating New Modules

1. Create a new app folder under `modules/`
2. Create an `apps.py` with AppConfig
3. Add to `INSTALLED_APPS` in `config/settings/base.py`
4. Create models, views, serializers as needed

## Contributing

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Create feature branches

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please contact the development team.

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure database (PostgreSQL)
- [ ] Set up environment variables
- [ ] Configure allowed hosts
- [ ] Enable HTTPS/SSL
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Run security checks: `python manage.py check --deploy`

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

```bash
cd docker
docker-compose -f docker-compose.yml up -d
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-06
