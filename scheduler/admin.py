"""
Django admin configuration for MindCraft.
"""
from django.contrib import admin
from .models import UserProfile, Task, FixedSchedule, PomodoroSession, Achievement, UserAchievement


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_xp', 'current_streak', 'theme_preference']
    list_filter = ['theme_preference', 'strict_mode']
    search_fields = ['user__username', 'user__email']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'scheduled_time', 'pomodoros_completed', 'pomodoros_needed', 'completed']
    list_filter = ['completed', 'priority', 'category']
    search_fields = ['title', 'user__username']
    date_hierarchy = 'scheduled_time'


@admin.register(FixedSchedule)
class FixedScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'day_of_week', 'start_time', 'end_time', 'recurrence']
    list_filter = ['day_of_week', 'recurrence']
    search_fields = ['title', 'user__username']


@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'start_time', 'duration', 'completed', 'xp_earned']
    list_filter = ['completed', 'start_time']
    search_fields = ['user__username', 'task__title']
    date_hierarchy = 'start_time'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_icon', 'xp_reward']
    search_fields = ['name', 'description']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement', 'earned_at']
    search_fields = ['user__username', 'achievement__name']
    date_hierarchy = 'earned_at'
