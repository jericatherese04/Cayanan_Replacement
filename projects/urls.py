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
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('', views.homepage, name='homepage'),  # Home page URL
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('approve_project/<int:project_id>/', views.approve_project_request, name='approve_project'),
    path('approve_quotation/<int:quote_id>/', views.approve_quotation, name='approve_quotation'),
    path('decline_quotation/<int:quote_id>/', views.decline_quotation, name='decline_quotation'),
    path('view-declined-projects/', views.declined_projects, name='view_declined_project'),
    path('approved-quotations/', views.approved_quotations, name='view_approved_project'),

]
