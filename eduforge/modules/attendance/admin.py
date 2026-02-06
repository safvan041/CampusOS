"""
Admin configuration for attendance module.
"""
from django.contrib import admin
from .models import Class, Student, Attendance


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin interface for Class model."""
    list_display = ('name', 'section', 'class_teacher', 'tenant', 'academic_year', 'is_active', 'get_student_count')
    list_filter = ('tenant', 'academic_year', 'is_active')
    search_fields = ('name', 'section', 'class_teacher__first_name', 'class_teacher__last_name')
    ordering = ('tenant', 'name', 'section')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'name', 'section', 'class_teacher', 'academic_year')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_student_count(self, obj):
        """Display student count."""
        return obj.get_student_count()
    get_student_count.short_description = 'Students'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    list_display = ('get_full_name', 'roll_number', 'admission_number', 'class_assigned', 'tenant', 'is_active')
    list_filter = ('tenant', 'class_assigned', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'roll_number', 'admission_number')
    ordering = ('class_assigned', 'roll_number')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant', 'user', 'roll_number', 'admission_number', 'class_assigned')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'parent_contact', 'parent_email')
        }),
        ('Status', {
            'fields': ('admission_date', 'is_active')
        }),
    )
    
    def get_full_name(self, obj):
        """Display student's full name."""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance model."""
    list_display = ('get_student_name', 'date', 'status', 'marked_by', 'tenant')
    list_filter = ('tenant', 'status', 'date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__roll_number')
    date_hierarchy = 'date'
    ordering = ('-date', 'student__roll_number')
    
    fieldsets = (
        ('Attendance Information', {
            'fields': ('tenant', 'student', 'date', 'status')
        }),
        ('Additional Information', {
            'fields': ('marked_by', 'notes')
        }),
    )
    
    def get_student_name(self, obj):
        """Display student's name."""
        return obj.student.user.get_full_name()
    get_student_name.short_description = 'Student'
