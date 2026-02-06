from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Prefetch

from .models import TimeSlot, SectionTimetable
from modules.academic.models import Section, AcademicSession, Class as AcademicClass
from core.users.models import CustomUser

def is_staff_or_principal(user):
    return user.is_authenticated and (user.role.name in ['Principal', 'Staff'])

@login_required
def dashboard(request):
    """Timetable dashboard."""
    tenant = request.user.tenant
    
    # Quick stats
    total_slots = TimeSlot.objects.for_tenant(tenant).count()
    sections_with_timetable = SectionTimetable.objects.for_tenant(tenant).values('section').distinct().count()
    
    
    # Fetch all academic sections for the dashboard list
    # We want to show all sections so the principal can manage them
    sections = Section.objects.for_tenant(tenant).select_related('class_obj', 'class_teacher').order_by('class_obj__name', 'name')

    context = {
        'tenant': tenant,
        'module_name': 'Timetable',
        'total_slots': total_slots,
        'sections_with_timetable': sections_with_timetable,
        'sections': sections,
    }
    return render(request, 'modules/timetable/dashboard.html', context)

@login_required
def manage_time_slots(request):
    """Manage time slots (List & Create)."""
    if not is_staff_or_principal(request.user):
        messages.error(request, "Permission denied.")
        return redirect('timetable:dashboard')
        
    tenant = request.user.tenant
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        is_break = request.POST.get('is_break') == 'on'
        
        if name and start_time and end_time:
            TimeSlot.objects.create(
                tenant=tenant,
                name=name,
                start_time=start_time,
                end_time=end_time,
                is_break=is_break
            )
            messages.success(request, "Time slot created successfully.")
            return redirect('timetable:manage_time_slots')
            
    time_slots = TimeSlot.objects.for_tenant(tenant).order_by('start_time')
    
    context = {
        'tenant': tenant,
        'time_slots': time_slots,
        'module_name': 'Timetable',
    }
    return render(request, 'modules/timetable/time_slot_list.html', context)

@login_required
def delete_time_slot(request, slot_id):
    """Delete a time slot."""
    if not is_staff_or_principal(request.user):
        messages.error(request, "Permission denied.")
        return redirect('timetable:dashboard')
        
    tenant = request.user.tenant
    slot = get_object_or_404(TimeSlot, id=slot_id, tenant=tenant)
    
    if request.method == 'POST':
        slot.delete()
        messages.success(request, "Time slot deleted.")
        
    return redirect('timetable:manage_time_slots')

@login_required
def section_timetable(request, section_id):
    """View timetable for a specific section."""
    tenant = request.user.tenant
    section = get_object_or_404(Section, id=section_id, tenant=tenant)
    
    # Get active session
    active_session = AcademicSession.objects.for_tenant(tenant).filter(is_active=True).first()
    
    if not active_session:
        messages.warning(request, "No active academic session found.")
        return redirect('timetable:dashboard')
        
    # Get timetable entries
    entries = SectionTimetable.objects.for_tenant(tenant).filter(
        section=section,
        academic_session=active_session
    ).select_related('time_slot', 'teacher').order_by('time_slot__start_time')
    
    # Organize by day and time slot
    timetable_grid = {}
    time_slots = TimeSlot.objects.for_tenant(tenant).order_by('start_time')
    days = SectionTimetable.DAYS_OF_WEEK
    
    for day_code, day_name in days:
        timetable_grid[day_code] = {
            'name': day_name,
            'slots': {}
        }
        for slot in time_slots:
            timetable_grid[day_code]['slots'][slot.id] = None
            
    for entry in entries:
        timetable_grid[entry.day_of_week]['slots'][entry.time_slot.id] = entry
        
    context = {
        'tenant': tenant,
        'section': section,
        'time_slots': time_slots,
        'timetable_grid': timetable_grid,
        'module_name': 'Timetable',
    }
    return render(request, 'modules/timetable/section_view.html', context)

@login_required
def manage_timetable(request, section_id):
    """Manage (Create/Edit) timetable for a section."""
    # Only Principal/Staff should access
    if request.user.role.name not in ['Principal', 'Staff']:
        messages.error(request, "Permission denied.")
        return redirect('timetable:dashboard')
        
    tenant = request.user.tenant
    section = get_object_or_404(Section, id=section_id, tenant=tenant)
    active_session = AcademicSession.objects.for_tenant(tenant).filter(is_active=True).first()
    
    if not active_session:
        messages.error(request, "Active academic session required.")
        return redirect('timetable:dashboard')

    if request.method == 'POST':
        # Process bulk update/create
        # Format: slot_{day}_{slot_id}_subject, slot_{day}_{slot_id}_teacher
        days = [d[0] for d in SectionTimetable.DAYS_OF_WEEK]
        time_slots = TimeSlot.objects.for_tenant(tenant)
        
        count = 0
        for day in days:
            for slot in time_slots:
                subject = request.POST.get(f"slot_{day}_{slot.id}_subject")
                teacher_id = request.POST.get(f"slot_{day}_{slot.id}_teacher")
                
                if subject: # creating or updating
                    SectionTimetable.objects.update_or_create(
                        tenant=tenant,
                        section=section,
                        academic_session=active_session,
                        day_of_week=day,
                        time_slot=slot,
                        defaults={
                            'subject': subject,
                            'teacher_id': teacher_id if teacher_id else None
                        }
                    )
                    count += 1
                else:
                    # check if we need to delete existing
                    SectionTimetable.objects.filter(
                        tenant=tenant,
                        section=section,
                        academic_session=active_session,
                        day_of_week=day,
                        time_slot=slot
                    ).delete()
                    
        messages.success(request, f"Timetable updated for {section.full_name}")
        return redirect('timetable:section_timetable', section_id=section.id)

    # Get existing data to pre-fill form
    entries = SectionTimetable.objects.for_tenant(tenant).filter(
        section=section,
        academic_session=active_session
    )
    existing_data = {}
    for entry in entries:
        existing_data[f"{entry.day_of_week}_{entry.time_slot.id}"] = entry

    time_slots = TimeSlot.objects.for_tenant(tenant).order_by('start_time')
    teachers = CustomUser.objects.filter(tenant=tenant, role__name='Teacher', is_active=True)
    
    context = {
        'tenant': tenant,
        'section': section,
        'time_slots': time_slots,
        'days': SectionTimetable.DAYS_OF_WEEK,
        'existing_data': existing_data,
        'teachers': teachers,
        'module_name': 'Timetable',
    }
    return render(request, 'modules/timetable/manage_form.html', context)
