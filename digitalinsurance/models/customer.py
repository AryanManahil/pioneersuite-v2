from django.db import models  # ✅ this is missing
from django.conf import settings  # for settings.AUTH_USER_MODEL

class CustomerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # KYC fields – make all optional
    national_id = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='kyc/photos/', blank=True, null=True)
    document = models.FileField(upload_to='kyc/docs/', blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.email if hasattr(self.user, 'email') else self.user.username}"
