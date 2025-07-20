from django.db import models
from django.conf import settings
from django.utils import timezone

class ReinsuranceContract(models.Model):
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name='reinsurances')
    reinsurer = models.CharField(max_length=100)
    share_percent = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 60.00
    contract_ref = models.CharField(max_length=100)
    agreement_date = models.DateField()

    def __str__(self):
        return f"{self.policy.policy_number} - {self.reinsurer}"
