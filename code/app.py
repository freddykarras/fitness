"""
Fitness Tracker Web Application
Author: Freddy Karras
Course: CS Problem Solving - Fall 2025
Virginia Tech

This Flask application tracks user fitness data including workouts, weight, steps,
and calories. It provides data visualization using Chart.js and user authentication.
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from sqlalchemy import func
import os

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Configure database with absolute path
basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(os.path.dirname(basedir), 'data')
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, 'fitness.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ============= DATABASE MODELS =============

class User(db.Model):
    """
    User model for authentication and profile management
    Stores user credentials and basic profile information
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships to other tables
    workouts = db.relationship('Workout', backref='user', lazy=True, cascade='all, delete-orphan')
    weights = db.relationship('Weight', backref='user', lazy=True, cascade='all, delete-orphan')
    daily_stats = db.relationship('DailyStats', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)


class Workout(db.Model):
    """
    Workout model to track exercise sessions
    Stores workout type, duration, and calories burned
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_type = db.Column(db.String(50), nullable=False)  # Running, Gym, Cycling, etc.
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    calories = db.Column(db.Integer)  # Calories burned
    distance = db.Column(db.Float)  # Distance in miles (optional)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert workout to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'workout_type': self.workout_type,
            'duration': self.duration,
            'calories': self.calories,
            'distance': self.distance,
            'notes': self.notes,
            'date': self.date.strftime('%Y-%m-%d %H:%M')
        }


class Weight(db.Model):
    """
    Weight model to track user weight over time
    Enables progress tracking and visualization
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Weight in pounds
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert weight entry to dictionary"""
        return {
            'id': self.id,
            'weight': self.weight,
            'date': self.date.strftime('%Y-%m-%d')
        }


class DailyStats(db.Model):
    """
    Daily statistics model for steps and calorie tracking
    Stores daily activity metrics
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    steps = db.Column(db.Integer, default=0)
    calories_consumed = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, default=datetime.utcnow().date)

    def to_dict(self):
        """Convert daily stats to dictionary"""
        return {
            'id': self.id,
            'steps': self.steps,
            'calories_consumed': self.calories_consumed,
            'date': self.date.strftime('%Y-%m-%d')
        }


# ============= HELPER FUNCTIONS =============

def login_required(f):
    """Decorator to require login for protected routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============= AUTHENTICATION ROUTES =============

@app.route('/')
def home():
    """Landing page - redirects to dashboard if logged in"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and authentication handler"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Log out current user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ============= MAIN APPLICATION ROUTES =============

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing overview of fitness data"""
    user_id = session['user_id']
    
    # Get recent workouts (last 5)
    recent_workouts = Workout.query.filter_by(user_id=user_id).order_by(
        Workout.date.desc()
    ).limit(5).all()
    
    # Get latest weight
    latest_weight = Weight.query.filter_by(user_id=user_id).order_by(
        Weight.date.desc()
    ).first()
    
    # Get today's stats
    today = datetime.utcnow().date()
    today_stats = DailyStats.query.filter_by(user_id=user_id, date=today).first()
    
    # Calculate weekly workout summary
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= week_ago
    ).all()
    
    total_weekly_duration = sum(w.duration for w in weekly_workouts)
    total_weekly_calories = sum(w.calories or 0 for w in weekly_workouts)
    
    return render_template('dashboard.html',
                         recent_workouts=recent_workouts,
                         latest_weight=latest_weight,
                         today_stats=today_stats,
                         total_weekly_duration=total_weekly_duration,
                         total_weekly_calories=total_weekly_calories,
                         workout_count=len(weekly_workouts))


@app.route('/workouts')
@login_required
def workouts():
    """View all workouts"""
    user_id = session['user_id']
    all_workouts = Workout.query.filter_by(user_id=user_id).order_by(
        Workout.date.desc()
    ).all()
    return render_template('workouts.html', workouts=all_workouts)


@app.route('/add_workout', methods=['GET', 'POST'])
@login_required
def add_workout():
    """Add new workout entry"""
    if request.method == 'POST':
        user_id = session['user_id']
        
        workout_type = request.form.get('workout_type')
        duration = int(request.form.get('duration'))
        calories = request.form.get('calories')
        distance = request.form.get('distance')
        notes = request.form.get('notes')
        
        new_workout = Workout(
            user_id=user_id,
            workout_type=workout_type,
            duration=duration,
            calories=int(calories) if calories else None,
            distance=float(distance) if distance else None,
            notes=notes
        )
        
        try:
            db.session.add(new_workout)
            db.session.commit()
            flash('Workout added successfully!', 'success')
            return redirect(url_for('workouts'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding workout. Please try again.', 'danger')
    
    return render_template('add_workout.html')


@app.route('/delete_workout/<int:workout_id>')
@login_required
def delete_workout(workout_id):
    """Delete a workout entry"""
    user_id = session['user_id']
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first_or_404()
    
    try:
        db.session.delete(workout)
        db.session.commit()
        flash('Workout deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting workout.', 'danger')
    
    return redirect(url_for('workouts'))


@app.route('/weight_tracking')
@login_required
def weight_tracking():
    """View weight tracking page"""
    user_id = session['user_id']
    weights = Weight.query.filter_by(user_id=user_id).order_by(Weight.date.desc()).all()
    return render_template('weight_tracking.html', weights=weights)


@app.route('/add_weight', methods=['POST'])
@login_required
def add_weight():
    """Add new weight entry"""
    user_id = session['user_id']
    weight = float(request.form.get('weight'))
    
    new_weight = Weight(user_id=user_id, weight=weight)
    
    try:
        db.session.add(new_weight)
        db.session.commit()
        flash('Weight recorded successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error recording weight.', 'danger')
    
    return redirect(url_for('weight_tracking'))


@app.route('/daily_stats')
@login_required
def daily_stats():
    """View and manage daily statistics"""
    user_id = session['user_id']
    today = datetime.utcnow().date()
    
    # Get or create today's stats
    stats = DailyStats.query.filter_by(user_id=user_id, date=today).first()
    if not stats:
        stats = DailyStats(user_id=user_id, date=today)
        db.session.add(stats)
        db.session.commit()
    
    # Get last 7 days of stats
    week_ago = today - timedelta(days=7)
    recent_stats = DailyStats.query.filter(
        DailyStats.user_id == user_id,
        DailyStats.date >= week_ago
    ).order_by(DailyStats.date.desc()).all()
    
    return render_template('daily_stats.html', today_stats=stats, recent_stats=recent_stats)


@app.route('/update_daily_stats', methods=['POST'])
@login_required
def update_daily_stats():
    """Update today's daily statistics"""
    user_id = session['user_id']
    today = datetime.utcnow().date()
    
    steps = int(request.form.get('steps', 0))
    calories = int(request.form.get('calories', 0))
    
    stats = DailyStats.query.filter_by(user_id=user_id, date=today).first()
    
    if stats:
        stats.steps = steps
        stats.calories_consumed = calories
    else:
        stats = DailyStats(user_id=user_id, date=today, steps=steps, calories_consumed=calories)
        db.session.add(stats)
    
    try:
        db.session.commit()
        flash('Daily stats updated!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating stats.', 'danger')
    
    return redirect(url_for('daily_stats'))


