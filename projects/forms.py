# forms.py
from django import forms
from .models import ProjectElement

class QuotationRequestForm(forms.Form):
    element = forms.ModelChoiceField(queryset=ProjectElement.objects.all(), widget=forms.RadioSelect)
