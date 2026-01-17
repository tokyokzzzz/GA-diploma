# MindCraft - AI-Powered Productivity Platform

![MindCraft Logo](static/images/logo.png)

MindCraft is a comprehensive Django web application that combines **AI-powered scheduling**, the **Pomodoro Technique**, and **gamification** to help users achieve their goals efficiently.

## 🌟 Features

### 🤖 AI Schedule Generation
- **Greedy Algorithm**: Fast scheduling for simple tasks
- **Genetic Algorithm**: Advanced optimization for complex schedules
- Automatically distributes tasks across 6 months
- Respects fixed schedule conflicts (work, university, etc.)
- Calculates optimal Pomodoro sessions

### 🍅 Pomodoro Timer
- 25-minute focus sessions with automatic breaks
- **Strict Mode**: Cannot pause/stop once started
- Circular progress visualization
- Motivational quotes during sessions
- Celebration animations on completion
- Sound and vibration notifications

### 🎮 Gamification System
- **XP & Leveling**: Earn points for completing Pomodoros
- **Achievements**: Unlock badges for milestones
- **Leaderboard**: Compete with other users
- **Streak Tracking**: Maintain daily consistency

### 📊 Analytics Dashboard
- Pomodoros completed over time
- Time distribution by category
- Completion rate statistics
- Personal productivity insights
- Interactive charts (Chart.js)

### 📱 Mobile-First Design
- Responsive Bootstrap 5 interface
- Touch-friendly 44x44px targets
- Swipe gestures for calendar navigation
- Bottom navigation bar on mobile
- Dark mode support
- PWA capabilities (Add to Home Screen)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
cd d:\claude\mindcraft
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
copy .env.example .env
# Edit .env and set your SECRET_KEY
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Load initial achievements**
```bash
python manage.py shell
>>> from scheduler.models import Achievement
>>> Achievement.objects.create(name='first_pomodoro', description='Complete your first Pomodoro session', badge_icon='🎯', xp_reward=10, criteria={'pomodoros': 1})
>>> Achievement.objects.create(name='centurion', description='Complete 100 Pomodoros', badge_icon='💯', xp_reward=500, criteria={'pomodoros': 100})
>>> Achievement.objects.create(name='streak_master', description='Maintain a 7-day streak', badge_icon='🔥', xp_reward=100, criteria={'streak': 7})
>>> Achievement.objects.create(name='consistency_king', description='Maintain a 30-day streak', badge_icon='👑', xp_reward=1000, criteria={'streak': 30})
>>> exit()
```

8. **Run development server**
```bash
python manage.py runserver
```

9. **Access the application**
Open your browser and navigate to: `http://127.0.0.1:8000`

## 📖 Usage Guide

### 1. Create an Account
- Visit the homepage
- Click "Sign Up"
- Fill in your details

### 2. Generate AI Schedule
- Go to Dashboard → "Generate AI Schedule"
- Fill in your goal (e.g., "Learn Python")
- Set daily time commitment (e.g., 3 hours)
- Choose duration (1, 3, or 6 months)
- Set priority level (1-10)
- Add fixed schedule conflicts (university, work hours)
- Select AI algorithm (Greedy or Genetic)
- Click "Generate AI Schedule"

### 3. Complete Pomodoro Sessions
- View your calendar
- Click on a task
- Click "Start Pomodoro"
- Focus for 25 minutes (strict mode - cannot pause!)
- Earn XP and level up

### 4. Track Progress
- Visit Analytics page for detailed statistics
- Check Leaderboard to see your ranking
- View Profile for achievements

## 🎯 AI Algorithms Explained

### Greedy Algorithm
- **How it works**: Scores tasks by priority, urgency, and difficulty
- **Formula**: `score = 0.5 × priority + 0.3 × urgency + 0.2 × difficulty`
- **Best for**: Simple schedules, quick generation
- **Speed**: Fast (< 1 second)

### Genetic Algorithm
- **How it works**: Evolves population of schedules over generations
- **Process**: Random initialization → Fitness evaluation → Selection → Crossover → Mutation
- **Best for**: Complex schedules with many constraints
- **Speed**: Slower (2-3 seconds) but more optimized

## 🗂️ Project Structure

```
mindcraft/
├── manage.py
├── requirements.txt
├── Procfile
├── README.md
├── .env.example
├── productivity_app/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── scheduler/
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin configuration
│   └── ai_scheduler.py     # AI algorithms
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── calendar.html
│   ├── pomodoro.html
│   ├── analytics.html
│   └── ... (other templates)
└── static/
    ├── css/
    │   ├── style.css
    │   └── mobile.css
    └── js/
        ├── calendar.js
        ├── pomodoro.js
        └── charts.js
```

## 🚢 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
```bash
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

2. **Login to Heroku**
```bash
heroku login
```

3. **Create Heroku app**
```bash
heroku create mindcraft-app
```

4. **Set environment variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

5. **Deploy**
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

6. **Run migrations**
```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Railway Deployment

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login and deploy**
```bash
railway login
railway init
railway up
```

### PythonAnywhere Deployment

1. Upload code to PythonAnywhere
2. Create virtual environment
3. Install requirements
4. Configure WSGI file
5. Set up static files
6. Run migrations

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: PostgreSQL connection string (production)

### Pomodoro Settings
Users can customize in Settings page:
- Work duration: 15-45 minutes (default: 25)
- Short break: 3-10 minutes (default: 5)
- Long break: 10-30 minutes (default: 15)
- Strict mode: On/Off

## 📊 Database Models

- **UserProfile**: XP, level, streak, settings
- **Task**: Title, duration, priority, Pomodoros
- **FixedSchedule**: Unavailable time blocks
- **PomodoroSession**: Session tracking, XP awards
- **Achievement**: Badge definitions
- **UserAchievement**: Earned badges

## 🎨 Tech Stack

- **Backend**: Django 4.2+, Python 3.10+
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (dev), PostgreSQL (production)
- **Charts**: Chart.js
- **Calendar**: FullCalendar
- **Deployment**: Heroku, Railway, PythonAnywhere

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'decouple'`
**Solution**: Run `pip install python-decouple`

**Issue**: Static files not loading
**Solution**: Run `python manage.py collectstatic`

**Issue**: Database migrations failing
**Solution**: Delete `db.sqlite3` and run migrations again

## 📧 Support

For support, email support@mindcraft.com or open an issue on GitHub.

## 🙏 Acknowledgments

- Bootstrap 5 for responsive design
- Chart.js for analytics visualizations
- FullCalendar for calendar functionality
- Django community for excellent documentation

---

**Made with ❤️ by MindCraft Team**
