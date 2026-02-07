"""
Database models for MindCraft productivity app.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import math


class UserProfile(models.Model):
    """Extended user profile with gamification data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    theme_preference = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    
    # Pomodoro settings
    work_duration = models.IntegerField(default=25)  # minutes
    short_break = models.IntegerField(default=5)  # minutes
    long_break = models.IntegerField(default=15)  # minutes
    strict_mode = models.BooleanField(default=True)  # Cannot stop timer
    
    # Notification settings
    daily_reminder_time = models.TimeField(null=True, blank=True)
    streak_reminders = models.BooleanField(default=True)
    achievement_notifications = models.BooleanField(default=True)
    
    def update_level(self):
        """Calculate level based on XP: Level = floor(sqrt(total_XP / 100))"""
        self.level = math.floor(math.sqrt(self.total_xp / 100))
        self.save()
    
    def add_xp(self, amount):
        """Add XP and update level."""
        self.total_xp += amount
        self.update_level()
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level} ({self.total_xp} XP)"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    instance.profile.save()


class Task(models.Model):
    """Task model with AI scheduling data."""
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('study', 'Study'),
        ('personal', 'Personal'),
        ('health', 'Health'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField()  # Total duration
    priority = models.IntegerField(default=5)  # 1-10
    deadline = models.DateTimeField()
    start_date = models.DateTimeField()
    scheduled_time = models.DateTimeField(null=True, blank=True)  # AI-assigned time
    pomodoros_needed = models.IntegerField(default=0)
    pomodoros_completed = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    ai_score = models.FloatField(default=0.0)  # AI-calculated priority score
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-priority', 'deadline']
    
    def calculate_pomodoros(self):
        """Calculate number of Pomodoros needed: ceil(duration / 25)"""
        self.pomodoros_needed = math.ceil(self.duration_minutes / 25)
        self.save()
    
    def is_overdue(self):
        """Check if task is past deadline."""
        from django.utils import timezone
        return timezone.now() > self.deadline and not self.completed
    
    def completion_percentage(self):
        """Calculate completion percentage."""
        if self.pomodoros_needed == 0:
            return 0
        return int((self.pomodoros_completed / self.pomodoros_needed) * 100)
    
    def __str__(self):
        return f"{self.title} - {self.pomodoros_completed}/{self.pomodoros_needed} Pomodoros"


class FixedSchedule(models.Model):
    """User's unavailable time blocks (university, work, etc.)"""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
        (-1, 'All Days'),
    ]
    
    RECURRENCE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fixed_schedules')
    title = models.CharField(max_length=100)  # e.g., "University", "Work"
    day_of_week = models.IntegerField(choices=DAY_CHOICES, default=-1)
    start_time = models.TimeField()
    end_time = models.TimeField()
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='weekly')
    
    def __str__(self):
        return f"{self.title} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class PomodoroSession(models.Model):
    """Individual Pomodoro session tracking."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=25)  # minutes
    completed = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_time']
    
    def mark_complete(self):
        """Mark session as complete and award XP."""
        from django.utils import timezone
        self.completed = True
        self.end_time = timezone.now()
        self.xp_earned = 10  # Base XP for completing Pomodoro
        self.save()
        
        # Update task progress
        self.task.pomodoros_completed += 1
        if self.task.pomodoros_completed >= self.task.pomodoros_needed:
            self.task.completed = True
            self.xp_earned += 50  # Bonus for completing task
        self.task.save()
        
        # Award XP to user
        self.user.profile.add_xp(self.xp_earned)
        
        # Update streak
        self.user.profile.update_streak()
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class Achievement(models.Model):
    """Achievement/Badge definitions."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_icon = models.CharField(max_length=50)  # Emoji or icon class
    xp_reward = models.IntegerField(default=0)
    criteria = models.JSONField()  # Criteria for earning (e.g., {"pomodoros": 100})
    
    def __str__(self):
        return f"{self.badge_icon} {self.name}"


class UserAchievement(models.Model):
    """User's earned achievements."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


# Add method to UserProfile for streak tracking
def update_streak(self):
    """Update user's streak based on activity."""
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    
    if self.last_activity_date is None:
        self.current_streak = 1
        self.last_activity_date = today
    elif self.last_activity_date == today:
        # Already active today, no change
        pass
    elif self.last_activity_date == today - timedelta(days=1):
        # Consecutive day
        self.current_streak += 1
        self.last_activity_date = today
        
        # Check for streak bonus
        if self.current_streak == 7:
            self.add_xp(100)  # 7-day streak bonus
    else:
        # Streak broken
        self.current_streak = 1
        self.last_activity_date = today
    
    # Update longest streak
    if self.current_streak > self.longest_streak:
        self.longest_streak = self.current_streak
    
    self.save()

# Attach method to UserProfile
UserProfile.update_streak = update_streak
