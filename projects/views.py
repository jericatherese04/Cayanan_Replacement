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
from django.http import HttpResponseForbidden
import json
from django.utils import timezone
from django.contrib.auth.models import User


@login_required
def view_complete_projects(request):
    # Fetch all quotations that are marked as "Complete" for the authenticated user
    completed_quotes = QuotationRequest.objects.filter(status="Complete", user=request.user)

    return render(request, 'view_complete_project.html', {'completed_quotes': completed_quotes})
@login_required
def complete_quotation(request, quotation_id):
    # Fetch the quotation object
    quotation = get_object_or_404(QuotationRequest, id=quotation_id, user=request.user)

    # Update the status to "Complete"
    quotation.status = "Complete"
    quotation.end_date = timezone.now().date()  # Set end_date to today
    quotation.save()

    # Redirect to the page showing approved quotations (or any other page you prefer)
    return redirect('view_approved_project')  # Make sure to use the correct URL name
@login_required
def approved_quotations(request):
    # Fetch all quotations approved by the admin
    approved_quotes = QuotationRequest.objects.filter(status="Approved by Admin")

    # Fetch all quotations approved by the user
    user_approved_quotes = QuotationRequest.objects.filter(status="Approved by User", user=request.user)

    return render(request, 'view_approved_project.html', {
        'approved_quotes': approved_quotes,
        'user_approved_quotes': user_approved_quotes
    })
@login_required
def declined_projects(request):
    if request.user.is_authenticated:
        declined_quotes = QuotationRequest.objects.filter(status="Declined by User", user=request.user)
    else:
        declined_quotes = []

    return render(request, 'view_declined_project.html', {'declined_quotes': declined_quotes})

@csrf_exempt
def decline_quotation(request, quote_id):
    quote = get_object_or_404(QuotationRequest, id=quote_id)

    if request.method == 'POST':
        if request.user.is_authenticated:
            quote.status = "Declined by User"
            quote.save()
            return JsonResponse({'success': True, 'message': 'Quotation declined successfully!'})
        return JsonResponse({'success': False, 'message': 'You are not allowed to decline this quotation.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
from django.utils import timezone  # Make sure to import timezone

@csrf_exempt  # Only if absolutely necessary; otherwise, manage CSRF in AJAX
def approve_quotation(request, quote_id):
    quote = get_object_or_404(QuotationRequest, id=quote_id)

    if request.method == 'POST':
        if request.user.is_authenticated:
            quote.status = "Approved by User"
            quote.start_date = timezone.now().date()  # Set start_date to the current date
            quote.save()
            return JsonResponse({'success': True, 'message': 'Quotation approved successfully!'})
        return JsonResponse({'success': False, 'message': 'You are not allowed to approve this quotation.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
@csrf_exempt  # Only if absolutely necessary; otherwise, manage CSRF in AJAX
def approve_project_request(request, project_id):
    project_request = get_object_or_404(QuotationRequest, id=project_id)

    if request.method == 'POST':
        if request.user.is_authenticated and request.user.is_staff:
            project_request.status = 'Approved by Admin'
            project_request.save()
            return JsonResponse({'success': True, 'message': 'Request approved successfully!'})
        return JsonResponse({'success': False, 'message': 'You are not allowed to approve this request.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

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
                    project.material.add(material)

                except Material.DoesNotExist:
                    continue  # Handle the case where the material does not exist

            # Redirect to a success page after saving changes
            return redirect('homepage')

    else:
        # If not a POST request, bind the existing project data to the form
        form = QuotationRequestForm(instance=project)

    # Fetch all materials to display in the form
    materials_with_details = Material.objects.all()

    # Access the related materials using the correct attribute
    selected_material_ids = project.material.values_list('id', flat=True)

    # Pass the project, form, and materials to the context for rendering
    context = {
        'project': project,  # Include the project object in the context
        'form': form,
        'materials_with_details': materials_with_details,
        'selected_material_ids': selected_material_ids,
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
        user_id = request.POST.get('user_id')  # Get the selected user ID from the form

        # Create the QuotationRequest instance
        quotation_request = QuotationRequest.objects.create(
            user=request.user,  # This is the logged-in user
            quantity=quantity,
            area_size=area_size,
            location=location
        )

        # If the user is a superuser and a user_id is provided, assign the selected user
        if request.user.is_superuser and user_id:
            selected_user = User.objects.get(id=user_id)
            quotation_request.user = selected_user  # Assign the selected user
            quotation_request.save()  # Save the instance again to update the user

        # Add selected project elements and materials
        quotation_request.project_element.add(*selected_elements)
        if selected_materials:
            quotation_request.material.add(*selected_materials)

        return redirect('quotation_success')  # Redirect to a success page or appropriate response

    # Fetch project elements and users for rendering the form
    project_elements = ProjectElement.objects.all()
    users = User.objects.all()  # Fetch all users

    return render(request, 'quotation_request.html', {
        'project_elements': project_elements,
        'users': users,  # Pass users to the template
    })
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


@login_required
def admin_request_view(request):
    if request.method == 'POST':
        form = QuotationRequestForm(request.POST)
        if form.is_valid():
            # Save the form data to create a new QuotationRequest instance
            quotation_request = form.save(commit=False)  # Create the instance without saving to DB yet
            user_id = request.POST.get('user_id')  # Get the user ID to whom the request will be sent
            user = get_object_or_404(User, id=user_id)
            quotation_request.user = user  # Set the user
            quotation_request.status = 'Pending'  # Set status to Pending
            quotation_request.save()  # Now save the instance

            return redirect('quotation_success')  # Redirect to a success page
    else:
        form = QuotationRequestForm()  # Create an empty form instance

    return render(request, 'admin_request.html', {
        'form': form,
        'users': User.objects.all(),  # Fetch all users for the dropdown
    })


@login_required
def submit_project_request(request):
    # Handle AJAX request to load materials for a selected project element
    if request.is_ajax() and request.method == 'GET':
        element_id = request.GET.get('element_id')
        materials = Material.objects.filter(project_element_id=element_id)
        material_data = list(materials.values('id', 'name', 'price', 'markup'))
        return JsonResponse(material_data, safe=False)

    # Standard form rendering for initial page load
    form = QuotationRequestForm()
    project_elements = ProjectElement.objects.all()
    users = User.objects.all()

    if request.method == 'POST':
        form = QuotationRequestForm(request.POST)
        if form.is_valid():
            quotation_request = form.save(commit=False)
            quotation_request.user = request.user
            quotation_request.save()

            # Add selected materials to the quotation request
            selected_materials = request.POST.getlist('materials')
            for material_id in selected_materials:
                material = Material.objects.get(id=material_id)
                quotation_request.material.add(material)

            return redirect('quotation_success')

    return render(request, 'admin_request.html', {
        'form': form,
        'project_elements': project_elements,
        'users': users,
    })