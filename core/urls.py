from django.urls import path
from django.views.generic import RedirectView # For redirecting root URL to home
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.homeView, name='home'),
    path('signup/', views.userSignupView, name='signup'),
    path('login/', views.userLoginView, name='login'),
    path('logout/', views.userLogoutView, name='logout'),
    path('dashboard/', views.dashboardView, name='dashboard'),
    path('profile/edit/', views.editProfileView, name='edit_profile'),
    path('user/<int:user_id>/', views.profileDisplayView, name='view_profile'),
    path('create-hackathon/', views.createHackathonView, name='create_hackathon'),
    path('hackathons/', views.hackathonListView, name='hackathons'),
    path('hackathon/<int:pk>/', views.hackathonDetailView, name='hackathon_detail'),
    path('hackathon/<int:pk>/edit/', views.editHackathonView, name='edit_hackathon'),
    path('hackathon/<int:pk>/delete/', views.deleteHackathonView, name='delete_hackathon'),
    path('hackathon/<int:pk>/teams/', views.manageTeamsView, name='manage_teams'),
    path('team/<int:team_id>/submit/', views.submitProjectView, name='submit_project'),
    path('submission/<int:pk>/grade/', views.gradeSubmissionView, name='grade_submission'),
    path('hackathon/<int:pk>/leaderboard/', views.leaderboardView, name='leaderboard'),
]