from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from digitalinsurance.models import Product, Plan, TravelPurpose
from digitalinsurance.forms import ProductForm


# Utility function to check if the user is NOT in the 'Customer' group
def not_customer(user):
    return not user.groups.filter(name='Customer').exists()


# ✅ View: List all insurance products (accessible by all logged-in users)
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'digitalinsurance/product_list.html', {'products': products})


# ✅ View: Create a new product (restricted to Admin/Manager/User)
@login_required
@user_passes_test(not_customer)
def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('digitalinsurance:product_list')
    return render(request, 'digitalinsurance/product_form.html', {'form': form})


# ✅ View: Update an existing product (restricted to Admin/Manager/User)
@login_required
@user_passes_test(not_customer)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('digitalinsurance:product_list')
    return render(request, 'digitalinsurance/product_form.html', {'form': form})


# ✅ View: Delete a product (restricted to Admin/Manager/User)
@login_required
@user_passes_test(not_customer)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('digitalinsurance:product_list')
    return render(request, 'digitalinsurance/product_confirm_delete.html', {'product': product})


# ✅ View: View product details with grouped Travel Purposes (accessible by all logged-in users)
@login_required
def product_detail(request, code):
    product = get_object_or_404(Product, code=code)

    # Fetch all TravelPurpose objects related to the product's plans
    purposes = TravelPurpose.objects.filter(plan__product=product).select_related("plan")

    # Group plans by purpose_type
    purpose_map = {}
    for purpose in purposes:
        key = purpose.purpose_type
        if key not in purpose_map:
            purpose_map[key] = []
        purpose_map[key].append(purpose.plan)

    return render(request, "digitalinsurance/product_detail.html", {
        "product": product,
        "purpose_map": purpose_map,
    })
