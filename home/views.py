from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    modules = [
        {"name": "Users", "url": "/users/", "description": "Manage user accounts and profiles."},
        {"name": "Access Control", "url": "/accesscontrol/", "description": "Manage roles and permissions."},
        {"name": "Purchase", "url": "/purchase/", "description": "Handle requisitions and purchases."},
        {"name": "E-Documents", "url": "/edocuments/", "description": "Digitize and manage documents."},
        {"name": "Digital-Insurance", "url": "/digitalinsurance/", "description": "Manage digital insurance records."},
        {"name": "Settings", "url": "/settings/", "description": "Configure system settings."},
        {"name": "Reports", "url": "/reports/", "description": "View and download reports."},
    ]
    return render(request, 'home/home.html', {
        "user": request.user,
        "modules": modules,
    })
