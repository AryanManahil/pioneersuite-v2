# digitalinsurance/views/common.py
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_superuser:
        return redirect('digitalinsurance:admin_dashboard')
    else:
        return redirect('digitalinsurance:customer_dashboard')
