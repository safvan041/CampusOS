#!/usr/bin/env python
"""
Initialize EduForge project with basic setup.

This script helps set up the project:
- Creates necessary directories
- Sets up environment files
- Creates database migrations
"""

import os
import sys
import shutil
from pathlib import Path


def setup_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')

    if env_file.exists():
        print('✓ .env file already exists')
        return

    if env_example.exists():
        shutil.copy(env_example, env_file)
        print('✓ Created .env file from .env.example')
    else:
        print('✗ .env.example not found')


def setup_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'media',
        'staticfiles',
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f'✓ Created {directory}/ directory')


def main():
    """Run setup tasks."""
    print('=' * 50)
    print('EduForge - Project Setup')
    print('=' * 50)
    print()

    print('Setting up environment...')
    setup_env_file()
    print()

    print('Creating directories...')
    setup_directories()
    print()

    print('=' * 50)
    print('Setup Complete!')
    print('=' * 50)
    print()
    print('Next steps:')
    print('1. Edit .env file with your configuration')
    print('2. Run: python manage.py migrate')
    print('3. Run: python manage.py createsuperuser')
    print('4. Run: python manage.py runserver')
    print()


if __name__ == '__main__':
    main()
