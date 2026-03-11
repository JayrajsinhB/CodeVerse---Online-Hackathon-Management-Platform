from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='login/'), name='home_redirect'), 
    path('signup/', views.userSignupView, name='signup'),
    path('login/', views.userLoginView, name='login'),     # <-- NEW
    path('logout/', views.userLogoutView, name='logout'),  # <-- NEW
]