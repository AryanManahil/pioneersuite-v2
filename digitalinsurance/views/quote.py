# digitalinsurance/views/quote.py

from django.shortcuts import render, get_object_or_404
from datetime import date
from digitalinsurance.models import (
    Plan, TravelPurpose, Premium, DurationBand, Quote
)
from digitalinsurance.utils import (
    calculate_age, get_age_band, get_duration_band
)


def travel_quote_view(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    today = date.today().isoformat()

    if request.method == "POST":
        return handle_quote_submission(request, plan)

    duration_bands = DurationBand.objects.order_by("min_days")
    return render(request, "digitalinsurance/travel_quote_form.html", {
        "plan": plan,
        "today": today,
        "duration_bands": duration_bands,
    })


def handle_quote_submission(request, plan):
    try:
        countries = request.POST.getlist("countries")
        dob = request.POST.get("dob")
        departure_date_str = request.POST.get("departure_date")  # string from form
        duration_band_id = int(request.POST.get("coverage_period"))

        age = calculate_age(date.fromisoformat(dob))
        age_band = get_age_band(age)
        duration_band = DurationBand.objects.get(id=duration_band_id)

        if not age_band or not duration_band:
            raise ValueError("No matching age/duration band found.")

        purpose = TravelPurpose.objects.filter(
            plan=plan,
            purpose_type__iexact="Business and Holiday"
        ).first()

        if not purpose:
            raise ValueError("Travel purpose not defined for this plan.")

        premium_entry = Premium.objects.filter(
            purpose=purpose,
            age_band=age_band,
            duration_band=duration_band
        ).first()

        if not premium_entry or premium_entry.no_cover:
            raise ValueError("No coverage available for selected criteria.")

        vat_rate = 15
        stamp_fee = 50
        net_premium = premium_entry.amount
        vat = round(net_premium * vat_rate / 100, 2)
        gross = round(net_premium + vat + stamp_fee, 2)

        # Create Quote object only
        quote = Quote.objects.create(
            customer=request.user,
            product=plan.product,
            total_premium=gross,
            status='pending'
        )

        return render(request, "digitalinsurance/travel_quote_result.html", {
            "quote": quote,
            "countries": countries,
            "plan_name": plan.name,
            "region": plan.region,
            "currency": plan.currency,
            "age": age,
            "coverage_period": f"{duration_band.label} ({duration_band.min_days}-{duration_band.max_days} days)",
            "net_premium": net_premium,
            "vat": vat,
            "vat_rate": vat_rate,
            "stamp": stamp_fee,
            "gross_premium": gross,
            "departure_date": departure_date_str,
            "duration_days": duration_band.max_days,
        })

    except Exception as e:
        return render_quote_error(request, plan, f"❗ {str(e)}")

def render_quote_error(request, plan, reason):
    duration_bands = DurationBand.objects.order_by("min_days")
    today = date.today().isoformat()
    return render(request, "digitalinsurance/travel_quote_form.html", {
        "plan": plan,
        "today": today,
        "duration_bands": duration_bands,
        "error": reason,
    })


def travel_purpose_detail(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)

    purpose = TravelPurpose.objects.filter(
        plan=plan,
        purpose_type__iexact="Business and Holiday"
    ).first()

    return render(request, "digitalinsurance/travel_purpose_detail.html", {
        "plan": plan,
        "purpose": purpose,
    })
