# forms.py
from django import forms
from .models import ProjectElement, Material

class QuotationRequestForm(forms.Form):
    element = forms.ModelChoiceField(queryset=ProjectElement.objects.all(), widget=forms.RadioSelect)
    material = forms.ModelChoiceField(queryset=Material.objects.all(), widget=forms.RadioSelect, required=False)
class ProjectElementForm(forms.ModelForm):
    class Meta:
        model = ProjectElement
        fields = ['name']  # Adjust fields as necessary

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'project_element']  # Assuming project_element is a ForeignKey in Material