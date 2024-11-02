# forms.py
from django import forms
from .models import ProjectElement, Material, QuotationRequest


class QuotationRequestForm(forms.Form):
    element = forms.ModelChoiceField(
        queryset=ProjectElement.objects.all(),
        widget=forms.RadioSelect,
        empty_label="Select a Project Element"  # Optional
    )
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        widget=forms.RadioSelect,
        required=False
    )
    quantity = forms.IntegerField(min_value=1, initial=1)
    area_size = forms.CharField(max_length=100, required=False)
    location = forms.CharField(max_length=200, required=False)

class ProjectElementForm(forms.ModelForm):
    class Meta:
        model = ProjectElement
        fields = ['name']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'project_element']
