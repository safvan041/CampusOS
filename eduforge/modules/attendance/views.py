"""
Attendance module views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    """
    Attendance module home page.
    """
    tenant = request.user.tenant
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'module_name': 'Attendance',
    }
    
    return render(request, 'modules/attendance/index.html', context)


@login_required
def mark_attendance(request):
    """
    Mark attendance for students.
    """
    messages.info(request, 'Attendance marking feature coming soon!')
    return redirect('attendance:index')


@login_required
def view_reports(request):
    """
    View attendance reports.
    """
    messages.info(request, 'Attendance reports feature coming soon!')
    return redirect('attendance:index')
