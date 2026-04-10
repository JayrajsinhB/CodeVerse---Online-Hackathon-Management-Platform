# core/views/hackathon_views.py

"""
Hackathon Views
---------------
Handles:
- Hackathon creation, editing, deletion
- Listing and viewing hackathons
- Team creation and joining
- Organizer team management

Responsibilities:
- Enforce role-based access (organizer vs participant)
- Manage team lifecycle inside hackathons
- Handle invite-based team joining
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail

from ..forms import HackathonForm
from ..models import Hackathon, Team, TeamMember
from ..utils import is_organizer


# ==============================
# Hackathon Creation (Organizer)
# ==============================
@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def createHackathonView(request):
    """
    Create a new hackathon.

    Only accessible by organizers.
    Automatically assigns the creator.
    """

    if request.method == "POST":
        form = HackathonForm(request.POST)

        if form.is_valid():
            hackathon = form.save(commit=False)
            hackathon.created_by = request.user
            hackathon.save()
            return redirect('dashboard')

    else:
        form = HackathonForm()

    return render(request, 'core/create_hackathon.html', {'form': form})


# ==============================
# Hackathon Listing
# ==============================
@login_required(login_url='login')
def hackathonListView(request):
    """
    Display all non-draft hackathons.
    Ordered by newest first.
    """

    hackathons = Hackathon.objects.exclude(status='draft').order_by('-start_date')

    return render(request, 'core/hackathon_list.html', {
        'hackathons': hackathons
    })


# ==============================
# Hackathon Detail + Team Logic
# ==============================
@login_required(login_url='login')
def hackathonDetailView(request, pk):
    """
    Hackathon detail page.

    Features:
    - View hackathon details
    - Create a team
    - Join a team using invite code

    Restrictions:
    - Teams can only be created/joined when hackathon is 'open'
    - User can only belong to one team per hackathon
    """

    hackathon = get_object_or_404(Hackathon, pk=pk)

    # Check if user already belongs to a team in this hackathon
    membership = TeamMember.objects.filter(
        user=request.user,
        team__hackathon=hackathon
    ).first()

    user_team = membership.team if membership else None

    if request.method == "POST":

        # Block actions if hackathon is not open
        if hackathon.status != 'open':
            return redirect('hackathon_detail', pk=hackathon.id)

        # -------- Create Team --------
        if 'create_team' in request.POST:
            team_name = request.POST.get('team_name')

            if team_name and not user_team:
                team = Team.objects.create(
                    name=team_name,
                    hackathon=hackathon,
                    leader=request.user
                )

                TeamMember.objects.create(
                    team=team,
                    user=request.user
                )

                # Send confirmation email
                send_mail(
                    f'Team Created: {team.name}',
                    (
                        f'You have successfully created the team "{team.name}" '
                        f'for {hackathon.title}.\n\n'
                        f'Your invite code is: {team.access_code}\n'
                        f'Share it with your teammates.\n\n'
                        f'- The CodeVerse Team'
                    ),
                    None,
                    [request.user.email],
                    fail_silently=False,
                )

                return redirect('hackathon_detail', pk=hackathon.id)

        # -------- Join Team --------
        elif 'join_team' in request.POST:
            invite_code = request.POST.get('invite_code')

            if invite_code and not user_team:
                team = Team.objects.filter(
                    access_code=invite_code,
                    hackathon=hackathon
                ).first()

                if team:
                    TeamMember.objects.create(
                        team=team,
                        user=request.user
                    )

                    # Send confirmation email
                    send_mail(
                        f'Welcome to Team {team.name}!',
                        (
                            f'You have successfully joined "{team.name}" '
                            f'for {hackathon.title}.\n\n'
                            f'Happy hacking!\n\n'
                            f'- The CodeVerse Team'
                        ),
                        None,
                        [request.user.email],
                        fail_silently=False,
                    )

                    return redirect('hackathon_detail', pk=hackathon.id)

    return render(request, 'core/hackathon_detail.html', {
        'hackathon': hackathon,
        'user_team': user_team
    })


# ==============================
# Hackathon Editing (Organizer)
# ==============================
@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def editHackathonView(request, pk):
    """
    Edit an existing hackathon.
    Only accessible by the creator.
    """

    hackathon = get_object_or_404(
        Hackathon,
        pk=pk,
        created_by=request.user
    )

    if request.method == "POST":
        form = HackathonForm(request.POST, instance=hackathon)

        if form.is_valid():
            form.save()
            return redirect('dashboard')

    else:
        form = HackathonForm(instance=hackathon)

    return render(request, 'core/create_hackathon.html', {
        'form': form,
        'hackathon': hackathon
    })


# ==============================
# Hackathon Deletion (Organizer)
# ==============================
@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def deleteHackathonView(request, pk):
    """
    Delete a hackathon.
    Only accessible by the creator.
    """

    hackathon = get_object_or_404(
        Hackathon,
        pk=pk,
        created_by=request.user
    )

    if request.method == "POST":
        hackathon.delete()
        return redirect('dashboard')

    return render(request, 'core/delete_hackathon.html', {
        'hackathon': hackathon
    })


# ==============================
# Team Management (Organizer)
# ==============================
@login_required(login_url='login')
@user_passes_test(is_organizer, login_url='dashboard')
def manageTeamsView(request, pk):
    """
    View and manage all teams in a hackathon.
    Only accessible by the organizer.
    """

    hackathon = get_object_or_404(
        Hackathon,
        pk=pk,
        created_by=request.user
    )

    teams = hackathon.teams.all().prefetch_related('members')

    return render(request, 'core/manage_teams.html', {
        'hackathon': hackathon,
        'teams': teams
    })