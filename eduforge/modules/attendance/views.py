"""
Attendance module views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
import csv

from .models import Class, Student, Attendance
from core.users.models import CustomUser


def teacher_or_principal_required(view_func):
    """Decorator to restrict access to Teachers and Principals only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        
        user_role = request.user.role.name if request.user.role else None
        if user_role not in ['Teacher', 'Principal']:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('attendance:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def index(request):
    """
    Attendance module home page.
    """
    tenant = request.user.tenant
    user_role = request.user.role.name if request.user.role else None
    
    today = timezone.now().date()
    
    # Initialize stats with default values
    total_students = 0
    present_count = 0
    absent_count = 0
    late_count = 0
    attendance_percentage = 0
    absent_students = []
    
    if user_role == 'Student':
        # Student View: specific to the logged-in student
        try:
            # Try to get student profile from legacy or academic enrollment
            student_profile = Student.objects.filter(user=request.user, is_active=True).first()
            if student_profile:
                # Personal stats
                my_attendance = Attendance.objects.filter(student=student_profile)
                total_days = my_attendance.count()
                if total_days > 0:
                    my_present = my_attendance.filter(status='present').count()
                    attendance_percentage = round((my_present / total_days * 100), 2)
                    present_count = my_present
                    absent_count = my_attendance.filter(status='absent').count()
                    late_count = my_attendance.filter(status='late').count()
                    total_students = 1  # Represents "Me"
        except Exception:
            pass
            
    elif user_role == 'Teacher':
        # Teacher View: restricted to assigned classes/sections
        # Get legacy classes
        teacher_classes = Class.objects.for_tenant(tenant).filter(class_teacher=request.user, is_active=True)
        # Get academic sections (if module exists)
        try:
            from modules.academic.models import Section, Enrollment
            active_sections = Section.objects.for_tenant(tenant).filter(class_teacher=request.user)
            # Combine queries or counts
            # For dashboard high-level stats, we'll aggregate
            
            # 1. Total Students in my classes
            legacy_student_ids = Student.objects.filter(class_assigned__in=teacher_classes, is_active=True).values_list('id', flat=True)
            section_student_ids = Enrollment.objects.filter(section__in=active_sections, is_active=True).values_list('student__id', flat=True) # logic might differ as Enrollment links to User not Student model directly usually, but Student model links to User. 
            # Note: Student model is the central point for Attendance currently.
            
            # Let's verify Student model usage. 
            # The Student model in attendance app is the "Profile". 
            # Enrollments link to User. 
            # We need to find Student profiles corresponding to Enrollments.
            
            all_student_users = []
            
            # Legacy students
            legacy_users = Student.objects.filter(class_assigned__in=teacher_classes, is_active=True).values_list('user__id', flat=True)
            
            # New section students
            section_users = Enrollment.objects.filter(section__in=active_sections, is_active=True).values_list('student__id', flat=True)
            
            # Combine unique user IDs
            all_related_user_ids = set(list(legacy_users) + list(section_users))
            total_students = len(all_related_user_ids)
            
            # 2. Today's Attendance for these students
            today_recs = Attendance.objects.for_tenant(tenant).filter(
                date=today,
                student__user__id__in=all_related_user_ids
            )
            present_count = today_recs.filter(status='present').count()
            absent_count = today_recs.filter(status='absent').count()
            late_count = today_recs.filter(status='late').count()
            
            if total_students > 0:
                attendance_percentage = round((present_count / total_students * 100), 2)
                
            # 3. Absent students list
            absent_students = Student.objects.filter(
                user__id__in=all_related_user_ids,
                attendance_records__date=today,
                attendance_records__status='absent'
            ).select_related('user')[:10]
            
        except ImportError:
            # Fallback for legacy only
            total_students = Student.objects.filter(class_assigned__in=teacher_classes, is_active=True).count()
            today_recs = Attendance.objects.filter(student__class_assigned__in=teacher_classes, date=today)
            present_count = today_recs.filter(status='present').count()
            absent_count = today_recs.filter(status='absent').count()
            late_count = today_recs.filter(status='late').count()
            
            if total_students > 0:
                attendance_percentage = round((present_count / total_students * 100), 2)
                
            absent_students = Student.objects.filter(
                class_assigned__in=teacher_classes,
                attendance_records__date=today,
                attendance_records__status='absent'
            ).select_related('user')[:10]

        # Get recently attended classes (history)
        recent_history = []
        try:
            # Fetch recent attendance records marked by this teacher
            # We fetch a larger chunk to ensure we get enough unique (date, class) groups
            recent_logs = Attendance.objects.for_tenant(tenant).filter(
                marked_by=request.user
            ).select_related(
                'student__class_assigned',
                'student__enrollment__section'
            ).order_by('-updated_at')[:200]

            seen_groups = set()
            for log in recent_logs:
                # Identify the class/section
                class_name = "Unknown Class"
                class_id = None
                is_academic = False
                
                if log.student.enrollment and log.student.enrollment.section:
                    # New Academic Structure
                    class_name = log.student.enrollment.section.full_name
                    class_id = log.student.enrollment.section.id
                    is_academic = True
                elif log.student.class_assigned:
                    # Legacy Structure
                    class_name = log.student.class_assigned.name
                    if log.student.class_assigned.section:
                        class_name += f" - {log.student.class_assigned.section}"
                    class_id = log.student.class_assigned.id
                    is_academic = False
                else:
                    continue

                # Group Key: Date + Class
                group_key = (log.date, class_name)
                
                if group_key not in seen_groups:
                    seen_groups.add(group_key)
                    recent_history.append({
                        'class_name': class_name,
                        'date': log.date,
                        'id': class_id,
                        'is_academic': is_academic
                    })
                    
                if len(recent_history) >= 5:
                    break
        except Exception as e:
            # Fallback or error handling
            print(f"Error fetching recent history: {e}")
            pass

    else:
        # Principal/Admin View: Global stats (existing logic)
        recent_history = [] # Not needed for Principal yet, or could add similar logic
        total_students = Student.objects.for_tenant(tenant).filter(is_active=True).count()
        today_attendance = Attendance.objects.for_tenant(tenant).filter(date=today)
        present_count = today_attendance.filter(status='present').count()
        absent_count = today_attendance.filter(status='absent').count()
        late_count = today_attendance.filter(status='late').count()
        
        attendance_percentage = round((present_count / total_students * 100), 2) if total_students > 0 else 0
        
        absent_students = Student.objects.filter(
            attendance_records__date=today,
            attendance_records__status='absent',
            is_active=True
        ).select_related('user', 'class_assigned')[:10]
        
    # Get user's classes if teacher (for list display)
    user_classes = []
    if user_role == 'Teacher':
        # Legacy Classes
        legacy_classes = Class.objects.for_tenant(tenant).filter(
            class_teacher=request.user,
            is_active=True
        )
        
        # New Academic Sections
        try:
            from modules.academic.models import Section
            academic_sections = Section.objects.for_tenant(tenant).filter(
                class_teacher=request.user
            )
        except ImportError:
            academic_sections = []
            
        # Combine for display - generic structure
        for lc in legacy_classes:
            user_classes.append({
                'id': lc.id,
                'name': lc.name,
                'section': lc.section,
                'student_count': lc.get_student_count(),
                'type': 'legacy'
            })
            
        for section in academic_sections:
            user_classes.append({
                'id': section.id,
                'name': section.class_obj.name, 
                'section': section.name,   # just 'A', 'B' etc
                'student_count': section.enrollments.filter(is_active=True).count(), # approximated
                'type': 'academic'
            })

    context = {
        'tenant': tenant,
        'user': request.user,
        'user_role': user_role,
        'module_name': 'Attendance',
        'total_students': total_students,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_percentage': attendance_percentage,
        'absent_students': absent_students,
        'user_classes': user_classes,
        'recent_history': recent_history if 'recent_history' in locals() else [],
        'today': today,
    }
    
    return render(request, 'modules/attendance/index.html', context)


@teacher_or_principal_required
def select_class(request):
    """
    Select a class/section to mark attendance.
    Shows both legacy classes and new academic sections.
    """
    tenant = request.user.tenant
    user_role = request.user.role.name if request.user.role else None
    
    # Get legacy classes based on role
    if user_role == 'Principal':
        classes = Class.objects.for_tenant(tenant).filter(is_active=True)
    else:  # Teacher
        classes = Class.objects.for_tenant(tenant).filter(
            class_teacher=request.user,
            is_active=True
        )
    
    # NEW: Get academic sections (if academic module is available)
    academic_sections = []
    try:
        from modules.academic.models import Section, AcademicSession
        
        # Get active academic session
        active_session = AcademicSession.objects.for_tenant(tenant).filter(is_active=True).first()
        
        if active_session:
            if user_role == 'Principal':
                # Principal can see all sections
                academic_sections = Section.objects.for_tenant(tenant).filter(
                    class_obj__academic_session=active_session
                ).select_related('class_obj', 'class_teacher')
            else:  # Teacher
                # Teacher can see sections they teach
                academic_sections = Section.objects.for_tenant(tenant).filter(
                    class_obj__academic_session=active_session,
                    class_teacher=request.user
                ).select_related('class_obj', 'class_teacher')
    except ImportError:
        # Academic module not installed
        pass
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'classes': classes,
        'academic_sections': academic_sections,
        'module_name': 'Attendance',
    }
    
    return render(request, 'modules/attendance/select_class.html', context)


