# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('request-quotation/', views.quotation_request, name='quotation_request'),
    path('load-materials/', views.load_materials, name='load_materials'),
]
