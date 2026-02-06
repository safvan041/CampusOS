"""
Attendance module models.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.tenants.models import Tenant
from core.users.models import CustomUser
import uuid


class TenantScopedManager(models.Manager):
    """
    Manager that automatically filters by tenant.
    """
    def get_queryset(self):
        """Override to add tenant filtering."""
        return super().get_queryset()
    
    def for_tenant(self, tenant):
        """Filter queryset by tenant."""
        return self.get_queryset().filter(tenant=tenant)


class Class(models.Model):
    """
    Class/Grade model representing academic classes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=50, help_text="e.g., Grade 10, Class 5")
    section = models.CharField(max_length=10, blank=True, help_text="e.g., A, B, C")
    class_teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='classes_taught',
        limit_choices_to={'role__name': 'Teacher'}
    )
    
    # Academic year
    academic_year = models.CharField(max_length=20, default='2025-2026', help_text="e.g., 2025-2026")
    
    # NEW: Link to academic module (for gradual migration)
    academic_section = models.ForeignKey(
        'academic.Section',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_attendance_classes',
        help_text="Link to academic module section (new structure)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ('tenant', 'name', 'section', 'academic_year')
        ordering = ['name', 'section']
    
    def __str__(self):
        section_str = f" - {self.section}" if self.section else ""
        return f"{self.name}{section_str} ({self.tenant.school_name})"
    
    def get_student_count(self):
        """Get total number of students in this class."""
        return self.students.filter(is_active=True).count()
    
    def get_present_count(self, date=None):
        """Get number of present students for a given date."""
        if date is None:
            date = timezone.now().date()
        return Attendance.objects.filter(
            student__class_assigned=self,
            date=date,
            status='present'
        ).count()


class Student(models.Model):
    """
    Student model extending the User model with academic information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='student_profile',
        limit_choices_to={'role__name': 'Student'}
    )
    roll_number = models.CharField(max_length=20)
    class_assigned = models.ForeignKey(
        Class, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='students'
    )
    
    # Additional student information
    admission_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_contact = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    
    # Status
    admission_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # NEW: Link to academic module enrollment (for gradual migration)
    enrollment = models.ForeignKey(
        'academic.Enrollment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legacy_attendance_students',
        help_text="Link to academic module enrollment (new structure)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        unique_together = ('tenant', 'roll_number', 'class_assigned')
        ordering = ['class_assigned', 'roll_number']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number} ({self.class_assigned})"
    
    def get_attendance_percentage(self, start_date=None, end_date=None):
        """Calculate attendance percentage for a date range."""
        if end_date is None:
            end_date = timezone.now().date()
        if start_date is None:
            # Default to current month
            start_date = end_date.replace(day=1)
        
        total_days = Attendance.objects.filter(
            student=self,
            date__gte=start_date,
            date__lte=end_date
        ).count()
        
        if total_days == 0:
            return 0
        
        present_days = Attendance.objects.filter(
            student=self,
            date__gte=start_date,
            date__lte=end_date,
            status='present'
        ).count()
        
        return round((present_days / total_days) * 100, 2)
    
    def clean(self):
        """Validate that user and tenant match."""
        if self.user and self.user.tenant != self.tenant:
            raise ValidationError("Student's user must belong to the same tenant.")


class Attendance(models.Model):
    """
    Attendance record model.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused Absence'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    
    # Who marked the attendance
    marked_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='attendance_marked'
    )
    
    # Optional notes
    notes = models.TextField(blank=True, help_text="Optional notes about the attendance")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
        unique_together = ('student', 'date')
        ordering = ['-date', 'student__roll_number']
        indexes = [
            models.Index(fields=['tenant', 'date']),
            models.Index(fields=['student', 'date']),
        ]
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date} - {self.get_status_display()}"
    
    def clean(self):
        """Validate attendance record."""
        # Ensure student and tenant match
        if self.student and self.student.tenant != self.tenant:
            raise ValidationError("Student must belong to the same tenant.")
        
        # Ensure marked_by user belongs to same tenant
        if self.marked_by and self.marked_by.tenant != self.tenant:
            raise ValidationError("Marker must belong to the same tenant.")
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
