# digitalinsurance/views/customer_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from digitalinsurance.models.policy import InsurancePolicy

@login_required
def customer_dashboard(request):
    # your dashboard logic
    return render(request, 'digitalinsurance/dashboard.html')

@login_required
def my_policies_view(request):
    policies = InsurancePolicy.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'digitalinsurance/my_policies.html', {'policies': policies})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from digitalinsurance.models.quote import Quote

# digitalinsurance/views.py or wherever your quotes view is

from django.shortcuts import render
from digitalinsurance.models import Quote, InsurancePolicy

def my_quotes_view(request):
    quotes = Quote.objects.filter(customer=request.user)
    policies = InsurancePolicy.objects.filter(quote__in=quotes)
    policies_by_quote_id = {policy.quote.id: policy for policy in policies}

    context = {
        'quotes': quotes,
        'policies_by_quote_id': policies_by_quote_id,
    }
    return render(request, 'digitalinsurance/my_quotes.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from digitalinsurance.models import InsurancePolicy

@login_required
def my_payments_view(request):
    # Fetch only policies with completed payments (i.e., have transaction IDs)
    payments = (
        InsurancePolicy.objects
        .filter(user=request.user, transaction_id__isnull=False)
        .order_by('-created_at')
    )

    context = {
        'payments': payments,
    }
    return render(request, 'digitalinsurance/my_payments.html', context)


@login_required
def my_claims_view(request):
    # Temporary placeholder data or fetch real claim data here
    claims = []  # Replace with actual query later

    return render(request, 'digitalinsurance/my_claims.html', {'claims': claims})

@login_required
def submit_kyc_view(request):
    # implement or placeholder
    pass
