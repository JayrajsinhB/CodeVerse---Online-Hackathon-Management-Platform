# core/views/public_views.py

"""
Public Views
------------
Handles:
- Public-facing pages accessible without special permissions

Current:
- Leaderboard display for hackathons
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, get_object_or_404

from ..models import Hackathon, Submission, User


# ==============================
# Leaderboard View
# ==============================
def leaderboardView(request, pk):
    """
    Display leaderboard for a specific hackathon.

    Behavior:
    - Fetch hackathon by ID
    - Show submissions with score > 0
    - Order by highest score first
    """

    hackathon = get_object_or_404(Hackathon, pk=pk)

    submissions = (
        Submission.objects
        .filter(hackathon=hackathon, score__gt=0)
        .order_by('-score')
    )

    return render(request, 'core/leaderboard.html', {
        'hackathon': hackathon,
        'submissions': submissions
    })

# ==============================
# Profile Display View
# ==============================
def profileDisplayView(request, user_id):
    """
    Display a user's public or private profile.
    
    Behavior:
    - Target user fetched using user_id
    - Renders different details based on the user's role
    """
    target_user = get_object_or_404(User, pk=user_id)
    profile = None

    if target_user.role == User.PARTICIPANT and hasattr(target_user, 'participant_profile'):
        profile = target_user.participant_profile
    elif target_user.role == User.ORGANIZER and hasattr(target_user, 'organizer_profile'):
        profile = target_user.organizer_profile
    elif target_user.role == User.JUDGE and hasattr(target_user, 'judge_profile'):
        profile = target_user.judge_profile

    return render(request, 'core/profile_display.html', {
        'target_user': target_user,
        'profile': profile
    })