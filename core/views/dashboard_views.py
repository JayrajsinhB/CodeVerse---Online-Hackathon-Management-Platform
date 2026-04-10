# core/views/dashboard_views.py

"""
Dashboard Views
---------------
Handles:
- Home page routing
- Role-based dashboard rendering

Responsibilities:
- Redirect authenticated users appropriately
- Serve different dashboards based on user role:
    - Organizer → Hackathons created
    - Judge → Submissions to review
    - Participant → Team memberships
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from ..models import Hackathon, TeamMember, Submission, User
from ..forms import ParticipantProfileForm, OrganizerProfileForm, JudgeProfileForm

# ==============================
# Home View
# ==============================
def homeView(request):
    """
    Landing page.

    Behavior:
    - Redirect authenticated users to dashboard
    - Show public home page for guests
    """

    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'core/home.html')


# ==============================
# Dashboard View (Role-Based)
# ==============================
@login_required(login_url='login')
def dashboardView(request):
    """
    Main dashboard router.

    Routes users based on role:
    - organizer → manage hackathons
    - judge → review submissions
    - participant → view teams
    """

    # -------- Organizer Dashboard --------
    if request.user.role == User.ORGANIZER:
        hackathons = (
            Hackathon.objects
            .filter(created_by=request.user)
            .order_by('-id')
        )

        return render(request, 'core/organizer_dashboard.html', {
            'hackathons': hackathons
        })

    # -------- Judge Dashboard --------
    elif request.user.role == User.JUDGE:
        submissions = (
            Submission.objects
            .exclude(hackathon__status='draft')
            .select_related('team', 'hackathon')
            .order_by('-submitted_at')
        )

        return render(request, 'core/judge_dashboard.html', {
            'submissions': submissions
        })

    # -------- Participant Dashboard (Default) --------
    memberships = (
        TeamMember.objects
        .filter(user=request.user)
        .select_related('team', 'team__hackathon')
    )

    return render(request, 'core/participant_dashboard.html', {
        'memberships': memberships
    })

# ==============================
# Edit Profile View
# ==============================
@login_required(login_url='login')
def editProfileView(request):
    user = request.user

    # Determine which form to use based on role
    if user.role == User.PARTICIPANT:
        form_class = ParticipantProfileForm
        profile = user.participant_profile
    elif user.role == User.ORGANIZER:
        form_class = OrganizerProfileForm
        profile = user.organizer_profile
    elif user.role == User.JUDGE:
        form_class = JudgeProfileForm
        profile = user.judge_profile
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        form = form_class(instance=profile)

    return render(request, 'core/edit_profile.html', {
        'form': form
    })