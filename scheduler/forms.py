"""
Django forms for MindCraft.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, FixedSchedule, UserProfile


class UserRegistrationForm(UserCreationForm):
    """User registration form with email."""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ScheduleGeneratorForm(forms.Form):
    """Form for AI schedule generation."""
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
    ]
    
    TIME_CHOICES = [
        ('morning', 'Morning (6 AM - 12 PM)'),
        ('afternoon', 'Afternoon (12 PM - 6 PM)'),
        ('evening', 'Evening (6 PM - 10 PM)'),
        ('night', 'Night (10 PM - 2 AM)'),
    ]
    
    ALGORITHM_CHOICES = [
        ('greedy', 'Greedy Algorithm (Faster)'),
        ('genetic', 'Genetic Algorithm (More Optimized)'),
    ]
    
    goal_title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Learn Python'})
    )
    
    daily_hours = forms.IntegerField(
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '3'})
    )
    
    total_months = forms.ChoiceField(
        choices=DURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'})
    )
    
    preferred_times = forms.MultipleChoiceField(
        choices=TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    algorithm = forms.ChoiceField(
        choices=ALGORITHM_CHOICES,
        initial='greedy',
        widget=forms.RadioSelect
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class FixedScheduleForm(forms.ModelForm):
    """Form for adding fixed schedule conflicts."""
    class Meta:
        model = FixedSchedule
        fields = ['title', 'day_of_week', 'start_time', 'end_time', 'recurrence']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., University'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'recurrence': forms.Select(attrs={'class': 'form-select'}),
        }


class TaskForm(forms.ModelForm):
    """Form for manual task creation/editing."""
    class Meta:
        model = Task
        fields = ['title', 'description', 'duration_minutes', 'priority', 'deadline', 'category', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile settings."""
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture', 'theme_preference', 'work_duration', 
            'short_break', 'long_break', 'strict_mode',
            'daily_reminder_time', 'streak_reminders', 'achievement_notifications'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
            'work_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 15, 'max': 45}),
            'short_break': forms.NumberInput(attrs={'class': 'form-control', 'min': 3, 'max': 10}),
            'long_break': forms.NumberInput(attrs={'class': 'form-control', 'min': 10, 'max': 30}),
            'strict_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_reminder_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'streak_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'achievement_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
