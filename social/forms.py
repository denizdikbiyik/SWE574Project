from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    description = forms.CharField(
        label = '',
        widget = forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Create a service...'
        })
    )

    servicedate = forms.DateTimeField(
        label = '',
        widget = forms.DateInput(attrs={
            'class': 'timepicker',
            'placeholder': '2022-12-12 00:00:00'
        })
    )

    class Meta:
        model = Service
        fields = ['description', 'servicedate']