
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # Add this line to include the quiz app's URLs'
    path('projects/', include('projects.urls')),  # Add this line to include the accounts app's URLs'
]
