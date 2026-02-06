"""
Timetable Module Models
Defines the structure for scheduling classes using academic sections.
"""
from django.db import models
from django.utils import timezone
from core.tenants.models import Tenant
from core.users.models import CustomUser
from modules.academic.models import Section, AcademicSession


class TenantScopedManager(models.Manager):
    """Manager that automatically filters by tenant."""
    def get_queryset(self):
        return super().get_queryset()
    
    def for_tenant(self, tenant):
        return self.get_queryset().filter(tenant=tenant)


class TimeSlot(models.Model):
    """
    Represents a time period for classes (e.g., "Period 1", "Morning Break").
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='time_slots')
    name = models.CharField(max_length=50, help_text="e.g., 'Period 1', 'Lunch Break'")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False, help_text="If true, no classes can be scheduled")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        unique_together = ('tenant', 'name', 'start_time')
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"


class SectionTimetable(models.Model):
    """
    Represents a scheduled class for a specific section.
    Links a section to a subject, teacher, and time slot.
    """
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='timetables')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='timetables')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='timetables')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='allocations')
    
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    
    # Keep as CharField for now - can link to Subject later if needed
    subject = models.CharField(
        max_length=100,
        help_text="Subject name (e.g., Mathematics, English)"
    )
    teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='timetable_allocations',
        limit_choices_to={'role__name': 'Teacher'}
    )
    
    room_number = models.CharField(max_length=20, blank=True, help_text="Override section room if needed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantScopedManager()
    
    class Meta:
        verbose_name = 'Section Timetable'
        verbose_name_plural = 'Section Timetables'
        unique_together = ('tenant', 'section', 'day_of_week', 'time_slot')
        ordering = ['day_of_week', 'time_slot__start_time']
        
    def __str__(self):
        day = self.get_day_of_week_display()
        return f"{self.section.full_name} - {day} - {self.time_slot.name} ({self.subject})"
