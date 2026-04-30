# Fitness Tracker Web Application

**Author:** Freddy Karras  
**Institution:** Virginia Tech

## Project Overview

A comprehensive web-based fitness tracking application that allows users to monitor their workout activities, track weight progress, log daily steps and calorie intake, and visualize their fitness data through interactive charts.

### Video Demonstration
[Insert YouTube link here after recording]

## Problem Statement

Many individuals struggle to maintain consistent fitness routines due to lack of tracking and visualization of their progress. This application provides an easy-to-use platform for:
- Logging various types of workouts with detailed metrics
- Tracking weight changes over time
- Monitoring daily activity (steps and calories)
- Visualizing fitness data to identify patterns and progress

## Key Features

### 1. User Authentication
- Secure registration and login system
- Password hashing for security
- Session management

### 2. Workout Tracking
- Log multiple workout types (Running, Cycling, Gym, Yoga, etc.)
- Track duration, calories burned, and distance
- Add personal notes for each workout
- View and delete workout history

### 3. Weight Monitoring
- Record weight entries with timestamps
- Visual line chart showing weight progress over time
- Historical weight data tracking

### 4. Daily Statistics
- Log daily steps count
- Track calories consumed
- View weekly activity summary

### 5. Analytics Dashboard
- Interactive charts powered by Chart.js:
  - Pie chart for workout type distribution
  - Bar charts for total duration and calories by workout type
  - Line chart for daily steps trends
- 30-day rolling data visualization

## Technologies Used

### Backend
- **Python 3.x**: Primary programming language
- **Flask**: Web framework for routing and server logic
- **Flask-SQLAlchemy**: ORM for database management
- **SQLite**: Lightweight database for data storage
- **Werkzeug**: Password hashing and security

### Frontend
- **HTML5**: Page structure and content
- **CSS3**: Styling and responsive design
- **JavaScript**: Client-side interactions
- **Chart.js**: Data visualization library

## Project Structure

```
fitness-tracker-web-app/
├── code/
│   ├── app.py                  # Main Flask application
│   ├── templates/              # HTML templates
│   │   ├── base.html          # Base template with navigation
│   │   ├── home.html          # Landing page
│   │   ├── register.html      # User registration
│   │   ├── login.html         # User login
│   │   ├── dashboard.html     # Main dashboard
│   │   ├── workouts.html      # Workout list view
│   │   ├── add_workout.html   # Add workout form
│   │   ├── weight_tracking.html  # Weight tracking page
│   │   ├── daily_stats.html   # Daily statistics
│   │   └── analytics.html     # Analytics with charts
│   └── static/                # Static files
│       ├── style.css          # CSS stylesheet
│       └── script.js          # JavaScript functions
├── data/
│   └── fitness.db            # SQLite database (created on first run)
├── tests/
│   └── test_app.py           # Test cases
├── docs/
│   └── screenshots/          # Application screenshots
├── report/
│   └── project_report.pdf    # Final project report
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fitness-tracker-web-app.git
   cd fitness-tracker-web-app
   ```

2. **Create and activate virtual environment:**
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Mac/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   cd code
   python app.py
   ```
   
   The database will be automatically created in the `data/` directory on first run.

## How to Run

1. **Ensure virtual environment is activated**

2. **Navigate to the code directory:**
   ```bash
   cd code
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your web browser and go to: `http://127.0.0.1:5001`

5. **Create an account:**
   - Click "Register" and create a new account
   - Login with your credentials
   - Start tracking your fitness!

## Usage Guide

### First Time Setup
1. Register for a new account
2. Log in with your credentials
3. Add your first workout from the dashboard or workouts page
4. Log your current weight in the Weight Tracking section
5. Update daily stats with today's steps and calories

### Daily Usage
1. Log in to your account
2. Add today's workout with all relevant details
3. Update your daily steps and calorie intake
4. Check the analytics page to view your progress

### Understanding the Dashboard
- **Quick Stats Cards**: Shows weekly totals and current weight
- **Quick Actions**: Fast access to add data
- **Recent Workouts**: Last 5 workouts at a glance
- **Today's Activity**: Current day's steps and calories

### Using Analytics
- View workout distribution by type
- Compare total duration across workout types
- Analyze calories burned by activity
- Track daily steps trends over 14 days

## Testing

### Running Automated Tests
```bash
cd tests
python test_app.py
```

All 19 tests should pass successfully.

## Database Schema

### User Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- created_at

### Workout Table
- id (Primary Key)
- user_id (Foreign Key)
- workout_type
- duration
- calories
- distance
- notes
- date

### Weight Table
- id (Primary Key)
- user_id (Foreign Key)
- weight
- date

### DailyStats Table
- id (Primary Key)
- user_id (Foreign Key)
- steps
- calories_consumed
- date

## API Endpoints

### Authentication
- `GET /` - Home page
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - Logout user

### Main Features
- `GET /dashboard` - Main dashboard
- `GET /workouts` - View all workouts
- `GET/POST /add_workout` - Add new workout
- `GET /delete_workout/<id>` - Delete workout
- `GET /weight_tracking` - Weight tracking page
- `POST /add_weight` - Add weight entry
- `GET /daily_stats` - Daily statistics page
- `POST /update_daily_stats` - Update daily stats
- `GET /analytics` - Analytics dashboard

### API Routes (JSON)
- `GET /api/workout_data` - Workout data for charts
- `GET /api/weight_data` - Weight data for charts
- `GET /api/daily_stats_data` - Daily stats for charts

## Security Features

- Password hashing using Werkzeug's security module
- Session-based authentication
- Login required decorators for protected routes
- SQL injection prevention through SQLAlchemy ORM

## Learning Outcomes

Through this project, I achieved the following learning objectives:

1. **Full-Stack Web Development**: Gained hands-on experience building a complete web application with backend (Flask/Python) and frontend (HTML/CSS/JavaScript)

2. **Database Management**: Learned to design database schemas, implement relationships, and perform CRUD operations using SQLAlchemy ORM

3. **Data Visualization**: Mastered Chart.js library to create interactive and responsive data visualizations

4. **User Authentication**: Implemented secure user registration and login systems with password hashing

5. **RESTful API Design**: Created API endpoints for data retrieval and learned JSON data handling

6. **Project Management**: Practiced scoping, planning, and executing a project within time constraints

## Credits and References

- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Chart.js Documentation**: https://www.chartjs.org/docs/
- **MDN Web Docs**: For HTML, CSS, and JavaScript references
- **Course Materials**: Virginia Tech CS Problem Solving course lectures and tutorials

## Author Information

**Name**: Freddy Karras  
**Course**: CS Problem Solving, Fall 2025  
**Institution**: Virginia Tech

## Honor Code Statement

I pledge that I have neither given nor received unauthorized assistance on this project. All code was written by me with guidance from official documentation, course materials, and Large Language Models (LLMs) as permitted by the project guidelines.

## License

This project is created for educational purposes as part of Virginia Tech coursework. All rights reserved.

---

**Last Updated**: December 2025  
**Version**: 1.0.0
