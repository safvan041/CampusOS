"""
Views for Academic module.
Handles academic session, class, section, and enrollment management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from .models import AcademicSession, Class, Section, Enrollment
from core.users.models import CustomUser


def principal_required(view_func):
    """Decorator to restrict access to Principal only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        
        user_role = request.user.role.name if request.user.role else None
        if user_role != 'Principal':
            messages.error(request, 'Only Principals can access Academic Setup.')
            return redirect('auth:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    """Academic Setup dashboard - overview of all academic data."""
    tenant = request.user.tenant
    
    # Get active session
    active_session = AcademicSession.objects.for_tenant(tenant).filter(is_active=True).first()
    
    # Get statistics
    total_sessions = AcademicSession.objects.for_tenant(tenant).count()
    total_classes = Class.objects.for_tenant(tenant).count()
    total_sections = Section.objects.for_tenant(tenant).count()
    total_enrollments = Enrollment.objects.for_tenant(tenant).filter(is_active=True).count()
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'active_session': active_session,
        'total_sessions': total_sessions,
        'total_classes': total_classes,
        'total_sections': total_sections,
        'total_enrollments': total_enrollments,
        'module_name': 'Academic Setup',
    }
    
    return render(request, 'modules/academic/dashboard.html', context)


# Academic Session Views
@principal_required
def session_list(request):
    """List all academic sessions."""
    tenant = request.user.tenant
    sessions = AcademicSession.objects.for_tenant(tenant).all()
    
    context = {
        'tenant': tenant,
        'sessions': sessions,
        'module_name': 'Academic Sessions',
    }
    
    return render(request, 'modules/academic/session_list.html', context)


@principal_required
def session_create(request):
    """Create a new academic session."""
    tenant = request.user.tenant
    
    if request.method == 'POST':
        name = request.POST.get('name')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        is_active = request.POST.get('is_active') == 'on'
        
        session = AcademicSession.objects.create(
            tenant=tenant,
            name=name,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active
        )
        
        messages.success(request, f'Academic session "{name}" created successfully!')
        return redirect('academic:session_list')
    
    return render(request, 'modules/academic/session_form.html', {
        'tenant': tenant,
        'module_name': 'Create Academic Session',
    })


