from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    # ===== Role Constants =====
    ORGANIZER = 'organizer'
    PARTICIPANT = 'participant'
    JUDGE = 'judge'

    ROLE_CHOICES = [
        (ORGANIZER, 'Organizer'),
        (PARTICIPANT, 'Participant'),
        (JUDGE, 'Judge'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=PARTICIPANT
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email} ({self.role})"

class AbstractProfile(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    class Meta:
        abstract = True

class ParticipantProfile(AbstractProfile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participant_profile')
    university = models.CharField(max_length=150, null=True, blank=True)
    degree = models.CharField(max_length=100, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    github_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    skills = models.TextField(help_text="Comma separated skills, e.g., Python, React", null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    def __str__(self):
        return f"Participant Profile: {self.user.email}"

class OrganizerProfile(AbstractProfile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organizer_profile')
    organization_name = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    organization_website = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Organizer Profile: {self.user.email}"

class JudgeProfile(AbstractProfile):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='judge_profile')
    company_name = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    expertise = models.TextField(help_text="Short Bio / Expertise", null=True, blank=True)

    def __str__(self):
        return f"Judge Profile: {self.user.email}"

class Hackathon(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Registration & Hacking Open'),
        ('judging', 'Judging in Progress'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    host_name = models.CharField(max_length=100, default='CodeVerse')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    prize_money = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_hackathons')
    
    # --- NEW STATUS FIELD ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title


# class Team(models.Model):
#     name = models.CharField(max_length=100)
#     access_code = models.CharField(max_length=10, unique=True)

#     hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='teams')

#     # Re-added the leader so we know who has permission to submit
#     leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
#     # Using 'through' to link the ManyToMany field properly to your custom TeamMember table
#     members = models.ManyToManyField(User, through='TeamMember', related_name='teams')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

import random
import string

class Team(models.Model):
    name = models.CharField(max_length=100)
    access_code = models.CharField(max_length=10, unique=True, blank=True)

    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')

    members = models.ManyToManyField(User, through='TeamMember', related_name='teams')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.access_code:
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if not Team.objects.filter(access_code=code).exists():
                    self.access_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['team', 'user'], name='unique_team_member')
        ]

    def __str__(self):
        return f"{self.user.email} in {self.team.name}"

# Submission is separated out! One Team = One Submission.
class Submission(models.Model):
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE, related_name='submissions')
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='submission')

    project_title = models.CharField(max_length=200)
    repo_link = models.URLField(max_length=255)
    demo_video = models.URLField(max_length=255, null=True, blank=True)
    description = models.TextField()

    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission: {self.project_title} by {self.team.name}"