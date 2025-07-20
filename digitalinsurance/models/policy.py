from django.db import models
from django.conf import settings
from django.utils import timezone
from digitalinsurance.models.product import Product,ProductField
from digitalinsurance.models.quote import Quote


class InsurancePolicy(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quote = models.OneToOneField(Quote, on_delete=models.SET_NULL, null=True, blank=True)
    policy_number = models.CharField(max_length=50, unique=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    transaction_method = models.CharField(max_length=50, default='SSLCommerz')
    transaction_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.policy_number}"


# --------------------------------------------------------
# 4. Submitted Field Values for Policy (Dynamic Key-Value)
# --------------------------------------------------------
class PolicyData(models.Model):
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name="fields")
    field = models.ForeignKey(ProductField, on_delete=models.CASCADE)
    value = models.TextField()  # Store all types as string

    def __str__(self):
        return f"{self.policy.policy_number} - {self.field.name}"

