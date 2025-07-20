from django.contrib import admin
from .models import Company, Branch, Department, Product

admin.site.register(Company)
admin.site.register(Branch)
admin.site.register(Department)
admin.site.register(Product)

