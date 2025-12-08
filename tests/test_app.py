"""
Test Suite for Fitness Tracker Application
Author: Freddy Karras
Course: CS Problem Solving - Fall 2025

This file contains unit tests for the fitness tracker web application.
Tests cover user authentication, database operations, and main features.
"""

import unittest
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../code')))

from app import app, db, User, Workout, Weight, DailyStats
from datetime import datetime, timedelta

class FitnessTrackerTestCase(unittest.TestCase):
    """Test case for Fitness Tracker application"""
    
    def setUp(self):
        """Set up test client and database before each test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after each test"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    # ============= Authentication Tests =============
    
    def test_home_page(self):
        """Test that home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Track Your Fitness Journey', response.data)
    
    def test_registration_page_loads(self):
        """Test that registration page loads"""
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create Account', response.data)
    
    def test_user_registration(self):
        """Test user can register successfully"""
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check user was added to database
        with app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
    
    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        # Register first user
        self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test1@example.com',
            'password': 'testpass123'
        })
        
        # Try to register with same username
        response = self.app.post('/register', data={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'testpass456'
        }, follow_redirects=True)
        
        self.assertIn(b'Username already exists', response.data)
    
    def test_login_success(self):
        """Test successful login"""
        # Register a user first
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.app.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, follow_redirects=True)
        
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_logout(self):
        """Test logout functionality"""
        # Register and login
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        with self.app as client:
            client.post('/login', data={
                'username': 'testuser',
                'password': 'testpass123'
            })
            
            # Logout
            response = client.get('/logout', follow_redirects=True)
            self.assertIn(b'logged out', response.data)
    
    # ============= Workout Tests =============
    
    def create_test_user_and_login(self):
        """Helper function to create and login a test user"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        self.app.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        return user_id
    
    def test_add_workout(self):
        """Test adding a workout"""
        user_id = self.create_test_user_and_login()
        
        response = self.app.post('/add_workout', data={
            'workout_type': 'Running',
            'duration': '30',
            'calories': '300',
            'distance': '3.5',
            'notes': 'Good run!'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify workout was added to database
        with app.app_context():
            workout = Workout.query.filter_by(user_id=user_id).first()
            self.assertIsNotNone(workout)
            self.assertEqual(workout.workout_type, 'Running')
            self.assertEqual(workout.duration, 30)
    
    def test_view_workouts(self):
        """Test viewing workouts page"""
        self.create_test_user_and_login()
        
        response = self.app.get('/workouts')
        self.assertEqual(response.status_code, 200)
    
    def test_delete_workout(self):
        """Test deleting a workout"""
        user_id = self.create_test_user_and_login()
        
        # Add a workout first
        with app.app_context():
            workout = Workout(
                user_id=user_id,
                workout_type='Cycling',
                duration=45,
                calories=400
            )
            db.session.add(workout)
            db.session.commit()
            workout_id = workout.id
        
        # Delete the workout
        response = self.app.get(f'/delete_workout/{workout_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify workout was deleted
        with app.app_context():
            workout = Workout.query.get(workout_id)
            self.assertIsNone(workout)
    
    # ============= Weight Tracking Tests =============
    
    def test_add_weight(self):
        """Test adding weight entry"""
        user_id = self.create_test_user_and_login()
        
        response = self.app.post('/add_weight', data={
            'weight': '175.5'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify weight was added
        with app.app_context():
            weight = Weight.query.filter_by(user_id=user_id).first()
            self.assertIsNotNone(weight)
            self.assertEqual(weight.weight, 175.5)
    
    def test_weight_tracking_page(self):
        """Test weight tracking page loads"""
        self.create_test_user_and_login()
        
        response = self.app.get('/weight_tracking')
        self.assertEqual(response.status_code, 200)
    
    # ============= Daily Stats Tests =============
    
    def test_update_daily_stats(self):
        """Test updating daily statistics"""
        user_id = self.create_test_user_and_login()
        
        response = self.app.post('/update_daily_stats', data={
            'steps': '10000',
            'calories': '2000'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify stats were updated
        with app.app_context():
            today = datetime.utcnow().date()
            stats = DailyStats.query.filter_by(
                user_id=user_id,
                date=today
            ).first()
            self.assertIsNotNone(stats)
            self.assertEqual(stats.steps, 10000)
            self.assertEqual(stats.calories_consumed, 2000)
    
    # ============= API Endpoint Tests =============
    
    def test_api_workout_data(self):
        """Test workout data API endpoint"""
        user_id = self.create_test_user_and_login()
        
        # Add some test workouts
        with app.app_context():
            workouts = [
                Workout(user_id=user_id, workout_type='Running', duration=30, calories=300),
                Workout(user_id=user_id, workout_type='Gym', duration=60, calories=400),
                Workout(user_id=user_id, workout_type='Running', duration=25, calories=250)
            ]
            for workout in workouts:
                db.session.add(workout)
            db.session.commit()
        
        response = self.app.get('/api/workout_data')
        self.assertEqual(response.status_code, 200)
        
        # Check JSON response
        data = response.get_json()
        self.assertIn('labels', data)
        self.assertIn('counts', data)
        self.assertIn('durations', data)
    
    def test_api_weight_data(self):
        """Test weight data API endpoint"""
        user_id = self.create_test_user_and_login()
        
        # Add test weight entries
        with app.app_context():
            weights = [
                Weight(user_id=user_id, weight=180.0),
                Weight(user_id=user_id, weight=178.5),
                Weight(user_id=user_id, weight=177.0)
            ]
            for weight in weights:
                db.session.add(weight)
            db.session.commit()
        
        response = self.app.get('/api/weight_data')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('dates', data)
        self.assertIn('weights', data)
        self.assertEqual(len(data['weights']), 3)
    
    # ============= Access Control Tests =============
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in', response.data)
    
    def test_add_workout_requires_login(self):
        """Test that adding workout requires authentication"""
        response = self.app.get('/add_workout', follow_redirects=True)
        self.assertIn(b'Please log in', response.data)
    
    # ============= Database Model Tests =============
    
    def test_user_password_hashing(self):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('mypassword')
            
            # Password should be hashed, not stored as plaintext
            self.assertNotEqual(user.password_hash, 'mypassword')
            
            # Check password should work
            self.assertTrue(user.check_password('mypassword'))
            self.assertFalse(user.check_password('wrongpassword'))
    
    def test_workout_to_dict(self):
        """Test workout serialization"""
        with app.app_context():
            workout = Workout(
                user_id=1,
                workout_type='Running',
                duration=30,
                calories=300,
                distance=3.5,
                notes='Great run!',
                date=datetime.utcnow()  # Add the date explicitly
            )
            
            workout_dict = workout.to_dict()
            self.assertEqual(workout_dict['workout_type'], 'Running')
            self.assertEqual(workout_dict['duration'], 30)
            self.assertIn('date', workout_dict)


def run_tests():
    """Run all tests and display results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(FitnessTrackerTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    run_tests()