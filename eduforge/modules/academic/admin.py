"""
Django Admin configuration for Academic module.
"""
from django.contrib import admin
from .models import AcademicSession, Class, Section, Enrollment


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'start_date', 'end_date', 'is_active')
    list_filter = ('tenant', 'is_active')
    search_fields = ('name',)
    ordering = ('-start_date',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_session', 'tenant')
    list_filter = ('tenant', 'academic_session')
    search_fields = ('name',)
    ordering = ('academic_session', 'name')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'class_teacher', 'room_number', 'tenant')
    list_filter = ('tenant', 'class_obj__academic_session')
    search_fields = ('name', 'class_obj__name')
    ordering = ('class_obj', 'name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'section', 'roll_number', 'academic_session', 'is_active')
    list_filter = ('tenant', 'academic_session', 'is_active', 'section')
    search_fields = ('student__first_name', 'student__last_name', 'student__username', 'roll_number')
    ordering = ('section', 'roll_number')
    
    def student_name(self, obj):
        return obj.student_name
    student_name.short_description = 'Student'