@teacher_or_principal_required
def mark_attendance(request, class_id):
    """
    Mark attendance for students in a class/section.
    Supports both legacy classes and new academic sections.
    """
    tenant = request.user.tenant
    
    # Determine if this is a legacy class or academic section
    # Academic section IDs are integers, legacy class IDs are UUIDs
    is_academic_section = False
    try:
        # Try to parse as integer (academic section)
        section_id = int(class_id)
        is_academic_section = True
    except ValueError:
        # It's a UUID (legacy class)
        is_academic_section = False
    
    if is_academic_section:
        # NEW: Handle academic section
        from modules.academic.models import Section, Enrollment
        
        section = get_object_or_404(Section, id=section_id, tenant=tenant)
        class_obj = None  # Not using legacy class
        
        # Check permissions
        user_role = request.user.role.name if request.user.role else None
        if user_role == 'Teacher' and section.class_teacher != request.user:
            messages.error(request, 'You do not have permission to mark attendance for this section.')
            return redirect('attendance:select_class')
        
        # Get students from enrollments
        enrollments = Enrollment.objects.for_tenant(tenant).filter(
            section=section,
            is_active=True
        ).select_related('student').order_by('roll_number')
        
        # Create student list with enrollment info
        students_data = []
        for enrollment in enrollments:
            students_data.append({
                'id': enrollment.student.id,
                'user': enrollment.student,
                'roll_number': enrollment.roll_number,
                'name': enrollment.student.get_full_name() or enrollment.student.username,
                'enrollment': enrollment
            })
        
        display_name = section.full_name
        
    else:
        # LEGACY: Handle old class structure
        class_obj = get_object_or_404(Class, id=class_id, tenant=tenant)
        section = None
        
        # Check permissions
        user_role = request.user.role.name if request.user.role else None
        if user_role == 'Teacher' and class_obj.class_teacher != request.user:
            messages.error(request, 'You do not have permission to mark attendance for this class.')
            return redirect('attendance:select_class')
        
        # Get students from legacy Student model
        students = Student.objects.for_tenant(tenant).filter(
            class_assigned=class_obj,
            is_active=True
        ).select_related('user').order_by('roll_number')
        
        # Format for template consistency
        students_data = []
        for student in students:
            students_data.append({
                'id': student.user.id,
                'user': student.user,
                'roll_number': student.roll_number,
                'name': student.user.get_full_name() or student.user.username,
                'student_obj': student
            })
        
        display_name = str(class_obj)
    
    # Get date from query params or use today
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        attendance_date = timezone.now().date()
    
    # Get existing attendance records for this date
    existing_attendance = {}
    if is_academic_section:
        # Query by student user IDs for academic sections
        student_ids = [s['id'] for s in students_data]
        attendance_records = Attendance.objects.filter(
            tenant=tenant,
            student__user_id__in=student_ids,
            date=attendance_date
        )
        for record in attendance_records:
            existing_attendance[str(record.student.user.id)] = record.status
    else:
        # Query by legacy class for old structure
        attendance_records = Attendance.objects.for_tenant(tenant).filter(
            student__class_assigned=class_obj,
            date=attendance_date
        )
        for record in attendance_records:
            existing_attendance[str(record.student.user.id)] = record.status
    
    if request.method == 'POST':
        # Process attendance submission
        marked_count = 0
        
        for student_data in students_data:
            status = request.POST.get(f'status_{student_data["id"]}')
            if status in ['present', 'absent', 'late', 'excused']:
                # Find or create Student record (for backward compatibility)
                if is_academic_section:
                    # For academic sections, ensure Student record exists
                    student_obj, created = Student.objects.get_or_create(
                        tenant=tenant,
                        user=student_data['user'],
                        defaults={
                            'roll_number': student_data['roll_number'],
                            'admission_number': f"ADM-{student_data['user'].id}",
                            'enrollment': student_data.get('enrollment')
                        }
                    )
                else:
                    student_obj = student_data['student_obj']
                
                # Update or create attendance record
                attendance, created = Attendance.objects.update_or_create(
                    tenant=tenant,
                    student=student_obj,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': request.user,
                    }
                )
                marked_count += 1
        
        messages.success(request, f'Attendance marked for {marked_count} students on {attendance_date}.')
        return redirect('attendance:index')
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'class_obj': class_obj,
        'section': section,
        'display_name': display_name,
        'students_data': students_data,
        'attendance_date': attendance_date,
        'existing_attendance': existing_attendance,
        'module_name': 'Attendance',
        'is_academic_section': is_academic_section,
    }
    
    return render(request, 'modules/attendance/mark_attendance.html', context)


