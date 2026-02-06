"""
Timetable module views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    """
    Timetable module home page.
    """
    tenant = request.user.tenant
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'module_name': 'Timetable',
    }
    
    return render(request, 'modules/timetable/index.html', context)


@login_required
def create_timetable(request):
    """
    Create new timetable.
    """
    messages.info(request, 'Timetable creation feature coming soon!')
    return redirect('timetable:index')


@login_required
def view_schedule(request):
    """
    View class schedules.
    """
    messages.info(request, 'Schedule viewing feature coming soon!')
    return redirect('timetable:index')
