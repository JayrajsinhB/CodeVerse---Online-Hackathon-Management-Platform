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

    ROLE_CHOICES = (
        ('owner','owner'),
        ('user','user'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Hackathon(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    host_name = models.CharField(max_length=100, default='CodeVerse')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    prize_money = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_hackathons', null=True, blank=True)

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=100)
    access_code = models.CharField(max_length=10, unique=True)
    # Re-added the leader so we know who has permission to submit
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    # Using 'through' to link the ManyToMany field properly to your custom TeamMember table
    members = models.ManyToManyField(User, through='TeamMember', related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} in {self.team.name}"

# Submission is separated out! One Team = One Submission.
class Submission(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='submission')
    project_title = models.CharField(max_length=200)
    repo_link = models.URLField(max_length=255)
    demo_video = models.URLField(max_length=255, null=True, blank=True)
    description = models.TextField()
    score = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission: {self.project_title} by {self.team.name}"