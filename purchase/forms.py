# purchase/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Requisition, RequisitionItem, Product,PurchaseOrder,PurchaseOrderItem
import json

class RequisitionForm(forms.ModelForm):
    """Form for creating or editing a Requisition (main form)."""

    class Meta:
        model = Requisition
        exclude = ['status']
        fields = ['requisition_date', 'expected_date', 'priority', 'status', 'approved_by']
        widgets = {
            'requisition_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2'
            }),
            'expected_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2'
            }),
            'approved_by': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # We’ll pass the user from the view
        super().__init__(*args, **kwargs)

        # Only show approval fields to Admins or Managers
        if user and not user.groups.filter(name__in=['Admin', 'Manager']).exists():
            self.fields.pop('status')
            self.fields.pop('approved_by')


class RequisitionItemForm(forms.ModelForm):
    """Form for adding/editing a single RequisitionItem (inline form)."""

    class Meta:
        model = RequisitionItem
        fields = ['item_name', 'quantity', 'unit', 'note']
        widgets = {
            'item_name': forms.Select(attrs={
                'class': 'item-select w-full border border-gray-300 rounded px-2 py-1'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'quantity-input w-full border border-gray-300 rounded px-2 py-1'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'unit-input w-full border border-gray-300 rounded px-2 py-1 bg-gray-50',
                'readonly': 'readonly'
            }),
            'note': forms.Textarea(attrs={
                'rows': 2,
                'class': 'note-input w-full border border-gray-300 rounded px-2 py-1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = Product.objects.all()
        self.fields['item_name'].queryset = products
        self.fields['item_name'].widget.attrs['data-units'] = json.dumps({
            str(product.id): product.unit for product in products
        })
        if self.instance and self.instance.pk and self.instance.item_name:
            self.fields['unit'].initial = self.instance.item_name.unit


# Inline formset for multiple requisition items
RequisitionItemFormSet = inlineformset_factory(
    parent_model=Requisition,
    model=RequisitionItem,
    form=RequisitionItemForm,
    extra=1,
    can_delete=True
)

# purchase/forms.py
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'vendor','vat_percent', 'discount']

PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    fields=('item_name', 'quantity', 'unit', 'price'),
    extra=1,
    can_delete=True
)
