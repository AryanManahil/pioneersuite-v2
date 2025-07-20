from django.contrib import admin
from .models import Product, Plan, TravelPurpose, AgeBand, DurationBand, Premium, ProductField,CustomerProfile

admin.site.register(Product)
admin.site.register(Plan)
admin.site.register(TravelPurpose)
admin.site.register(AgeBand)
admin.site.register(DurationBand)
admin.site.register(ProductField)
admin.site.register(CustomerProfile)

@admin.register(Premium)
class PremiumAdmin(admin.ModelAdmin):
    list_display = ("purpose", "age_band", "duration_band", "amount", "no_cover")
    list_filter = ("purpose__plan__product", "age_band", "duration_band", "no_cover")
    search_fields = ("purpose__purpose_type",)
