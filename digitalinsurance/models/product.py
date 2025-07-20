from django.db import models

# 🌐 Currency choices
CURRENCY_CHOICES = [
    ("BDT", "Taka (৳)"),
    ("USD", "US Dollar ($)"),
    ("EUR", "Euro (€)"),
]


# 🔹 Master: Insurance Product
class Product(models.Model):
    code = models.SlugField(unique=True)  # e.g. "omp", "cft"
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# 🔹 Travel Plan (Plan-A, Plan-B, etc.)
class Plan(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=20)  # e.g. "Plan-A"
    region = models.CharField(max_length=100)  # e.g. "Worldwide Excluding USA"
    currency = models.CharField(max_length=10, default="BDT")

    def __str__(self):
        return f"{self.product.code.upper()} - {self.name}"


# 🔹 Travel Purpose (Business, Holiday, Employment, Studies)
class TravelPurpose(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="purposes")
    purpose_type = models.CharField(max_length=100)  # e.g. "Business and Holiday"

    def __str__(self):
        return f"{self.plan.name} - {self.purpose_type}"


# 🔹 Age Band (0-18, 18-40, etc.)
class AgeBand(models.Model):
    label = models.CharField(max_length=20)
    min_age = models.PositiveIntegerField()
    max_age = models.PositiveIntegerField()

    def __str__(self):
        return self.label


# 🔹 Duration Band (01-14, 15-21, etc.)
class DurationBand(models.Model):
    label = models.CharField(max_length=20)
    min_days = models.PositiveIntegerField()
    max_days = models.PositiveIntegerField()

    def __str__(self):
        return self.label


# 🔹 Premium (final amount user pays)
class Premium(models.Model):
    purpose = models.ForeignKey(
        TravelPurpose,
        on_delete=models.CASCADE,
        related_name="premiums"
    )
    age_band = models.ForeignKey(AgeBand, on_delete=models.CASCADE)
    duration_band = models.ForeignKey(DurationBand, on_delete=models.CASCADE)

    amount = models.FloatField()
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="BDT")
    no_cover = models.BooleanField(default=False)

    class Meta:
        unique_together = ("purpose", "age_band", "duration_band")
        verbose_name = "Premium"
        verbose_name_plural = "Premiums"
        ordering = ["purpose", "age_band", "duration_band"]

    def __str__(self):
        status = "❌ No Cover" if self.no_cover else f"₹{self.amount}"
        return f"{self.purpose} | {self.age_band} | {self.duration_band} → {status}"


# 🔹 Optional: Dynamic Fields for Forms (DOB, Passport, etc.)
class ProductField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('choice', 'Choice'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)  # e.g., "passport_number"
    label = models.CharField(max_length=200)  # Display label
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=True)
    choices = models.TextField(blank=True, help_text="Comma-separated for choice fields")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.code.upper()} - {self.label}"
