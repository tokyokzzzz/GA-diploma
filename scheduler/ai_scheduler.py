"""
AI Scheduling Algorithms for MindCraft.
Implements Greedy and Genetic algorithms for optimal task scheduling.
"""
import math
import random
from datetime import datetime, timedelta
from django.utils import timezone
from typing import List, Dict, Tuple


def calculate_pomodoros(duration_minutes: int) -> int:
    """
    Calculate number of Pomodoros needed.
    Formula: pomodoros = ceil(duration / 25)
    """
    return math.ceil(duration_minutes / 25)


def calculate_task_score(task_data: Dict, current_time: datetime) -> float:
    """
    AI scoring formula for task prioritization.
    
    Score = 0.5 × priority + 0.3 × urgency_factor + 0.2 × difficulty_factor
    
    Where:
    - urgency_factor = 10 × (1 - days_until_deadline / total_days)
    - difficulty_factor = pomodoros_needed / 10
    
    Args:
        task_data: Dictionary with 'priority', 'deadline', 'start_date', 'duration_minutes'
        current_time: Current datetime for urgency calculation
    
    Returns:
        float: AI-calculated priority score
    """
    priority = task_data.get('priority', 5)
    deadline = task_data.get('deadline')
    start_date = task_data.get('start_date', current_time)
    duration_minutes = task_data.get('duration_minutes', 25)
    
    # Calculate urgency factor
    days_until_deadline = (deadline - current_time).days
    total_days = (deadline - start_date).days
    if total_days <= 0:
        total_days = 1  # Avoid division by zero
    urgency_factor = 10 * (1 - (days_until_deadline / total_days))
    urgency_factor = max(0, min(10, urgency_factor))  # Clamp to 0-10
    
    # Calculate difficulty factor
    pomodoros_needed = calculate_pomodoros(duration_minutes)
    difficulty_factor = min(10, pomodoros_needed / 10 * 10)  # Scale to 0-10
    
    # Final score
    score = 0.5 * priority + 0.3 * urgency_factor + 0.2 * difficulty_factor
    
    return round(score, 2)


def is_time_blocked(check_time: datetime, fixed_schedules: List[Dict]) -> bool:
    """
    Check if a given time conflicts with fixed schedules.
    
    Args:
        check_time: DateTime to check
        fixed_schedules: List of fixed schedule dictionaries
    
    Returns:
        bool: True if time is blocked, False otherwise
    """
    for schedule in fixed_schedules:
        day_of_week = schedule.get('day_of_week', -1)
        start_time = schedule.get('start_time')
        end_time = schedule.get('end_time')
        
        # Check if day matches (-1 means all days)
        if day_of_week != -1 and check_time.weekday() != day_of_week:
            continue
        
        # Check if time falls within blocked period
        check_time_only = check_time.time()
        if start_time <= check_time_only <= end_time:
            return True
    
    return False