@app.route('/analytics')
@login_required
def analytics():
    """Analytics page with data visualizations"""
    return render_template('analytics.html')


# ============= API ENDPOINTS FOR CHART.JS =============

@app.route('/api/workout_data')
@login_required
def api_workout_data():
    """API endpoint for workout visualization data"""
    user_id = session['user_id']
    
    # Get last 30 days of workouts
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.date >= thirty_days_ago
    ).order_by(Workout.date).all()
    
    # Group by workout type
    workout_types = {}
    for workout in workouts:
        if workout.workout_type not in workout_types:
            workout_types[workout.workout_type] = {
                'count': 0,
                'total_duration': 0,
                'total_calories': 0
            }
        workout_types[workout.workout_type]['count'] += 1
        workout_types[workout.workout_type]['total_duration'] += workout.duration
        workout_types[workout.workout_type]['total_calories'] += workout.calories or 0
    
    return jsonify({
        'labels': list(workout_types.keys()),
        'counts': [data['count'] for data in workout_types.values()],
        'durations': [data['total_duration'] for data in workout_types.values()],
        'calories': [data['total_calories'] for data in workout_types.values()]
    })


@app.route('/api/weight_data')
@login_required
def api_weight_data():
    """API endpoint for weight tracking visualization"""
    user_id = session['user_id']
    
    weights = Weight.query.filter_by(user_id=user_id).order_by(Weight.date).all()
    
    return jsonify({
        'dates': [w.date.strftime('%Y-%m-%d') for w in weights],
        'weights': [w.weight for w in weights]
    })


@app.route('/api/daily_stats_data')
@login_required
def api_daily_stats_data():
    """API endpoint for daily stats visualization"""
    user_id = session['user_id']
    
    # Get last 14 days
    fourteen_days_ago = datetime.utcnow().date() - timedelta(days=14)
    stats = DailyStats.query.filter(
        DailyStats.user_id == user_id,
        DailyStats.date >= fourteen_days_ago
    ).order_by(DailyStats.date).all()
    
    return jsonify({
        'dates': [s.date.strftime('%Y-%m-%d') for s in stats],
        'steps': [s.steps for s in stats],
        'calories': [s.calories_consumed for s in stats]
    })


# ============= DATABASE INITIALIZATION =============

def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
        print(f"Database location: {db_path}")


# ============= RUN APPLICATION =============

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)