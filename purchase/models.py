from django.db import models
from django.conf import settings
from django.utils import timezone
from core_settings.models import Product, Department
from decimal import Decimal

class Requisition(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    requisition_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requisitions'
    )
    requisition_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='requisitions'
    )
    expected_date = models.DateField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='Medium',
    )
    requisition_no = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        editable=False
    )

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DONE', 'done'),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requisitions'
    )

    class Meta:
        permissions = [
            ("can_approve_requisition", "Can approve requisition"),
            ("can_view_approved_requisition", "Can view approved requisitions"),
            ("can_view_purchaseorder", "Can view purchase order"),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.requisition_no:
            self.requisition_no = f"REQ-{self.requisition_date.strftime('%Y%m%d')}-{self.pk:04d}"
            self.save(update_fields=['requisition_no'])

    def __str__(self):
        return self.requisition_no or f"Requisition {self.pk}"


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(
        Requisition,
        related_name='items',
        on_delete=models.CASCADE
    )
    item_name = models.ForeignKey(
        Product,
        related_name='requisition_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unit and self.item_name:
            self.unit = self.item_name.unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name.name} - {self.quantity} {self.unit}"


class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=20, unique=True)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('sent', 'Sent'),
        ('completed', 'Completed')
    ], default='draft')
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Add this
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_grand_total(self):
        return sum(item.quantity * item.price for item in self.items.all())

    def get_vat_amount(self):
        return self.get_grand_total() * (self.vat_percent / 100)

    def get_net_payable(self):
        return self.get_grand_total() + self.get_vat_amount() - self.discount


    created_at = models.DateTimeField(auto_now_add=True)  # Add this line
    updated_at = models.DateTimeField(auto_now=True)  # Optional, for updates tracking

    def __str__(self):
        return f"PO-{self.po_number}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit}"
