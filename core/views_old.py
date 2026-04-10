# core/views.py

"""
Core Views Module
-----------------
Handles authentication, dashboards, hackathon management,
teams, submissions, and scoring logic.

Key Principles:
- Clean separation of concerns
- Role-based access control
- Minimal repetition
- Clear, professional commenting
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from .forms import UserSignupForm, HackathonForm, SubmissionForm, ScoreForm
from .models import Hackathon, Team, TeamMember, Submission


# ==============================
# Helper Functions
# ==============================
def is_organizer(user):
    """Check if user is an organizer."""
    return user.is_authenticated and user.role == 'organizer'


# ==============================
# Authentication Views
# ==============================
def userSignupView(request):
    """Handle user signup and send welcome email."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    form = UserSignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)

        # Send welcome email
        send_mail(
            'Welcome to CodeVerse!',
            f'Hi {user.email},\n\nWelcome to CodeVerse! We are thrilled to have you as a {user.role}.\n\nGet ready to build something amazing.\n\n- The CodeVerse Team',
            None,
            [user.email],
            fail_silently=False,
        )

        return redirect('dashboard')

    return render(request, 'core/signup.html', {'form': form})


def userLoginView(request):
    """Authenticate user and redirect to dashboard."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'dashboard'))

    return render(request, 'core/login.html', {'form': form})


def userLogoutView(request):
    """Logout user."""
    logout(request)
    return redirect('home')


# ==============================
# General Views
# ==============================
def homeView(request):
    """Landing page (redirects authenticated users)."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'core/home.html')


@login_required(login_url='login')
def dashboardView(request):
    """
    Role-based dashboard routing:
    - Organizer → Hackathons created
    - Judge → All submissions
    - Participant → Joined teams
    """

    if request.user.role == 'organizer':
        hackathons = Hackathon.objects.filter(created_by=request.user).order_by('-id')
        return render(request, 'core/organizer_dashboard.html', {'hackathons': hackathons})

    if request.user.role == 'judge':
        submissions = Submission.objects.select_related('team', 'hackathon').order_by('-submitted_at')
        return render(request, 'core/judge_dashboard.html', {'submissions': submissions})

    memberships = TeamMember.objects.filter(user=request.user).select_related('team', 'team__hackathon')
    return render(request, 'core/participant_dashboard.html', {'memberships': memberships})


# ==============================
# Hackathon Views (Organizer)
# ==============================
@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def createHackathonView(request):
    """Create a new hackathon."""

    form = HackathonForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        hackathon = form.save(commit=False)
        hackathon.created_by = request.user
        hackathon.save()
        return redirect('dashboard')

    return render(request, 'core/create_hackathon.html', {'form': form})


@login_required(login_url='login')
def hackathonListView(request):
    """List all hackathons."""

    hackathons = Hackathon.objects.all().order_by('-start_date')
    return render(request, 'core/hackathon_list.html', {'hackathons': hackathons})


@login_required(login_url='login')
def hackathonDetailView(request, pk):
    """
    Hackathon detail page:
    - View hackathon
    - Create team
    - Join team via invite code
    """

    hackathon = get_object_or_404(Hackathon, pk=pk)

    # Check if user already belongs to a team
    membership = TeamMember.objects.filter(user=request.user, team__hackathon=hackathon).first()
    user_team = membership.team if membership else None

    if request.method == "POST":

        # --- Create Team ---
        if 'create_team' in request.POST:
            team_name = request.POST.get('team_name')

            if team_name and not user_team:
                team = Team.objects.create(
                    name=team_name,
                    hackathon=hackathon,
                    leader=request.user
                )
                TeamMember.objects.create(team=team, user=request.user)

                send_mail(
                    f'Team Created: {team.name}',
                    f'You have successfully created "{team.name}" for {hackathon.title}.\n\nInvite code: {team.access_code}',
                    None,
                    [request.user.email],
                    fail_silently=False,
                )

                return redirect('hackathon_detail', pk=pk)

        # --- Join Team ---
        elif 'join_team' in request.POST:
            invite_code = request.POST.get('invite_code')

            if invite_code and not user_team:
                team = Team.objects.filter(access_code=invite_code, hackathon=hackathon).first()

                if team:
                    TeamMember.objects.create(team=team, user=request.user)

                    send_mail(
                        f'Welcome to Team {team.name}!',
                        f'You joined "{team.name}" for {hackathon.title}.',
                        None,
                        [request.user.email],
                        fail_silently=False,
                    )

                    return redirect('hackathon_detail', pk=pk)

    return render(request, 'core/hackathon_detail.html', {
        'hackathon': hackathon,
        'user_team': user_team
    })


@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def editHackathonView(request, pk):
    """Edit an existing hackathon."""

    hackathon = get_object_or_404(Hackathon, pk=pk, created_by=request.user)
    form = HackathonForm(request.POST or None, instance=hackathon)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('dashboard')

    return render(request, 'core/create_hackathon.html', {'form': form, 'hackathon': hackathon})


@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def deleteHackathonView(request, pk):
    """Delete a hackathon."""

    hackathon = get_object_or_404(Hackathon, pk=pk, created_by=request.user)

    if request.method == "POST":
        hackathon.delete()
        return redirect('dashboard')

    return render(request, 'core/delete_hackathon.html', {'hackathon': hackathon})


@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def manageTeamsView(request, pk):
    """View all teams for a hackathon."""

    hackathon = get_object_or_404(Hackathon, pk=pk, created_by=request.user)
    teams = hackathon.teams.all().prefetch_related('members')

    return render(request, 'core/manage_teams.html', {
        'hackathon': hackathon,
        'teams': teams
    })


# ==============================
# Submission & Scoring
# ==============================
@login_required(login_url='login')
def submitProjectView(request, team_id):
    """Submit or update a project for a team."""

    team = get_object_or_404(Team, id=team_id, members=request.user)
    hackathon = team.hackathon

    submission = getattr(team, 'submission', None)
    form = SubmissionForm(request.POST or None, instance=submission)

    if request.method == "POST" and form.is_valid():
        sub = form.save(commit=False)
        sub.team = team
        sub.hackathon = hackathon
        sub.save()
        return redirect('dashboard')

    return render(request, 'core/submit_project.html', {
        'form': form,
        'team': team,
        'hackathon': hackathon
    })


@login_required(login_url='login')
def gradeSubmissionView(request, pk):
    """Judge assigns score to a submission."""

    if request.user.role != 'judge':
        return redirect('dashboard')

    submission = get_object_or_404(Submission, pk=pk)
    form = ScoreForm(request.POST or None, instance=submission)

    if request.method == "POST" and form.is_valid():
        form.save()

        send_mail(
            f'Project Graded: {submission.project_title}',
            f'Score: {submission.score}/100 for {submission.hackathon.title}',
            None,
            [submission.team.leader.email],
            fail_silently=False,
        )

        return redirect('dashboard')

    return render(request, 'core/grade_submission.html', {
        'form': form,
        'submission': submission
    })


# ==============================
# Public Views
# ==============================
def leaderboardView(request, pk):
    """Display leaderboard for a hackathon."""

    hackathon = get_object_or_404(Hackathon, pk=pk)
    submissions = Submission.objects.filter(hackathon=hackathon, score__gt=0).order_by('-score')

    return render(request, 'core/leaderboard.html', {
        'hackathon': hackathon,
        'submissions': submissions
    })
