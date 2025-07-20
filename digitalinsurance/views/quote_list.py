from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from digitalinsurance.models import Quote, InsurancePolicy

@login_required
def quote_list(request):
    quotes = Quote.objects.filter(customer=request.user).order_by('-id')
    policies = InsurancePolicy.objects.filter(quote__in=quotes)
    policies_by_quote_id = {policy.quote.id: policy for policy in policies}

    return render(request, 'digitalinsurance/quote_list.html', {
        'quotes': quotes,
        'policies_by_quote_id': policies_by_quote_id,
    })
