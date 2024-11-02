from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import ProjectElement, Material, QuotationRequest
from .forms import QuotationRequestForm
from django.contrib.auth.decorators import login_required
import logging
from .forms import ProjectElementForm, MaterialForm
from django.views.decorators.csrf import csrf_exempt
import json


logger = logging.getLogger(__name__)
@login_required
def all_project_materials_and_elements(request):
    elements = ProjectElement.objects.prefetch_related('materials').all()

    if request.method == 'POST':
        # Handle form submission to update all material prices
        for element in elements:
            for material in element.materials.all():
                material_price = request.POST.get(f'material_price_{material.id}')
                material_markup = request.POST.get(f'material_markup_{material.id}')

                if material_price:
                    try:
                        material.price = float(material_price)
                        material.save()
                    except ValueError:
                        # Handle the case where price is not a valid float
                        pass

        return redirect('all_project_materials_and_elements')

    return render(request, 'all_project_materials_and_elements.html', {'elements': elements})


@csrf_exempt  # For testing, consider removing this in production
def update_prices(request, element_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug(f"Updating prices for element {element_id}: {data}")  # Log the incoming data

            prices = data.get('prices', [])
            markups = data.get('markups', [])

            # Update prices in the database
            for price_info in prices:
                material_id = price_info.get('materialId')
                price = price_info.get('price')

                if material_id is not None and price is not None:
                    material = get_object_or_404(Material, id=material_id)
                    material.price = price
                    material.save()
                else:
                    logger.warning(f"Invalid data for material price update: {price_info}")

            # Update markups in the database
            for markup_info in markups:
                material_id = markup_info.get('materialId')
                markup = markup_info.get('markup')

                if material_id is not None and markup is not None:
                    material = get_object_or_404(Material, id=material_id)
                    material.markup = markup
                    material.save()
                else:
                    logger.warning(f"Invalid data for material markup update: {markup_info}")

            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error updating prices for element {element_id}: {e}")
            return JsonResponse({'status': 'fail', 'error': str(e)}, status=400)

    return JsonResponse({'status': 'fail'}, status=400)


@login_required
def view_pending_projects(request):
    # Retrieve all pending project requests from all users
    pending_projects = QuotationRequest.objects.filter(status='Pending')
    return render(request, 'view_pending_projects.html', {'pending_projects': pending_projects})
@login_required
def add_project_element(request):
    if request.method == 'POST':
        form = ProjectElementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_project_materials_and_elements')
    else:
        form = ProjectElementForm()
    return render(request, 'add_project_element.html', {'form': form})

@login_required
def add_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_project_materials_and_elements')
    else:
        form = MaterialForm()
    return render(request, 'add_material.html', {'form': form})



@login_required
def list_of_my_quotes(request):
    user_quotes = QuotationRequest.objects.filter(user=request.user)

    # Add total cost calculation dynamically
    for quote in user_quotes:
        if quote.material:
            quote.total_cost = quote.material.price * quote.quantity  # Calculate total cost
        else:
            quote.total_cost = 0  # Handle case where material is None

    return render(request, 'homepage.html', {'user_quotes': user_quotes})





@login_required
def quotation_request(request):
    if request.method == 'POST':
        form = QuotationRequestForm(request.POST)
        if form.is_valid():
            element = form.cleaned_data['element']
            material = form.cleaned_data['material'] if 'material' in form.cleaned_data else None

            QuotationRequest.objects.create(
                user=request.user,
                project_element=element,
                material=material,
                status="Pending"
            )
            return redirect('quotation_success')
    else:
        form = QuotationRequestForm()

    elements = ProjectElement.objects.prefetch_related('materials').all()
    return render(request, 'quotation_request.html', {'form': form, 'project_elements': elements})

def load_materials(request):
    element_id = request.GET.get('element_id')
    materials = Material.objects.filter(project_element_id=element_id)
    return JsonResponse(list(materials.values('id', 'name')), safe=False)

def quotation_success(request):
    return render(request, 'quotation_success.html')
