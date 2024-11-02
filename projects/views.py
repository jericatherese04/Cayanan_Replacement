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
from django.views import View


import json

# views.py

@login_required
def edit_project(request, project_id):
    # Fetch the project or return a 404 if not found
    project = get_object_or_404(QuotationRequest, id=project_id)

    if request.method == 'POST':
        # Bind form data to the instance of the project
        form = QuotationRequestForm(request.POST, instance=project)

        if form.is_valid():
            # Save the updated project information
            form.save()

            # Clear existing materials to avoid duplicates
            project.material.clear()

            # Fetch selected materials correctly
            selected_material_ids = request.POST.getlist('materials')

            # Add each selected material to the project
            for material_id in selected_material_ids:
                try:
                    material = Material.objects.get(id=material_id)

                    # Construct keys to fetch price and markup from the form data
                    price_key = f'material_price_{material_id}'
                    markup_key = f'material_markup_{material_id}'

                    # Get the new price and markup; default to the existing ones if not provided
                    new_price = float(request.POST.get(price_key, material.price))
                    new_markup = float(request.POST.get(markup_key, material.markup))

                    # Update the material object with new values
                    material.price = new_price
                    material.markup = new_markup
                    material.save()

                    # Add the material to the project
                    project.material.add(material)  # Correctly associate the material with the project

                except Material.DoesNotExist:
                    # Handle the case where the material does not exist
                    continue  # Optionally log this or handle it differently

            # Redirect to a success page after saving changes
            return redirect('homepage')

    else:
        # If not a POST request, bind the existing project data to the form
        form = QuotationRequestForm(instance=project)

    # Fetch all materials to display in the form
    materials_with_details = Material.objects.all()

    # Access the related materials using the correct attribute
    selected_material_ids = project.material.values_list('id', flat=True)  # Get selected material IDs

    # Pass the form and materials to the context for rendering
    context = {
        'form': form,
        'materials_with_details': materials_with_details,
        'selected_material_ids': selected_material_ids,  # Pass selected material IDs for the template
    }
    return render(request, 'edit_project.html', context)


logger = logging.getLogger(__name__)
class DeleteElementView(View):
    def delete(self, request, pk):
        try:
            element = ProjectElement.objects.get(pk=pk)
            element.delete()
            return JsonResponse({'success': True, 'message': 'Element deleted successfully.'})
        except ProjectElement.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Element not found.'}, status=404)

class DeleteMaterialView(View):
    def delete(self, request, pk):
        try:
            material = Material.objects.get(pk=pk)
            material.delete()
            return JsonResponse({'success': True, 'message': 'Material deleted successfully.'})
        except Material.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Material not found.'}, status=404)

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
            return JsonResponse({'success': False, 'error': 'Invalid JSON format.'}, status=400)
        except Material.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'One or more materials not found.'}, status=404)
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
    user_quotes = QuotationRequest.objects.filter(user=request.user).prefetch_related('project_element', 'material')

    # Initialize total costs for each quote
    for quote in user_quotes:
        total_cost = 0  # Reset total cost for each quote
        materials_with_details = []  # List to hold material details for this quote

        for material in quote.material.all():  # Loop through each material for the quote
            material_cost = material.price * quote.quantity * (1 + (material.markup / 100))  # Calculate material cost with markup
            total_cost += material_cost  # Add to total cost

            # Store material details including name, price, and markup
            materials_with_details.append({
                'name': material.name,
                'price': material.price,
                'markup': material.markup,
                'material_cost': material_cost,  # Add the computed cost for individual material
            })

        quote.total_cost = total_cost  # Store the computed total cost for the quote
        quote.material_details = materials_with_details  # Attach material details to the quote

    return render(request, 'homepage.html', {'user_quotes': user_quotes})



import logging

logger = logging.getLogger(__name__)


@login_required
def quotation_request(request):
    if request.method == 'POST':
        selected_elements = request.POST.getlist('project_element')
        selected_materials = request.POST.getlist('materials')
        quantity = request.POST.get('quantity')
        area_size = request.POST.get('area_size')
        location = request.POST.get('location')
        user = request.user  # Assuming the user is logged in

        # Create the QuotationRequest instance
        quotation_request = QuotationRequest.objects.create(
            user=user,
            quantity=quantity,
            area_size=area_size,
            location=location
        )
        # Add selected project elements and materials
        quotation_request.project_element.add(*selected_elements)
        if selected_materials:
            quotation_request.material.add(*selected_materials)

        return redirect('quotation_success')  # Redirect to a success page or appropriate response

    # Fetch project elements for rendering the form
    project_elements = ProjectElement.objects.all()
    return render(request, 'quotation_request.html', {'project_elements': project_elements})

def load_materials(request):
    element_id = request.GET.get('element_id')
    materials = Material.objects.filter(project_element_id=element_id)
    return JsonResponse(list(materials.values('id', 'name', 'price', 'markup')), safe=False)

def quotation_success(request):
    return render(request, 'quotation_success.html')


@login_required
def homepage(request):
    user_quotes = QuotationRequest.objects.filter(user=request.user).prefetch_related('project_element', 'material')
    # Debugging output
    print("User Quotes:", user_quotes)
    for quote in user_quotes:
        print("Quote ID:", quote.id, "Materials:", quote.material.all())

    return render(request, 'homepage.html', {
        'user_quotes': user_quotes
    })