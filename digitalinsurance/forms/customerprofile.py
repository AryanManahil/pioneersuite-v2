from django import forms
from digitalinsurance.models.customer import CustomerProfile

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address', 'national_id', 'date_of_birth', 'photo', 'document']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter phone number',
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter your address',
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
                'placeholder': 'National ID or Passport number',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-600 border border-gray-300 rounded',
            }),
            'document': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-600 border border-gray-300 rounded',
            }),
        }
