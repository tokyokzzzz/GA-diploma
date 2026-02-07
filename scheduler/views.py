"""
Views for MindCraft productivity app.
Handles authentication, schedule generation, Pomodoro sessions, analytics, and more.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum, Q, Avg
from datetime import datetime, timedelta
import json

from .models import Task, UserProfile, FixedSchedule, PomodoroSession, Achievement, UserAchievement
from .forms import UserRegistrationForm, ScheduleGeneratorForm, FixedScheduleForm, TaskForm, UserProfileForm
from .ai_scheduler import generate_6_month_schedule


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def home(request):
    """Landing page for non-authenticated users."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to MindCraft! Let\'s create your first schedule.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ============================================================================
# DASHBOARD & SCHEDULE GENERATION
# ============================================================================

@login_required
def dashboard(request):
    """Main dashboard after login."""
    profile = request.user.profile
    
    # Get today's tasks
    today = timezone.now().date()
    today_tasks = Task.objects.filter(
        user=request.user,
        scheduled_time__date=today,
        completed=False
    ).order_by('scheduled_time')
    
    # Get stats
    total_pomodoros = PomodoroSession.objects.filter(user=request.user, completed=True).count()
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    
    # Calculate XP progress to next level
    # Level formula: level = floor(sqrt(total_xp / 100))
    # Level 0: 0-99 XP, Level 1: 100-399 XP, Level 2: 400-899 XP, etc.
    current_level_xp = profile.level * profile.level * 100
    next_level_xp = (profile.level + 1) * (profile.level + 1) * 100
    xp_in_current_level = max(0, profile.total_xp - current_level_xp)
    xp_needed_for_next = next_level_xp - current_level_xp
    xp_progress = int((xp_in_current_level / xp_needed_for_next) * 100) if xp_needed_for_next > 0 else 0
    xp_progress = max(0, min(100, xp_progress))  # Clamp between 0-100
    xp_for_next_level = next_level_xp  # Total XP needed to reach next level
    
    context = {
        'profile': profile,
        'today_tasks': today_tasks,
        'total_pomodoros': total_pomodoros,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'has_tasks': total_tasks > 0,
        'xp_progress': xp_progress,
        'xp_for_next_level': xp_for_next_level,
        'xp_needed_for_next': xp_needed_for_next,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def schedule_generator(request):
    """AI schedule generator form."""
    if request.method == 'POST':
        form = ScheduleGeneratorForm(request.POST)
        
        if form.is_valid():
            # Get form data
            goal_title = form.cleaned_data['goal_title']
            daily_hours = form.cleaned_data['daily_hours']
            total_months = int(form.cleaned_data['total_months'])
            priority = form.cleaned_data['priority']
            algorithm = form.cleaned_data['algorithm']
            
            # Get user's fixed schedules
            fixed_schedules = list(FixedSchedule.objects.filter(user=request.user).values(
                'title', 'day_of_week', 'start_time', 'end_time', 'recurrence'
            ))
            
            # Generate schedule using AI
            result = generate_6_month_schedule(
                user=request.user,
                goal_title=goal_title,
                hours_per_day=daily_hours,
                total_months=total_months,
                priority=priority,
                fixed_schedules=fixed_schedules,
                algorithm=algorithm
            )
            
            if result['success']:
                messages.success(
                    request,
                    f'✨ AI generated {result["total_tasks"]} tasks with {result["total_pomodoros"]} Pomodoros!'
                )
                return redirect('calendar')
            else:
                messages.error(request, 'Failed to generate schedule. Please try again.')
    else:
        form = ScheduleGeneratorForm()
    
    # Get existing fixed schedules
    fixed_schedules = FixedSchedule.objects.filter(user=request.user)
    
    return render(request, 'schedule_form.html', {
        'form': form,
        'fixed_schedules': fixed_schedules,
    })


@login_required
def add_fixed_schedule(request):
    """Add fixed schedule conflict."""
    if request.method == 'POST':
        form = FixedScheduleForm(request.POST)
        if form.is_valid():
            fixed_schedule = form.save(commit=False)
            fixed_schedule.user = request.user
            fixed_schedule.save()
            messages.success(request, 'Fixed schedule added successfully!')
            return redirect('schedule_generator')
    else:
        form = FixedScheduleForm()
    
    return render(request, 'add_fixed_schedule.html', {'form': form})


@login_required
def delete_fixed_schedule(request, schedule_id):
    """Delete fixed schedule."""
    schedule = get_object_or_404(FixedSchedule, id=schedule_id, user=request.user)
    schedule.delete()
    messages.success(request, 'Fixed schedule removed.')
    return redirect('schedule_generator')


# ============================================================================
# CALENDAR & TASK MANAGEMENT
# ============================================================================

@login_required
def calendar_view(request):
    """Calendar view with tasks."""
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Get all user's tasks
    tasks = Task.objects.filter(user=request.user).order_by('scheduled_time')
    
    # Prepare tasks for calendar (JSON format)
    calendar_events = []
    for task in tasks:
        if task.scheduled_time:
            # Determine color based on priority
            if task.priority >= 8:
                color = '#EF4444'  # Red (high)
            elif task.priority >= 5:
                color = '#F59E0B'  # Orange (medium)
            else:
                color = '#10B981'  # Green (low)
            
            calendar_events.append({
                'id': str(task.id),
                'title': f"🍅 {task.pomodoros_needed} - {task.title}",
                'start': task.scheduled_time.isoformat(),
                'end': (task.scheduled_time + timedelta(minutes=task.duration_minutes)).isoformat(),
                'backgroundColor': color,
                'borderColor': color,
                'display': 'block',
                'textColor': '#ffffff',
                'extendedProps': {
                    'pomodoros_needed': task.pomodoros_needed,
                    'pomodoros_completed': task.pomodoros_completed,
                    'priority': task.priority,
                    'completed': task.completed,
                }
            })
    
    # Count completed tasks
    completed_tasks_count = tasks.filter(completed=True).count()
    
    context = {
        'calendar_events': json.dumps(calendar_events, cls=DjangoJSONEncoder),
        'tasks': tasks,
        'completed_tasks_count': completed_tasks_count,
    }
    
    return render(request, 'calendar.html', context)


@login_required
def task_detail(request, task_id):
    """Get task details (AJAX)."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'scheduled_time': task.scheduled_time.strftime('%Y-%m-%d %H:%M') if task.scheduled_time else None,
        'pomodoros_needed': task.pomodoros_needed,
        'pomodoros_completed': task.pomodoros_completed,
        'priority': task.priority,
        'completed': task.completed,
        'notes': task.notes,
        'completion_percentage': task.completion_percentage(),
    }
    
    return JsonResponse(data)


@login_required
def update_task(request, task_id):
    """Update task (mark complete, reschedule, etc.)."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'complete':
            task.completed = True
            task.save()
            # Award bonus XP for completing task on time
            if not task.is_overdue():
                request.user.profile.add_xp(50)
            messages.success(request, 'Task completed! +50 XP')
        
        elif action == 'reschedule':
            new_time = data.get('new_time')
            task.scheduled_time = datetime.fromisoformat(new_time)
            task.save()
            messages.success(request, 'Task rescheduled.')
        
        elif action == 'add_note':
            note = data.get('note')
            task.notes = note
            task.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def delete_task(request, task_id):
    """Delete task."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted.')
    return redirect('calendar')


# ============================================================================
# POMODORO TIMER
# ============================================================================

@login_required
def pomodoro_timer(request, task_id):
    """Full-screen Pomodoro timer page."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    profile = request.user.profile
    
    # Create new Pomodoro session
    session = PomodoroSession.objects.create(
        task=task,
        user=request.user,
        duration=profile.work_duration
    )
    
    context = {
        'task': task,
        'session': session,
        'work_duration': profile.work_duration,
        'short_break': profile.short_break,
        'long_break': profile.long_break,
        'strict_mode': profile.strict_mode,
    }
    
    return render(request, 'pomodoro.html', context)


@login_required
def complete_pomodoro(request, session_id):
    """Mark Pomodoro session as complete (AJAX)."""
    session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)
    
    if not session.completed:
        session.mark_complete()
        
        # Check for achievements
        check_achievements(request.user)
        
        return JsonResponse({
            'success': True,
            'xp_earned': session.xp_earned,
            'total_xp': request.user.profile.total_xp,
            'level': request.user.profile.level,
            'task_completed': session.task.completed,
        })
    
    return JsonResponse({'success': False, 'message': 'Already completed'}, status=400)


