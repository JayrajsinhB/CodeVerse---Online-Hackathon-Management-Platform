from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class UserSignupForm(UserCreationForm):
    class Meta:
        model = User
        # Do NOT put password1 and password2 here. 
        # UserCreationForm generates them automatically!
        fields = ['email', 'role']