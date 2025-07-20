from django.db import models
from django.contrib.auth import get_user_model
from core_settings.models import Department  # adjust import if needed

User = get_user_model()

class EDocument(models.Model):
    DOCUMENT_TYPES = [
        ('leave', 'Leave Application'),
        ('travel', 'Travel Permission'),
        ('expense', 'Expense Report'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    class Meta:
        permissions = [
            ("can_view_document", "Can view documents"),
            ("can_approve_document", "Can approve documents"),
            ("can_upload_document", "Can upload documents"),
        ]

    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edocuments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    note = models.TextField()
    attachment = models.FileField(upload_to='edocuments/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    approval_note = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.document_type} - {self.submitted_by.username} ({self.status})"
