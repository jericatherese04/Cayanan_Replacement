from django import forms
from .models import ProjectElement, Material, QuotationRequest

class QuotationRequestForm(forms.ModelForm):
    class Meta:
        model = QuotationRequest
        fields = ['project_element', 'material', 'quantity', 'area_size', 'location']
        widgets = {
            'project_element': forms.CheckboxSelectMultiple(),  # Keep this if allowing multiple selections
            'material': forms.CheckboxSelectMultiple(),
        }

class ProjectElementForm(forms.ModelForm):
    class Meta:
        model = ProjectElement
        fields = ['name', 'price']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'project_element', 'price', 'markup']
