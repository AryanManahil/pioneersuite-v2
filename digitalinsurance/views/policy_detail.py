from django.shortcuts import render, get_object_or_404
from digitalinsurance.models.policy import InsurancePolicy

def policy_detail(request, policy_id):
    policy = get_object_or_404(InsurancePolicy, id=policy_id, user=request.user)
    return render(request, 'digitalinsurance/policy_detail.html', {'policy': policy})
