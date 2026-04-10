from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail, send_mass_mail
from .models import User, ParticipantProfile, OrganizerProfile, JudgeProfile, Hackathon, Submission

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.PARTICIPANT:
            ParticipantProfile.objects.create(user=instance)
        elif instance.role == User.ORGANIZER:
            OrganizerProfile.objects.create(user=instance)
        elif instance.role == User.JUDGE:
            JudgeProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == User.PARTICIPANT:
        if hasattr(instance, 'participant_profile'):
            instance.participant_profile.save()
    elif instance.role == User.ORGANIZER:
        if hasattr(instance, 'organizer_profile'):
            instance.organizer_profile.save()
    elif instance.role == User.JUDGE:
        if hasattr(instance, 'judge_profile'):
            instance.judge_profile.save()

# ==============================
# 1. Welcome Email (Signup)
# ==============================
@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Welcome to CodeVerse!'
        message = (
            f"Hi {instance.email},\n\n"
            f"Welcome to CodeVerse! We are thrilled to have you on board as a {instance.get_role_display()}.\n\n"
            f"Make sure to hop into your dashboard and complete your profile so you can get the most out of our platform.\n\n"
            f"Happy hacking,\nThe CodeVerse Team"
        )
        send_mail(subject, message, None, [instance.email], fail_silently=True)

# ==============================
# 2. Security Alert (New Login)
# ==============================
@receiver(user_logged_in)
def send_login_alert(sender, user, request, **kwargs):
    subject = 'CodeVerse Security Alert: New Login'
    message = (
        f"Hi {user.email},\n\n"
        f"We noticed a new login to your CodeVerse account just now.\n"
        f"If this was you, you can safely ignore this email.\n\n"
        f"Stay secure,\nThe CodeVerse Team"
    )
    send_mail(subject, message, None, [user.email], fail_silently=True)

# ==============================
# 3. Hackathon Lifecycle (Open Announcement)
# ==============================
@receiver(pre_save, sender=Hackathon)
def track_hackathon_status(sender, instance, **kwargs):
    """Store the original status before saving."""
    if instance.pk:
        try:
            original = Hackathon.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except Hackathon.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None

@receiver(post_save, sender=Hackathon)
def broadcast_new_hackathon(sender, instance, created, **kwargs):
    """Broadcast an email if the hackathon is transitioned to 'open'."""
    original_status = getattr(instance, '_original_status', None)
    
    # Check if newly created and already open, or if it was just changed to open
    if (created and instance.status == 'open') or (original_status != 'open' and instance.status == 'open'):
        
        # Get all participant emails
        participant_emails = list(User.objects.filter(role=User.PARTICIPANT).values_list('email', flat=True))
        
        if participant_emails:
            subject = f"New Hackathon: {instance.title} is now Open!"
            message = (
                f"Hello Hackers!\n\n"
                f"A brand new hackathon '{instance.title}' has just opened registration.\n\n"
                f"Prize: {instance.prize_money or 'TBD'}\n"
                f"Starts: {instance.start_date.strftime('%b %d, %Y')}\n\n"
                f"Log in to CodeVerse and find a team today!\n\n"
                f"Happy coding,\nThe CodeVerse Team"
            )
            
            # send_mass_mail requires a tuple of messages in format (subject, message, sender, [recipient])
            messages = ((subject, message, None, [email]) for email in participant_emails)
            send_mass_mail(messages, fail_silently=True)

# ==============================
# 4. Grading System (Score Updated)
# ==============================
@receiver(pre_save, sender=Submission)
def track_submission_score(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = Submission.objects.get(pk=instance.pk)
            instance._original_score = original.score
        except Submission.DoesNotExist:
            instance._original_score = 0
    else:
        instance._original_score = 0

@receiver(post_save, sender=Submission)
def notify_score_updated(sender, instance, **kwargs):
    original_score = getattr(instance, '_original_score', 0)
    
    # Check if score just increased from 0
    if original_score == 0 and instance.score > 0:
        team_leader = instance.team.leader
        
        subject = f"Your project for {instance.hackathon.title} was graded!"
        message = (
            f"Hi {team_leader.email},\n\n"
            f"Great news! Your team's submission '{instance.project_title}' has been reviewed by the judges.\n\n"
            f"You scored: {instance.score}/100.\n\n"
            f"Log in to check the leaderboard to see where you stand!\n\n"
            f"Cheers,\nThe CodeVerse Team"
        )
        send_mail(subject, message, None, [team_leader.email], fail_silently=True)
