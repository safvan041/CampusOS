"""
Academic Module Models
Defines the core academic structure: sessions, classes, sections, and enrollment.
"""
from django.db import models
from django.utils import timezone
from core.tenants.models import Tenant
from core.users.models import CustomUser


class TenantScopedManager(models.Manager):
    """Manager that automatically filters by tenant."""
    def get_queryset(self):
        return super().get_queryset()
    
    def for_tenant(self, tenant):
        return self.get_queryset().filter(tenant=tenant)


class AcademicSession(models.Model):
    """
    Represents an academic year/session (e.g., "2025-2026").
    Only one session can be active per tenant at a time.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='academic_sessions')
    name = models.CharField(max_length=50, help_text="e.g., '2025-2026'")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False, help_text="Only one session can be active per tenant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'
        unique_together = ('tenant', 'name')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.tenant.school_name})"
    
    def save(self, *args, **kwargs):
        """Ensure only one active session per tenant."""
        if self.is_active:
            AcademicSession.objects.filter(
                tenant=self.tenant,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class Class(models.Model):
    """
    Represents a grade/class level (e.g., "Grade 5", "Class 10").
    Linked to an academic session.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='academic_classes')
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='classes'
    )
    name = models.CharField(max_length=50, help_text="e.g., 'Grade 5', 'Class 10'")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ('tenant', 'academic_session', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.academic_session.name}"


class Section(models.Model):
    """
    Represents a section/division within a class (e.g., "A", "B", "C").
    Each section has a class teacher and can have a room number.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='academic_sections')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=10, help_text="e.g., 'A', 'B', 'C'")
    class_teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='academic_sections_taught',
        limit_choices_to={'role__name': 'Teacher'}
    )
    room_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
        unique_together = ('tenant', 'class_obj', 'name')
        ordering = ['class_obj', 'name']
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.name}"
    
    @property
    def full_name(self):
        """Returns full section name like 'Grade 5 - A'."""
        return f"{self.class_obj.name} - {self.name}"


class Enrollment(models.Model):
    """
    Represents a student's enrollment in a section for an academic session.
    Allows students to move between classes/sections each year.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='academic_enrollments')
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='academic_enrollments',
        limit_choices_to={'role__name': 'Student'}
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='enrollments')
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    roll_number = models.CharField(max_length=20)
    enrollment_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = ('tenant', 'student', 'academic_session')
        ordering = ['section', 'roll_number']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.section.full_name} ({self.academic_session.name})"
    
    @property
    def student_name(self):
        """Returns student's full name."""
        return self.student.get_full_name() or self.student.username


class Subject(models.Model):
    """
    Represents a subject (e.g., "Mathematics", "Science", "English").
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, help_text="e.g., 'MATH101'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        unique_together = ('tenant', 'code', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name