def greedy_scheduler(tasks: List[Dict], fixed_schedules: List[Dict], 
                     work_hours_start: int = 9, work_hours_end: int = 22) -> List[Dict]:
    """
    Greedy AI Algorithm for task scheduling.
    
    Algorithm:
    1. Calculate AI score for each task
    2. Sort tasks by score (descending)
    3. Assign to earliest available time slots
    4. Skip times blocked by fixed schedules
    5. Add Pomodoro breaks (5 min after each, 15 min after 4th)
    6. Return scheduled tasks with start times
    
    Args:
        tasks: List of task dictionaries
        fixed_schedules: List of fixed schedule dictionaries
        work_hours_start: Start of work hours (default 9 AM)
        work_hours_end: End of work hours (default 10 PM)
    
    Returns:
        List of tasks with scheduled_time assigned
    """
    from datetime import datetime, timedelta
    
    # Calculate scores and sort
    for task in tasks:
        task['ai_score'] = calculate_task_score(task, timezone.now())
    
    sorted_tasks = sorted(tasks, key=lambda x: x['ai_score'], reverse=True)
    
    # Start scheduling from start_date
    current_time = min(task.get('start_date', timezone.now()) for task in tasks)
    current_time = current_time.replace(hour=work_hours_start, minute=0, second=0, microsecond=0)
    
    scheduled_tasks = []
    pomodoro_count = 0
    
    for task in sorted_tasks:
        pomodoros_needed = calculate_pomodoros(task.get('duration_minutes', 25))
        
        for pomo in range(pomodoros_needed):
            # Find next available slot
            while True:
                # Check if within work hours
                if current_time.hour < work_hours_start:
                    current_time = current_time.replace(hour=work_hours_start, minute=0)
                elif current_time.hour >= work_hours_end:
                    # Move to next day
                    current_time = (current_time + timedelta(days=1)).replace(
                        hour=work_hours_start, minute=0, second=0, microsecond=0
                    )
                    pomodoro_count = 0  # Reset count for new day
                
                # Check if time is blocked
                if not is_time_blocked(current_time, fixed_schedules):
                    break
                
                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)
            
            # Schedule this Pomodoro
            if pomo == 0:  # First Pomodoro of task
                task['scheduled_time'] = current_time
            
            # Move time forward by 25 minutes (Pomodoro duration)
            current_time += timedelta(minutes=25)
            pomodoro_count += 1
            
            # Add break
            if pomodoro_count % 4 == 0:
                current_time += timedelta(minutes=15)  # Long break
            else:
                current_time += timedelta(minutes=5)  # Short break
        
        scheduled_tasks.append(task)
    
    return scheduled_tasks


