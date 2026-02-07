"""
Management command to initialize sample achievements.
Run with: python manage.py init_achievements
"""
from django.core.management.base import BaseCommand
from scheduler.models import Achievement


class Command(BaseCommand):
    help = 'Initialize sample achievements'

    def handle(self, *args, **kwargs):
        achievements = [
            {
                'name': 'first_pomodoro',
                'description': 'Complete your first Pomodoro session',
                'badge_icon': '🎯',
                'xp_reward': 10,
                'criteria': {'pomodoros': 1}
            },
            {
                'name': 'early_bird',
                'description': 'Complete 10 morning Pomodoros (6 AM - 12 PM)',
                'badge_icon': '🌅',
                'xp_reward': 50,
                'criteria': {'morning_pomodoros': 10}
            },
            {
                'name': 'night_owl',
                'description': 'Complete 10 evening Pomodoros (10 PM - 2 AM)',
                'badge_icon': '🦉',
                'xp_reward': 50,
                'criteria': {'night_pomodoros': 10}
            },
            {
                'name': 'streak_master',
                'description': 'Maintain a 7-day streak',
                'badge_icon': '🔥',
                'xp_reward': 100,
                'criteria': {'streak': 7}
            },
            {
                'name': 'centurion',
                'description': 'Complete 100 total Pomodoros',
                'badge_icon': '💯',
                'xp_reward': 500,
                'criteria': {'pomodoros': 100}
            },
            {
                'name': 'marathon_runner',
                'description': 'Complete 10 Pomodoros in one day',
                'badge_icon': '🏃',
                'xp_reward': 200,
                'criteria': {'daily_pomodoros': 10}
            },
            {
                'name': 'consistency_king',
                'description': 'Maintain a 30-day streak',
                'badge_icon': '👑',
                'xp_reward': 1000,
                'criteria': {'streak': 30}
            },
            {
                'name': 'dedicated_learner',
                'description': 'Complete 50 study category Pomodoros',
                'badge_icon': '📚',
                'xp_reward': 300,
                'criteria': {'study_pomodoros': 50}
            },
            {
                'name': 'work_warrior',
                'description': 'Complete 50 work category Pomodoros',
                'badge_icon': '💼',
                'xp_reward': 300,
                'criteria': {'work_pomodoros': 50}
            },
            {
                'name': 'level_10',
                'description': 'Reach Level 10',
                'badge_icon': '⭐',
                'xp_reward': 500,
                'criteria': {'level': 10}
            },
        ]

        for ach_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=ach_data['name'],
                defaults=ach_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created achievement: {achievement.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Achievement already exists: {achievement.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully initialized achievements!'))