# ============================================================================
# ANALYTICS & STATISTICS
# ============================================================================

@login_required
def analytics(request):
    """Analytics and progress page."""
    profile = request.user.profile
    
    # Overview stats
    total_pomodoros = PomodoroSession.objects.filter(user=request.user, completed=True).count()
    total_hours = (total_pomodoros * 25) / 60  # Assuming 25-min Pomodoros
    completion_rate = 0
    
    total_tasks = Task.objects.filter(user=request.user).count()
    if total_tasks > 0:
        completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
        completion_rate = int((completed_tasks / total_tasks) * 100)
    
    # Pomodoros per day (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_pomodoros = []
    
    for i in range(30):
        day = thirty_days_ago + timedelta(days=i)
        count = PomodoroSession.objects.filter(
            user=request.user,
            completed=True,
            start_time__date=day.date()
        ).count()
        daily_pomodoros.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Time distribution by category
    category_stats = Task.objects.filter(user=request.user).values('category').annotate(
        total_minutes=Sum('duration_minutes')
    )
    
    # Most productive time
    hour_stats = PomodoroSession.objects.filter(
        user=request.user,
        completed=True
    ).extra(select={'hour': 'CAST(strftime("%%H", start_time) AS INTEGER)'}).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')
    
    most_productive_hour = hour_stats[0]['hour'] if hour_stats else 9
    
    context = {
        'profile': profile,
        'total_pomodoros': total_pomodoros,
        'total_hours': round(total_hours, 1),
        'completion_rate': completion_rate,
        'daily_pomodoros': json.dumps(daily_pomodoros),
        'category_stats': json.dumps(list(category_stats)),
        'most_productive_hour': most_productive_hour,
    }
    
    return render(request, 'analytics.html', context)


