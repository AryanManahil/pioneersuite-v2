from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from digitalinsurance.models.customer import CustomerProfile
from digitalinsurance.models.policy import InsurancePolicy  # ✅ Add this import

# ✅ Helper to restrict admin/staff access
def is_staff_or_superuser(user):
    """Check if user is staff or superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ✅ Admin: View all customer profiles
@user_passes_test(is_staff_or_superuser)
@login_required
def all_customer_profiles(request):
    profiles = CustomerProfile.objects.select_related('user').all()
    return render(request, 'digitalinsurance/all_customer_profiles.html', {
        'profiles': profiles
    })


# ✅ Admin: Approve or reject customer profile
@user_passes_test(is_staff_or_superuser)
@login_required
def admin_customer_detail(request, pk):
    profile = get_object_or_404(CustomerProfile.objects.select_related('user'), pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            profile.status = 'Approved'
        elif action == 'reject':
            profile.status = 'Rejected'
        profile.save()
        return redirect('digitalinsurance:admin_customer_detail', pk=pk)

    return render(request, 'digitalinsurance/customer_profile_view.html', {
        'profile': profile,
        'is_admin_view': True
    })


# ✅ Admin: View all policies in the system
@user_passes_test(is_staff_or_superuser)
@login_required
def all_policies(request):
    policies = InsurancePolicy.objects.select_related('user', 'product').order_by('-created_at')
    return render(request, 'digitalinsurance/admin_policies.html', {
        'policies': policies
    })
