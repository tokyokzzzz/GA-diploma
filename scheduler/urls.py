"""
URL routing for scheduler app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Schedule Generation
    path('dashboard/', views.dashboard, name='dashboard'),
    path('schedule/generate/', views.schedule_generator, name='schedule_generator'),
    path('schedule/fixed/add/', views.add_fixed_schedule, name='add_fixed_schedule'),
    path('schedule/fixed/delete/<int:schedule_id>/', views.delete_fixed_schedule, name='delete_fixed_schedule'),
    
    # Calendar & Tasks
    path('calendar/', views.calendar_view, name='calendar'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    
    # Pomodoro
    path('pomodoro/<int:task_id>/', views.pomodoro_timer, name='pomodoro_timer'),
    path('pomodoro/complete/<int:session_id>/', views.complete_pomodoro, name='complete_pomodoro'),
    
    # Analytics & Leaderboard
    path('analytics/', views.analytics, name='analytics'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    
    # Profile & Settings
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
]
