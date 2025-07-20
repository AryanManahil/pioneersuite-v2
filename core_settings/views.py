# core_settings/views.py

from django.shortcuts import render
from .models import Company, Branch, Department, Product

def settings_home(request):
    return render(request, 'core_settings/home.html')

def company_list(request):
    companies = Company.objects.all()
    return render(request, 'core_settings/company_list.html', {'companies': companies})

def branch_list(request):
    branches = Branch.objects.all()
    return render(request, 'core_settings/branch_list.html', {'branches': branches})

def department_list(request):
    departments = Department.objects.all()
    return render(request, 'core_settings/department_list.html', {'departments': departments})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'core_settings/product_list.html', {'products': products})

