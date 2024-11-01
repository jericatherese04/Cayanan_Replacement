from django.urls import path, include
from . import views

urlpatterns = [
   path('', views.homepage, name='home'),
   path('register/', views.register_view, name='register'),
   path('login/', views.login_view, name='login'),
   path('logout/', views.logout_view, name='logout'),
   path('homepage/', views.homepage, name='homepage'),
]