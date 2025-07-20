from datetime import date

def calculate_age(born_date):
    today = date.today()
    return today.year - born_date.year - ((today.month, today.day) < (born_date.month, born_date.day))

def get_age_band(age):
    from digitalinsurance.models import AgeBand
    return AgeBand.objects.filter(min_age__lte=age, max_age__gte=age).first()

def get_duration_band(days):
    from digitalinsurance.models import DurationBand
    return DurationBand.objects.filter(min_days__lte=days, max_days__gte=days).first()

from django.utils import timezone

def generate_policy_number():
    today = timezone.now().strftime('%Y%m%d')  # e.g., 20250715
    prefix = "POL"
    base_number = f"{prefix}{today}"

    # Count how many policies created today
    from .models import InsurancePolicy
    count = InsurancePolicy.objects.filter(created_at__date=timezone.now().date()).count() + 1
    return f"{base_number}{str(count).zfill(3)}"  # e.g., POL20250715001
