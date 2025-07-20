from django.db import models
from django.conf import settings
from django.utils import timezone

class UnderwritingDecision(models.Model):
    policy = models.OneToOneField(InsurancePolicy, on_delete=models.CASCADE)
    approved = models.BooleanField()
    decision_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.policy.policy_number} - {'Approved' if self.approved else 'Rejected'}"
