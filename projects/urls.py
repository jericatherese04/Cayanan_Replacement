# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('request-quotation/', views.quotation_request, name='quotation_request'),
    path('load-materials/', views.load_materials, name='load_materials'),
    path('quotation/success/', views.quotation_success, name='quotation_success'),
    path('my-quotes/', views.list_of_my_quotes, name='homepage'),
    path('materials-and-elements/', views.all_project_materials_and_elements, name='all_project_materials_and_elements'),
    path('add-element/', views.add_project_element, name='add_project_element'),
    path('add-material/', views.add_material, name='add_material'),
    path('pending-projects/', views.view_pending_projects, name='view_pending_projects'),
    path('update-prices/', views.update_prices, name='update_prices'),
    path('delete-quotation/<int:request_id>/', views.delete_quotation_request, name='delete_quotation'),
    path('delete_element/<int:pk>/', views.DeleteElementView.as_view(), name='delete_element'),
    path('delete_material/<int:pk>/', views.DeleteMaterialView.as_view(), name='delete_material'),

]
