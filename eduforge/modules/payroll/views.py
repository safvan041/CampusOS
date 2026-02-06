"""
Payroll module views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def index(request):
    """
    Payroll module home page.
    """
    tenant = request.user.tenant
    
    context = {
        'tenant': tenant,
        'user': request.user,
        'module_name': 'Payroll',
    }
    
    return render(request, 'modules/payroll/index.html', context)


@login_required
def manage_salaries(request):
    """
    Manage employee salaries.
    """
    messages.info(request, 'Salary management feature coming soon!')
    return redirect('payroll:index')


@login_required
def generate_payslips(request):
    """
    Generate payslips.
    """
    messages.info(request, 'Payslip generation feature coming soon!')
    return redirect('payroll:index')
