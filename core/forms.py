from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils import timezone # Added to check current time
from .models import User, Hackathon, Submission, ParticipantProfile, OrganizerProfile, JudgeProfile

class UserSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    mobile_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 1234567890'}))

    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name', 'mobile_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            
            profile = None
            if user.role == User.PARTICIPANT and hasattr(user, 'participant_profile'):
                profile = user.participant_profile
            elif user.role == User.ORGANIZER and hasattr(user, 'organizer_profile'):
                profile = user.organizer_profile
            elif user.role == User.JUDGE and hasattr(user, 'judge_profile'):
                profile = user.judge_profile
            
            if profile:
                profile.first_name = self.cleaned_data.get('first_name')
                profile.last_name = self.cleaned_data.get('last_name')
                profile.mobile_number = self.cleaned_data.get('mobile_number')
                profile.save()
                
        return user

class HackathonForm(forms.ModelForm):
    class Meta:
        model = Hackathon
        # ADDED 'status' to the fields list
        fields = ['title', 'description', 'start_date', 'end_date', 'prize_money', 'status']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'prize_money': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ₹50,000 or Swag'}),
            # ADDED widget for the dropdown menu
            'status': forms.Select(attrs={'class': 'form-select'}), 
        }

    # Added validation logic
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            # 1. Block start dates that are in the past
            if start_date < timezone.now():
                self.add_error('start_date', "Start date cannot be in the past.")
            
            # 2. Block end dates that happen before the start date
            if end_date <= start_date:
                self.add_error('end_date', "End date must be after the start date.")

        return cleaned_data

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['project_title', 'description', 'repo_link', 'demo_video']
        widgets = {
            'project_title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'repo_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'e.g., https://github.com/yourname/project'}),
            'demo_video': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional YouTube or Drive link'}),
        }

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'placeholder': 'Enter score (0-100)'})
        }

class ParticipantProfileForm(forms.ModelForm):
    class Meta:
        model = ParticipantProfile
        fields = ['first_name', 'last_name', 'mobile_number', 'profile_picture', 'university', 'degree', 'graduation_year', 'github_url', 'linkedin_url', 'skills', 'resume']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 1234567890'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Stanford University'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., B.S. Computer Science'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2025'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/yourusername'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Python, React, Django...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

class OrganizerProfileForm(forms.ModelForm):
    class Meta:
        model = OrganizerProfile
        fields = ['first_name', 'last_name', 'mobile_number', 'profile_picture', 'organization_name', 'designation', 'organization_website', 'linkedin_url']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 1234567890'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization or Company Name'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Event Lead'}),
            'organization_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
        }

class JudgeProfileForm(forms.ModelForm):
    class Meta:
        model = JudgeProfile
        fields = ['first_name', 'last_name', 'mobile_number', 'profile_picture', 'company_name', 'job_title', 'linkedin_url', 'expertise']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 1234567890'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'expertise': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '10 years experience in AI and Web3'}),
        }