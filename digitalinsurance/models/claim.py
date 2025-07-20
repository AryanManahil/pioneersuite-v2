from django.db import models
from django.conf import settings
from django.utils import timezone

# ----------------------------
# 6. Insurance Claim
# ----------------------------
class Claim(models.Model):
    STATUS = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name='claims')
    claim_number = models.CharField(max_length=50, unique=True)
    claim_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS, default='submitted')
    description = models.TextField()
    amount_claimed = models.DecimalField(max_digits=10, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.claim_number} - {self.policy.policy_number}"

