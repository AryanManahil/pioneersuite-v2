from django import forms
from digitalinsurance.models import Product, ProductField   # note uppercase P

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'is_active']

class ProductFieldForm(forms.ModelForm):
    class Meta:
        model = ProductField
        fields = ['product', 'name', 'label', 'field_type', 'required', 'choices', 'order']
