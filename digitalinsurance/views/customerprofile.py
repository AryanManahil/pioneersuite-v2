from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from digitalinsurance.models.customer import CustomerProfile
from digitalinsurance.forms import CustomerProfileForm, UserNameForm

@login_required
def customer_profile_edit(request):
    user = request.user
    try:
        profile = user.customerprofile
    except CustomerProfile.DoesNotExist:
        profile = CustomerProfile(user=user)

    if request.method == 'POST':
        user_form = UserNameForm(request.POST, instance=user)
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            profile.status = 'Pending'  # if you want to reset status on edit
            profile.save()
            return redirect('digitalinsurance:customer_profile_view')
    else:
        user_form = UserNameForm(instance=user)
        profile_form = CustomerProfileForm(instance=profile)

    return render(request, 'digitalinsurance/customer_profile_form.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })



@login_required
def customer_profile_view(request):
    profile = request.user.customerprofile
    return render(request, 'digitalinsurance/customer_profile_view.html', {
        'profile': profile,
        'is_admin_view': False  # Default False when customer views their own
    })
