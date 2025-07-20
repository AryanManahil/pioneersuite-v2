from django import forms
from .models import EDocument

class EDocumentForm(forms.ModelForm):
    class Meta:
        model = EDocument
        fields = ['document_type', 'note', 'attachment']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2'
            }),
            'note': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full border border-gray-300 rounded px-3 py-2'
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'w-full border border-gray-300 rounded px-3 py-2'
            }),
        }