# ============================================================================
# LEADERBOARD
# ============================================================================

@login_required
def leaderboard(request):
    """Leaderboard page showing top users."""
    # Get top 10 users by Pomodoro count
    from django.contrib.auth.models import User
    from django.db.models import Count
    
    top_users = User.objects.annotate(
        pomodoro_count=Count('pomodoro_sessions', filter=Q(pomodoro_sessions__completed=True))
    ).order_by('-pomodoro_count')[:10]
    
    # Add rank and additional data
    leaderboard_data = []
    for rank, user in enumerate(top_users, 1):
        try:
            # Try to get profile, skip if doesn't exist
            profile = user.profile
            leaderboard_data.append({
                'rank': rank,
                'username': user.username,
                'pomodoro_count': user.pomodoro_count,
                'total_xp': profile.total_xp,
                'level': profile.level,
                'current_streak': profile.current_streak,
                'is_current_user': user == request.user,
            })
        except:
            # Skip users without profiles
            continue
    
    # Find current user's rank if not in top 10
    current_user_rank = None
    if request.user not in top_users:
        all_users = User.objects.annotate(
            pomodoro_count=Count('pomodoro_sessions', filter=Q(pomodoro_sessions__completed=True))
        ).order_by('-pomodoro_count')
        
        for rank, user in enumerate(all_users, 1):
            if user == request.user:
                try:
                    profile = user.profile
                    current_user_rank = {
                        'rank': rank,
                        'username': user.username,
                        'pomodoro_count': user.pomodoro_count,
                        'total_xp': profile.total_xp,
                        'level': profile.level,
                        'current_streak': profile.current_streak,
                    }
                except:
                    pass
                break
    
    context = {
        'leaderboard': leaderboard_data,
        'current_user_rank': current_user_rank,
    }
    
    return render(request, 'leaderboard.html', context)


# ============================================================================
# PROFILE & ACHIEVEMENTS
# ============================================================================

@login_required
def profile(request):
    """User profile with achievements."""
    profile = request.user.profile
    
    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    
    # Get all achievements to show locked ones
    all_achievements = Achievement.objects.all()
    earned_achievement_ids = user_achievements.values_list('achievement_id', flat=True)
    
    context = {
        'profile': profile,
        'user_achievements': user_achievements,
        'all_achievements': all_achievements,
        'earned_achievement_ids': earned_achievement_ids,
    }
    
    return render(request, 'profile.html', context)


# ============================================================================
# SETTINGS
# ============================================================================

@login_required
def settings(request):
    """Settings page."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('settings')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'settings.html', {'form': form})


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_achievements(user):
    """Check and award achievements based on user activity."""
    profile = user.profile
    
    # Get total completed Pomodoros
    total_pomodoros = PomodoroSession.objects.filter(user=user, completed=True).count()
    
    # Define achievement criteria
    achievements_to_check = [
        ('first_pomodoro', total_pomodoros >= 1),
        ('centurion', total_pomodoros >= 100),
        ('streak_master', profile.current_streak >= 7),
        ('consistency_king', profile.current_streak >= 30),
    ]
    
    for achievement_name, condition in achievements_to_check:
        if condition:
            try:
                achievement = Achievement.objects.get(name=achievement_name)
                UserAchievement.objects.get_or_create(
                    user=user,
                    achievement=achievement
                )
            except Achievement.DoesNotExist:
                pass


# ============================================================================
# ROADMAP VIEWS
# ============================================================================
# REMOVED - Roadmap feature removed

