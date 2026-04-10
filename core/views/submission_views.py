# core/views/submission_views.py

"""
Submission Views
----------------
Handles:
- Project submission by participants
- Project grading by judges

Responsibilities:
- Ensure only team members can submit
- Ensure only judges can grade
- Prevent submissions when hackathon is closed
- Notify users via email after grading
"""

# ==============================
# Imports
# ==============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from ..forms import SubmissionForm, ScoreForm
from ..models import Team, TeamMember, Submission, User


# ==============================
# Project Submission View
# ==============================
@login_required(login_url='login')
def submitProjectView(request, team_id):
    """
    Submit or update a project for a team.

    Rules:
    - User must be a member of the team
    - Hackathon must be in 'open' state
    - Only one submission per team (update if exists)
    """

    # Ensure user belongs to the team
    team_member = get_object_or_404(
        TeamMember,
        team_id=team_id,
        user=request.user
    )

    team = team_member.team

    hackathon = team.hackathon

    # Block submissions if hackathon is not open
    if hackathon.status != 'open':
        return redirect('dashboard')

    # Fetch existing submission (if any)
    try:
        submission = team.submission
    except Submission.DoesNotExist:
        submission = None

    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=submission)

        if form.is_valid():
            sub = form.save(commit=False)
            sub.team = team
            sub.hackathon = hackathon
            sub.save()

            return redirect('dashboard')

    else:
        form = SubmissionForm(instance=submission)

    return render(request, 'core/submit_project.html', {
        'form': form,
        'team': team,
        'hackathon': hackathon
    })


# ==============================
# Submission Grading View (Judge)
# ==============================
@login_required(login_url='login')
def gradeSubmissionView(request, pk):
    """
    Grade a submission.

    Rules:
    - Only users with 'judge' role can access
    - Sends email notification after grading
    """

    # Restrict access to judges only
    if request.user.role != User.JUDGE:
        return redirect('dashboard')

    submission = get_object_or_404(Submission, pk=pk)

    if request.method == "POST":
        form = ScoreForm(request.POST, instance=submission)

        if form.is_valid():
            form.save()

            # Notify team leader via email
            send_mail(
                f'Project Graded: {submission.project_title}',
                (
                    f'Great news!\n\n'
                    f'Your project for \"{submission.hackathon.title}\" '
                    f'has just been graded.\n\n'
                    f'Score: {submission.score} / 100\n\n'
                    f'Check the leaderboard for rankings.\n\n'
                    f'- The CodeVerse Team'
                ),
                None,
                [submission.team.leader.email],
                fail_silently=False,
            )

            return redirect('dashboard')

    else:
        form = ScoreForm(instance=submission)

    return render(request, 'core/grade_submission.html', {
        'form': form,
        'submission': submission
    })