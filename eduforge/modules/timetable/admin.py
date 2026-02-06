from django.contrib import admin
from .models import TimeSlot, SectionTimetable

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'tenant', 'is_break')
    list_filter = ('tenant', 'is_break')
    search_fields = ('name',)

@admin.register(SectionTimetable)
class SectionTimetableAdmin(admin.ModelAdmin):
    list_display = ('section', 'day_of_week', 'time_slot', 'subject', 'teacher', 'tenant')
    list_filter = ('tenant', 'day_of_week', 'academic_session', 'section__class_obj')
    search_fields = ('subject', 'teacher__username', 'section__name')
    autocomplete_fields = ['section', 'time_slot', 'teacher']
