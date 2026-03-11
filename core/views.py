from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserSignupForm

# 1. Signup View (Updated redirect)
def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            # Now that we are building the login page, we can redirect them here!
            return redirect('login') 
    else:
        form = UserSignupForm()
    return render(request, 'core/signup.html', {'form': form})

# 2. Login View
def userLoginView(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Send them to the homepage/dashboard after successful login
            return redirect('home_redirect') 
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# 3. Logout View
def userLogoutView(request):
    logout(request)
    return redirect('login')