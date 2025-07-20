from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dihome_home(request):
    return render(request, 'digitalinsurance/dihome.html')

@login_required
def product(request):
    return render(request, 'digitalinsurance/product.html')

@login_required
def policy(request):
    return render(request, 'digitalinsurance/policy.html')

@login_required
def claim(request):
    return render(request, 'digitalinsurance/claim.html')

@login_required
def bill(request):
    return render(request, 'digitalinsurance/bill.html')

@login_required
def digital_insurance_landing(request):
    return render(request, "digitalinsurance/landing.html")

@login_required
def admin_dashboard(request):
    return render(request, "digitalinsurance/admin_dashboard.html")


