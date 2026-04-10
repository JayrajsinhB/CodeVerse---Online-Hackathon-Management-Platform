# core/views/auth_views.py

"""
Authentication Views
--------------------
Handles:
- User Signup
- User Login
- User Logout

Responsibilities:
- Manage authentication flow
- Send welcome email on signup
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail

from ..forms import UserSignupForm


# ==============================
# Signup View
# ==============================
def userSignupView(request):
    """
    Register a new user and auto-login.

    Flow:
    1. Prevent access if already authenticated
    2. Validate signup form
    3. Save user
    4. Log user in
    5. Send welcome email
    6. Redirect to dashboard
    """

    # Prevent logged-in users from accessing signup
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = UserSignupForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Auto login after successful signup
            login(request, user)

            # Send welcome email
            send_mail(
                'Welcome to CodeVerse!',
                (
                    f'Hi {user.email},\n\n'
                    f'Welcome to CodeVerse! We are thrilled to have you as a {user.role}.\n\n'
                    f'Get ready to build something amazing.\n\n'
                    f'- The CodeVerse Team'
                ),
                None,
                [user.email],
                fail_silently=False,
            )

            return redirect('dashboard')

    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})


# ==============================
# Login View
# ==============================
def userLoginView(request):
    """
    Authenticate and log in a user.

    Flow:
    1. Prevent access if already authenticated
    2. Validate login form
    3. Authenticate user
    4. Redirect to next page or dashboard
    """

    # Prevent logged-in users from accessing login page
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # Log the user in
            login(request, user)

            # Redirect to 'next' if present, else dashboard
            return redirect(request.GET.get('next', 'dashboard'))

    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


# ==============================
# Logout View
# ==============================
def userLogoutView(request):
    """
    Log out the current user and redirect to home page.
    """

    logout(request)
    return redirect('home')