# digitalinsurance/views/admin_dashboard.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def admin_dashboard(request):
    return render(request, 'digitalinsurance/admin_dashboard.html')
