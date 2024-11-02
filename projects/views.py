# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ProjectElement, Material
from .forms import QuotationRequestForm

def quotation_request(request):
    elements = ProjectElement.objects.prefetch_related('materials').all()  # Prefetch related materials
    return render(request, 'quotation_request.html', {'project_elements': elements})

def load_materials(request):
    element_id = request.GET.get('element_id')
    materials = Material.objects.filter(project_element_id=element_id)
    return JsonResponse(list(materials.values('id', 'name')), safe=False)