@teacher_or_principal_required
def edit_attendance(request, class_id):
    """
    Edit attendance for a specific class and date.
    """
    # This uses the same view as mark_attendance since it handles both create and update
    return mark_attendance(request, class_id)


@login_required
def student_summary(request, student_id=None):
    """
    View attendance summary for a student.
    """
    tenant = request.user.tenant
    user_role = request.user.role.name if request.user.role else None
    
    # Determine which student to show
    if student_id:
        student = get_object_or_404(Student, id=student_id, tenant=tenant)
        # Check permissions
        if user_role == 'Student' and student.user != request.user:
            messages.error(request, 'You can only view your own attendance.')
            return redirect('attendance:index')
    else:
        # If no student_id, show current user's attendance (if they're a student)
        if user_role != 'Student':
            messages.error(request, 'Please select a student.')
            return redirect('attendance:index')
        student = get_object_or_404(Student, user=request.user, tenant=tenant)
    
    # Get date range from query params
    end_date = timezone.now().date()
    start_date = end_date.replace(day=1)  # Current month
    
    if request.GET.get('start_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if request.GET.get('end_date'):
        try:
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        student=student,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')
    
    # Calculate statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = attendance_records.filter(status='absent').count()
    late_days = attendance_records.filter(status='late').count()
    excused_days = attendance_records.filter(status='excused').count()
    
    attendance_percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'student': student,
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'excused_days': excused_days,
        'attendance_percentage': attendance_percentage,
        'module_name': 'Attendance',
    }
    
    return render(request, 'modules/attendance/student_summary.html', context)


