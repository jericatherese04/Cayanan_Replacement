from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import ProjectElement, Material, QuotationRequest
from .forms import QuotationRequestForm
from django.contrib.auth.decorators import login_required
import logging
from .forms import ProjectElementForm, MaterialForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
logger = logging.getLogger(__name__)


@login_required
def delete_quotation_request(request, request_id):
    quotation_request = get_object_or_404(QuotationRequest, id=request_id, user=request.user)
    quotation_request.delete()
    return redirect('homepage')  # Redirect to the quotes page after deletion
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


@csrf_exempt  # Use this only for testing; remove in production for security reasons
def update_prices(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prices = data.get('prices', [])
            markups = data.get('markups', [])

            # Update prices
            for item in prices:
                material_id = item['materialId']
                price = item['price']
                Material.objects.filter(id=material_id).update(price=price)

            # Update markups
            for item in markups:
                material_id = item['materialId']
                markup = item['markup']
                Material.objects.filter(id=material_id).update(markup=markup)

            return JsonResponse({'success': True, 'message': 'Prices and markups updated successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Only POST method is allowed.'}, status=405)


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
            quote.total_cost = quote.material.price * quote.quantity * (1 + (quote.material.markup / 100))  # Include markup in total cost
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
            quantity = form.cleaned_data['quantity']
            area_size = form.cleaned_data['area_size']
            location = form.cleaned_data['location']

            QuotationRequest.objects.create(
                user=request.user,
                project_element=element,
                material=material,
                quantity=quantity,
                area_size=area_size,
                location=location,
                status="Pending"
            )
            return redirect('quotation_success')
    else:
        form = QuotationRequestForm()

    elements = ProjectElement.objects.prefetch_related('materials').all()  # This fetches all project elements

    return render(request, 'quotation_request.html', {
        'form': form,
        'project_elements': elements  # Ensure this is passed to the template
    })


def load_materials(request):
    element_id = request.GET.get('element_id')
    materials = Material.objects.filter(project_element_id=element_id)
    return JsonResponse(list(materials.values('id', 'name', 'price', 'markup')), safe=False)

def quotation_success(request):
    return render(request, 'quotation_success.html')
