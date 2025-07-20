# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import User  # Assuming you have a User model
from .forms import UserForm  # Create a UserForm for user creation and editing
from django.shortcuts import render

# List all users
def user_list(request):
    users = User.objects.all()  # Fetch all users from the database
    return render(request, 'users/user_list.html', {'users': users})


# Create a new user
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from .forms import UserForm

from core_settings.models import Department, Branch  # Adjust if needed


def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ Set password securely
            user.set_password(form.cleaned_data['password'])
            user.is_staff = True

            # ✅ Get or create Customer Care Branch
            branch, _ = Branch.objects.get_or_create(name="Customer Care")

            # ✅ Get or create Customer Care Department under that branch
            department, _ = Department.objects.get_or_create(
                name="Customer Care",
                branch=branch
            )
            user.department = department

            user.save()

            # ✅ Assign to 'Customer' group (create if missing)
            customer_group, _ = Group.objects.get_or_create(name='Customer')
            user.groups.add(customer_group)

            # ✅ Auto login
            login(request, user)

            messages.success(request, 'Registration successful! You are now logged in.')
            return redirect('digitalinsurance:customer_dashboard')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})



# Edit an existing user
def user_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # Redirect to the user list after editing
    else:
        form = UserForm(instance=user)

    return render(request, 'users/user_form.html', {'form': form, 'user': user})


# Delete a user
def user_delete(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        user.delete()
        return redirect('user_list')  # Redirect to the user list after deletion

    return render(request, 'users/user_confirm_delete.html', {'user': user})



from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('users:activate_account', kwargs={'uidb64': uid, 'token': token})
    )
    message = f"Hi {user.email}, click the link to activate your account:\n{activation_link}"
    send_mail('Activate Your Account', message, None, [user.email])


from django.utils.encoding import force_str

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid or expired activation link.')
        return redirect('login')