@teacher_or_principal_required
def class_report(request, class_id=None):
    """
    View attendance report for a class.
    """
    tenant = request.user.tenant
    user_role = request.user.role.name if request.user.role else None
    
    # Get classes based on role
    if user_role == 'Principal':
        classes = Class.objects.for_tenant(tenant).filter(is_active=True)
    else:  # Teacher
        classes = Class.objects.for_tenant(tenant).filter(
            class_teacher=request.user,
            is_active=True
        )
    
    class_obj = None
    students_data = []
    
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id, tenant=tenant)
        
        # Check permissions
        if user_role == 'Teacher' and class_obj.class_teacher != request.user:
            messages.error(request, 'You do not have permission to view this class report.')
            return redirect('attendance:class_report')
        
        # Get date range
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1)  # Current month
        
        if request.GET.get('start_date'):
            try:
                start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if request.GET.get('end_date'):
            try:
                end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Get students and their attendance
        students = Student.objects.for_tenant(tenant).filter(
            class_assigned=class_obj,
            is_active=True
        ).select_related('user').order_by('roll_number')
        
        for student in students:
            attendance_records = Attendance.objects.filter(
                student=student,
                date__gte=start_date,
                date__lte=end_date
            )
            
            total_days = attendance_records.count()
            present_days = attendance_records.filter(status='present').count()
            absent_days = attendance_records.filter(status='absent').count()
            late_days = attendance_records.filter(status='late').count()
            
            percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
            
            students_data.append({
                'student': student,
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'late_days': late_days,
                'percentage': percentage,
            })
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'classes': classes,
        'class_obj': class_obj,
        'students_data': students_data,
        'start_date': start_date if class_id else None,
        'end_date': end_date if class_id else None,
        'module_name': 'Attendance',
    }
    
    return render(request, 'modules/attendance/class_report.html', context)


@teacher_or_principal_required
def export_report_csv(request, class_id):
    """
    Export class attendance report as CSV.
    """
    tenant = request.user.tenant
    class_obj = get_object_or_404(Class, id=class_id, tenant=tenant)
    
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date.replace(day=1)
    
    if request.GET.get('start_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if request.GET.get('end_date'):
        try:
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{class_obj.name}_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Student Name', 'Total Days', 'Present', 'Absent', 'Late', 'Attendance %'])
    
    # Get students and their attendance
    students = Student.objects.for_tenant(tenant).filter(
        class_assigned=class_obj,
        is_active=True
    ).select_related('user').order_by('roll_number')
    
    for student in students:
        attendance_records = Attendance.objects.filter(
            student=student,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status='present').count()
        absent_days = attendance_records.filter(status='absent').count()
        late_days = attendance_records.filter(status='late').count()
        
        percentage = round((present_days / total_days * 100), 2) if total_days > 0 else 0
        
        writer.writerow([
            student.roll_number,
            student.user.get_full_name(),
            total_days,
            present_days,
            absent_days,
            late_days,
            f'{percentage}%'
        ])
    
    return response