def genetic_algorithm_scheduler(tasks: List[Dict], fixed_schedules: List[Dict],
                                population_size: int = 50, generations: int = 100) -> List[Dict]:
    """
    Genetic Algorithm for optimal task scheduling.
    
    Algorithm:
    1. Create random schedules (population)
    2. Evaluate fitness (high priority early, meet deadlines, respect constraints)
    3. Select best schedules (elitism)
    4. Crossover (combine schedules)
    5. Mutate (random changes)
    6. Repeat for generations
    7. Return best schedule found
    
    Args:
        tasks: List of task dictionaries
        fixed_schedules: List of fixed schedule dictionaries
        population_size: Number of schedules in population
        generations: Number of evolution iterations
    
    Returns:
        List of tasks with optimized scheduled_time
    """
    
    def create_random_schedule(tasks_list):
        """Create a random valid schedule."""
        schedule = []
        for task in tasks_list:
            # Random time within next 6 months
            random_days = random.randint(0, 180)
            random_hour = random.randint(9, 21)
            random_minute = random.choice([0, 30])
            
            start_date = task.get('start_date', timezone.now())
            scheduled_time = start_date + timedelta(days=random_days, hours=random_hour, minutes=random_minute)
            
            task_copy = task.copy()
            task_copy['scheduled_time'] = scheduled_time
            schedule.append(task_copy)
        
        return schedule
    
    def calculate_fitness(schedule):
        """
        Calculate fitness score for a schedule.
        Higher is better.
        """
        score = 0
        
        for task in schedule:
            # Reward high-priority tasks scheduled early
            days_from_start = (task['scheduled_time'] - task.get('start_date', timezone.now())).days
            priority_score = task.get('priority', 5) * (180 - days_from_start) / 180
            score += priority_score
            
            # Penalty for missing deadlines
            if task['scheduled_time'] > task.get('deadline', timezone.now() + timedelta(days=365)):
                score -= 100
            
            # Penalty for scheduling during fixed blocks
            if is_time_blocked(task['scheduled_time'], fixed_schedules):
                score -= 50
            
            # Reward for meeting urgency
            urgency = calculate_task_score(task, timezone.now())
            score += urgency * 2
        
        return score
    
    def crossover(parent1, parent2):
        """Combine two schedules."""
        crossover_point = len(parent1) // 2
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child
    
    def mutate(schedule, mutation_rate=0.1):
        """Randomly change some scheduled times."""
        for task in schedule:
            if random.random() < mutation_rate:
                # Mutate: shift time by random amount
                shift_days = random.randint(-7, 7)
                shift_hours = random.randint(-3, 3)
                task['scheduled_time'] += timedelta(days=shift_days, hours=shift_hours)
        return schedule
    
    # Initialize population
    population = [create_random_schedule(tasks) for _ in range(population_size)]
    
    # Evolution loop
    for generation in range(generations):
        # Evaluate fitness
        fitness_scores = [(schedule, calculate_fitness(schedule)) for schedule in population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Elitism: keep top 20%
        elite_count = population_size // 5
        new_population = [schedule for schedule, _ in fitness_scores[:elite_count]]
        
        # Create offspring
        while len(new_population) < population_size:
            # Tournament selection
            parent1 = random.choice(fitness_scores[:population_size // 2])[0]
            parent2 = random.choice(fitness_scores[:population_size // 2])[0]
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutation
            child = mutate(child)
            
            new_population.append(child)
        
        population = new_population
    
    # Return best schedule
    final_fitness = [(schedule, calculate_fitness(schedule)) for schedule in population]
    best_schedule = max(final_fitness, key=lambda x: x[1])[0]
    
    return best_schedule


def generate_6_month_schedule(user, goal_title: str, hours_per_day: int, 
                              total_months: int, priority: int, 
                              fixed_schedules: List[Dict], 
                              preferred_times: List[str] = None,
                              algorithm: str = 'greedy') -> Dict:
    """
    Main function to generate AI-powered 6-month schedule.
    
    Args:
        user: Django User object
        goal_title: Title of the goal/task
        hours_per_day: Hours to spend per day
        total_months: Duration in months (1, 3, or 6)
        priority: Priority level (1-10)
        fixed_schedules: List of user's fixed schedule conflicts
        preferred_times: List of preferred time slots
        algorithm: 'greedy' or 'genetic'
    
    Returns:
        Dictionary with schedule summary and created tasks
    """
    from django.utils import timezone
    
    # Calculate total time needed
    total_days = total_months * 30
    total_hours = hours_per_day * total_days
    total_minutes = total_hours * 60
    
    # Calculate Pomodoros per day
    pomodoros_per_day = math.ceil((hours_per_day * 60) / 25)
    
    # Create task data
    start_date = timezone.now()
    deadline = start_date + timedelta(days=total_days)
    
    # Break into daily tasks
    tasks_data = []
    for day in range(total_days):
        task_date = start_date + timedelta(days=day)
        
        task = {
            'title': f"{goal_title} - Day {day + 1}",
            'description': f"Daily session for {goal_title}",
            'duration_minutes': hours_per_day * 60,
            'priority': priority,
            'deadline': deadline,
            'start_date': task_date,
            'category': 'study',
        }
        tasks_data.append(task)
    
    # Run AI scheduling algorithm
    if algorithm == 'genetic':
        scheduled_tasks = genetic_algorithm_scheduler(tasks_data, fixed_schedules)
    else:
        scheduled_tasks = greedy_scheduler(tasks_data, fixed_schedules)
    
    # Create Task objects in database
    from scheduler.models import Task
    created_tasks = []
    
    for task_data in scheduled_tasks:
        task = Task.objects.create(
            user=user,
            title=task_data['title'],
            description=task_data.get('description', ''),
            duration_minutes=task_data['duration_minutes'],
            priority=task_data['priority'],
            deadline=task_data['deadline'],
            start_date=task_data['start_date'],
            scheduled_time=task_data.get('scheduled_time'),
            category=task_data.get('category', 'other'),
            ai_score=task_data.get('ai_score', 0),
        )
        task.calculate_pomodoros()
        created_tasks.append(task)
    
    # Return summary
    return {
        'success': True,
        'total_tasks': len(created_tasks),
        'total_pomodoros': sum(t.pomodoros_needed for t in created_tasks),
        'total_hours': total_hours,
        'pomodoros_per_day': pomodoros_per_day,
        'start_date': start_date,
        'end_date': deadline,
        'algorithm_used': algorithm,
    }
