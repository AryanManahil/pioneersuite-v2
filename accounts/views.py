from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # 🔧 FIXED: no .username on custom user, use .email
            print("DEBUG: Logged in user:", user.email)
            print("DEBUG: Groups:", list(user.groups.values_list('name', flat=True)))

            department = getattr(user, 'department', None)
            department_name = getattr(department, 'name', None)
            print("DEBUG: Department:", department_name)

            if user.groups.filter(name='Customer').exists() and department_name == 'Customer Care':
                print("✅ Redirecting to customer_dashboard")
                return redirect('digitalinsurance:customer_dashboard')

            print("⏩ Default redirect to home")
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form, 'debug_test': 'CUSTOM LOGIN VIEW ACTIVE'})
