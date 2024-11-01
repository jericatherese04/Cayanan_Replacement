# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            # Create UserProfile only if it doesn't exist
            UserProfile.objects.get_or_create(user=user)  # This avoids IntegrityError
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on superuser status
            if user.is_superuser:
                messages.success(request, 'Logged in as admin.')
                return redirect('homepage')  # Redirect to the admin home page
            else:
                messages.success(request, f'Logged in as {user.username}.')
                return redirect('homepage')  # Redirect to the user home page
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

def homepage(request):
    return render(request, 'homepage.html')
