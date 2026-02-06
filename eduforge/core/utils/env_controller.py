"""
Environment Controller - Manages development/testing features and validation bypasses.
This file allows toggling various validations on/off for development and testing purposes.
"""
import os
from django.conf import settings


class EnvController:
    """
    Manages environment settings and feature flags.
    Set these to False in production.
    """
    
    # ==================== SUBDOMAIN VALIDATION ====================
    # Controls whether subdomain uniqueness and format validation is enforced
    BYPASS_SUBDOMAIN_VALIDATION = os.getenv('BYPASS_SUBDOMAIN_VALIDATION', 'True').lower() == 'true'
    
    # Allow subdomains that already exist (test multiple registrations with same subdomain)
    ALLOW_DUPLICATE_SUBDOMAINS = os.getenv('ALLOW_DUPLICATE_SUBDOMAINS', 'True').lower() == 'true'
    
    # Allow invalid subdomain formats (non-alphanumeric, too short/long)
    ALLOW_INVALID_SUBDOMAIN_FORMAT = os.getenv('ALLOW_INVALID_SUBDOMAIN_FORMAT', 'False').lower() == 'true'
    
    # ==================== EMAIL VALIDATION ====================
    # Controls whether email uniqueness validation is enforced
    BYPASS_EMAIL_VALIDATION = os.getenv('BYPASS_EMAIL_VALIDATION', 'True').lower() == 'true'
    
    # Allow duplicate email registrations
    ALLOW_DUPLICATE_EMAILS = os.getenv('ALLOW_DUPLICATE_EMAILS', 'True').lower() == 'true'
    
    # ==================== PASSWORD VALIDATION ====================
    # Controls whether strict password requirements are enforced
    BYPASS_PASSWORD_VALIDATION = os.getenv('BYPASS_PASSWORD_VALIDATION', 'True').lower() == 'true'
    
    # Allow passwords with less than 8 characters
    ALLOW_WEAK_PASSWORD = os.getenv('ALLOW_WEAK_PASSWORD', 'True').lower() == 'true'
    
    # Allow passwords without uppercase letters
    ALLOW_NO_UPPERCASE = os.getenv('ALLOW_NO_UPPERCASE', 'True').lower() == 'true'
    
    # Allow passwords without numbers
    ALLOW_NO_NUMBERS = os.getenv('ALLOW_NO_NUMBERS', 'True').lower() == 'true'
    
    # Allow passwords without special characters
    ALLOW_NO_SPECIAL_CHARS = os.getenv('ALLOW_NO_SPECIAL_CHARS', 'True').lower() == 'true'
    
    # ==================== PAYMENT/BILLING VALIDATION ====================
    # Skip payment processing and mark all subscriptions as active
    BYPASS_PAYMENT_VALIDATION = os.getenv('BYPASS_PAYMENT_VALIDATION', 'True').lower() == 'true'
    
    # Skip trial period - activate immediately
    SKIP_TRIAL_PERIOD = os.getenv('SKIP_TRIAL_PERIOD', 'True').lower() == 'true'
    
    # Allow free plans without payment
    ALLOW_FREE_PLANS = os.getenv('ALLOW_FREE_PLANS', 'True').lower() == 'true'
    
    # ==================== PHONE VALIDATION ====================
    # Skip phone number format validation
    BYPASS_PHONE_VALIDATION = os.getenv('BYPASS_PHONE_VALIDATION', 'True').lower() == 'true'
    
    # ==================== ADDRESS VALIDATION ====================
    # Make address fields optional instead of required
    MAKE_ADDRESS_OPTIONAL = os.getenv('MAKE_ADDRESS_OPTIONAL', 'True').lower() == 'true'
    
    # ==================== GENERAL SETTINGS ====================
    # Development mode - enables all bypasses
    DEV_MODE = os.getenv('DEV_MODE', 'True').lower() == 'true'
    
    # Enable debug logging for validations
    DEBUG_VALIDATIONS = os.getenv('DEBUG_VALIDATIONS', 'False').lower() == 'true'
    
    @classmethod
    def is_production(cls):
        """Check if running in production environment."""
        return not settings.DEBUG
    
    @classmethod
    def should_validate_subdomain(cls):
        """Determine if subdomain validation should be enforced."""
        if cls.is_production():
            return True
        return not cls.BYPASS_SUBDOMAIN_VALIDATION
    
    @classmethod
    def should_validate_email(cls):
        """Determine if email validation should be enforced."""
        if cls.is_production():
            return True
        return not cls.BYPASS_EMAIL_VALIDATION
    
    @classmethod
    def should_validate_password(cls):
        """Determine if password validation should be enforced."""
        if cls.is_production():
            return True
        return not cls.BYPASS_PASSWORD_VALIDATION
    
    @classmethod
    def should_validate_payment(cls):
        """Determine if payment validation should be enforced."""
        if cls.is_production():
            return True
        return not cls.BYPASS_PAYMENT_VALIDATION
    
    @classmethod
    def should_validate_phone(cls):
        """Determine if phone validation should be enforced."""
        if cls.is_production():
            return True
        return not cls.BYPASS_PHONE_VALIDATION
    
    @classmethod
    def log_validation_bypass(cls, validation_type, message):
        """Log when a validation is bypassed."""
        if cls.DEBUG_VALIDATIONS:
            print(f"[VALIDATION BYPASS] {validation_type}: {message}")
    
    @classmethod
    def get_all_settings(cls):
        """Return all environment controller settings as a dictionary."""
        return {
            'SUBDOMAIN': {
                'bypass': cls.BYPASS_SUBDOMAIN_VALIDATION,
                'allow_duplicates': cls.ALLOW_DUPLICATE_SUBDOMAINS,
                'allow_invalid_format': cls.ALLOW_INVALID_SUBDOMAIN_FORMAT,
            },
            'EMAIL': {
                'bypass': cls.BYPASS_EMAIL_VALIDATION,
                'allow_duplicates': cls.ALLOW_DUPLICATE_EMAILS,
            },
            'PASSWORD': {
                'bypass': cls.BYPASS_PASSWORD_VALIDATION,
                'allow_weak': cls.ALLOW_WEAK_PASSWORD,
                'allow_no_uppercase': cls.ALLOW_NO_UPPERCASE,
                'allow_no_numbers': cls.ALLOW_NO_NUMBERS,
                'allow_no_special_chars': cls.ALLOW_NO_SPECIAL_CHARS,
            },
            'PAYMENT': {
                'bypass': cls.BYPASS_PAYMENT_VALIDATION,
                'skip_trial': cls.SKIP_TRIAL_PERIOD,
                'allow_free_plans': cls.ALLOW_FREE_PLANS,
            },
            'PHONE': {
                'bypass': cls.BYPASS_PHONE_VALIDATION,
            },
            'ADDRESS': {
                'make_optional': cls.MAKE_ADDRESS_OPTIONAL,
            },
            'GENERAL': {
                'dev_mode': cls.DEV_MODE,
                'debug_validations': cls.DEBUG_VALIDATIONS,
                'is_production': cls.is_production(),
            }
        }


# Convenience instance for easier importing
env = EnvController()