@principal_required
def session_edit(request, pk):
    """Edit an existing academic session."""
    tenant = request.user.tenant
    session = get_object_or_404(AcademicSession, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        session.name = request.POST.get('name')
        session.start_date = request.POST.get('start_date')
        session.end_date = request.POST.get('end_date')
        session.is_active = request.POST.get('is_active') == 'on'
        session.save()
        
        messages.success(request, f'Academic session "{session.name}" updated successfully!')
        return redirect('academic:session_list')
    
    return render(request, 'modules/academic/session_form.html', {
        'tenant': tenant,
        'session': session,
        'module_name': 'Edit Academic Session',
    })


# Class Views
@principal_required
def class_list(request):
    """List all classes."""
    tenant = request.user.tenant
    classes = Class.objects.for_tenant(tenant).select_related('academic_session').all()
    
    context = {
        'tenant': tenant,
        'classes': classes,
        'module_name': 'Classes',
    }
    
    return render(request, 'modules/academic/class_list.html', context)


@principal_required
def class_create(request):
    """Create a new class."""
    tenant = request.user.tenant
    sessions = AcademicSession.objects.for_tenant(tenant).all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        session_id = request.POST.get('academic_session')
        description = request.POST.get('description', '')
        
        session = get_object_or_404(AcademicSession, pk=session_id, tenant=tenant)
        
        class_obj = Class.objects.create(
            tenant=tenant,
            academic_session=session,
            name=name,
            description=description
        )
        
        messages.success(request, f'Class "{name}" created successfully!')
        return redirect('academic:class_list')
    
    return render(request, 'modules/academic/class_form.html', {
        'tenant': tenant,
        'sessions': sessions,
        'module_name': 'Create Class',
    })


@principal_required
def class_edit(request, pk):
    """Edit an existing class."""
    tenant = request.user.tenant
    class_obj = get_object_or_404(Class, pk=pk, tenant=tenant)
    sessions = AcademicSession.objects.for_tenant(tenant).all()
    
    if request.method == 'POST':
        class_obj.name = request.POST.get('name')
        session_id = request.POST.get('academic_session')
        class_obj.academic_session = get_object_or_404(AcademicSession, pk=session_id, tenant=tenant)
        class_obj.description = request.POST.get('description', '')
        class_obj.save()
        
        messages.success(request, f'Class "{class_obj.name}" updated successfully!')
        return redirect('academic:class_list')
    
    return render(request, 'modules/academic/class_form.html', {
        'tenant': tenant,
        'class': class_obj,
        'sessions': sessions,
        'module_name': 'Edit Class',
    })


# Section Views
@principal_required
def section_list(request):
    """List all sections."""
    tenant = request.user.tenant
    sections = Section.objects.for_tenant(tenant).select_related('class_obj', 'class_teacher').all()
    
    context = {
        'tenant': tenant,
        'sections': sections,
        'module_name': 'Sections',
    }
    
    return render(request, 'modules/academic/section_list.html', context)


@principal_required
def section_create(request):
    """Create a new section."""
    tenant = request.user.tenant
    classes = Class.objects.for_tenant(tenant).all()
    teachers = CustomUser.objects.filter(tenant=tenant, role__name='Teacher')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        class_id = request.POST.get('class_obj')
        teacher_id = request.POST.get('class_teacher')
        room_number = request.POST.get('room_number', '')
        
        class_obj = get_object_or_404(Class, pk=class_id, tenant=tenant)
        teacher = None
        if teacher_id:
            teacher = get_object_or_404(CustomUser, pk=teacher_id, tenant=tenant)
        
        section = Section.objects.create(
            tenant=tenant,
            class_obj=class_obj,
            name=name,
            class_teacher=teacher,
            room_number=room_number
        )
        
        messages.success(request, f'Section "{section.full_name}" created successfully!')
        return redirect('academic:section_list')
    
    return render(request, 'modules/academic/section_form.html', {
        'tenant': tenant,
        'classes': classes,
        'teachers': teachers,
        'module_name': 'Create Section',
    })


@principal_required
def section_edit(request, pk):
    """Edit an existing section."""
    tenant = request.user.tenant
    section = get_object_or_404(Section, pk=pk, tenant=tenant)
    classes = Class.objects.for_tenant(tenant).all()
    teachers = CustomUser.objects.filter(tenant=tenant, role__name='Teacher')
    
    if request.method == 'POST':
        section.name = request.POST.get('name')
        class_id = request.POST.get('class_obj')
        section.class_obj = get_object_or_404(Class, pk=class_id, tenant=tenant)
        
        teacher_id = request.POST.get('class_teacher')
        section.class_teacher = None
        if teacher_id:
            section.class_teacher = get_object_or_404(CustomUser, pk=teacher_id, tenant=tenant)
        
        section.room_number = request.POST.get('room_number', '')
        section.save()
        
        messages.success(request, f'Section "{section.full_name}" updated successfully!')
        return redirect('academic:section_list')
    
    return render(request, 'modules/academic/section_form.html', {
        'tenant': tenant,
        'section': section,
        'classes': classes,
        'teachers': teachers,
        'module_name': 'Edit Section',
    })


# Enrollment Views
@principal_required
def enrollment_list(request):
    """List all enrollments."""
    tenant = request.user.tenant
    enrollments = Enrollment.objects.for_tenant(tenant).select_related(
        'student', 'section', 'academic_session'
    ).all()
    
    context = {
        'tenant': tenant,
        'enrollments': enrollments,
        'module_name': 'Student Enrollments',
    }
    
    return render(request, 'modules/academic/enrollment_list.html', context)


@principal_required
def enrollment_create(request):
    """Create a new enrollment."""
    tenant = request.user.tenant
    sections = Section.objects.for_tenant(tenant).select_related('class_obj').all()
    students = CustomUser.objects.filter(tenant=tenant, role__name='Student')
    sessions = AcademicSession.objects.for_tenant(tenant).all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        section_id = request.POST.get('section')
        session_id = request.POST.get('academic_session')
        roll_number = request.POST.get('roll_number')
        
        student = get_object_or_404(CustomUser, pk=student_id, tenant=tenant)
        section = get_object_or_404(Section, pk=section_id, tenant=tenant)
        session = get_object_or_404(AcademicSession, pk=session_id, tenant=tenant)
        
        enrollment = Enrollment.objects.create(
            tenant=tenant,
            student=student,
            section=section,
            academic_session=session,
            roll_number=roll_number
        )
        
        messages.success(request, f'Enrolled {student.get_full_name()} in {section.full_name}!')
        return redirect('academic:enrollment_list')
    
    return render(request, 'modules/academic/enrollment_form.html', {
        'tenant': tenant,
        'sections': sections,
        'students': students,
        'sessions': sessions,
        'module_name': 'Create Enrollment',
    })


@principal_required
def enrollment_edit(request, pk):
    """Edit an existing enrollment."""
    tenant = request.user.tenant
    enrollment = get_object_or_404(Enrollment, pk=pk, tenant=tenant)
    sections = Section.objects.for_tenant(tenant).select_related('class_obj').all()
    students = CustomUser.objects.filter(tenant=tenant, role__name='Student')
    sessions = AcademicSession.objects.for_tenant(tenant).all()
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        section_id = request.POST.get('section')
        session_id = request.POST.get('academic_session')
        
        enrollment.student = get_object_or_404(CustomUser, pk=student_id, tenant=tenant)
        enrollment.section = get_object_or_404(Section, pk=section_id, tenant=tenant)
        enrollment.academic_session = get_object_or_404(AcademicSession, pk=session_id, tenant=tenant)
        enrollment.roll_number = request.POST.get('roll_number')
        enrollment.is_active = request.POST.get('is_active') == 'on'
        enrollment.save()
        
        messages.success(request, 'Enrollment updated successfully!')
        return redirect('academic:enrollment_list')
    
    return render(request, 'modules/academic/enrollment_form.html', {
        'tenant': tenant,
        'enrollment': enrollment,
        'sections': sections,
        'students': students,
        'sessions': sessions,
        'module_name': 'Edit Enrollment',
    })


# Subject Views
@principal_required
def subject_list(request):
    """List all subjects."""
    tenant = request.user.tenant
    from .models import Subject
    subjects = Subject.objects.for_tenant(tenant).all()
    
    context = {
        'tenant': tenant,
        'subjects': subjects,
        'module_name': 'Subjects',
    }
    
    return render(request, 'modules/academic/subject_list.html', context)


@principal_required
def subject_create(request):
    """Create a new subject."""
    tenant = request.user.tenant
    from .models import Subject
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code', '')
        
        Subject.objects.create(
            tenant=tenant,
            name=name,
            code=code
        )
        
        messages.success(request, f'Subject "{name}" created successfully!')
        return redirect('academic:subject_list')
    
    # Check if this is a modal/popup request or standalone page
    # For now, we'll assume a standalone page or use the list page for creation if simple
    return render(request, 'modules/academic/subject_form.html', {
        'tenant': tenant,
        'module_name': 'Create Subject',
    })

@principal_required
def subject_delete(request, pk):
    """Delete a subject."""
    tenant = request.user.tenant
    from .models import Subject
    subject = get_object_or_404(Subject, pk=pk, tenant=tenant)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f'Subject "{subject.name}" deleted.')
        
    return redirect('academic:subject_list')
