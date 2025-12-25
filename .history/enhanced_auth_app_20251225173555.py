"""
Enhanced Smart Toilet Hygiene System with Simple Authentication
Dual interface system for public users and cleaning staff
Real-time toilet condition monitoring with interactive map
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import json
import random
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import uuid
from functools import wraps

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

CORS(app)

# User database (in production, use proper database)
users_db = {
    'user@example.com': {
        'password': generate_password_hash('password123'),
        'role': 'public',
        'name': 'Public User',
        'created_at': datetime.now().isoformat(),
        'last_login': None
    },
    'cleaner@example.com': {
        'password': generate_password_hash('password123'),
        'role': 'cleaner',
        'name': 'Cleaning Staff',
        'created_at': datetime.now().isoformat(),
        'last_login': None
    },
    'admin@example.com': {
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'System Admin',
        'created_at': datetime.now().isoformat(),
        'last_login': None
    }
}

# Toilet locations (simulated data for demonstration)
toilets_data = [
    {
        'id': 'toilet_001',
        'name': 'Central Park Public Toilet',
        'lat': 28.6139,
        'lng': 77.2090,
        'address': 'Central Park, Connaught Place, New Delhi',
        'type': 'public',
        'hygiene_score': 85,
        'status': 'Clean',
        'last_cleaned': datetime.now() - timedelta(hours=2),
        'next_scheduled': datetime.now() + timedelta(hours=4),
        'cleaner_assigned': 'cleaner@example.com',
        'occupancy': 'low',
        'water_available': True,
        'soap_available': True,
        'paper_available': True,
        'reviews': [
            {'user': 'user@example.com', 'rating': 4, 'comment': 'Very clean', 'timestamp': datetime.now() - timedelta(days=1)}
        ],
        'icon': '🚻',
        'path_points': [[28.6139, 77.2090], [28.6145, 77.2095], [28.6150, 77.2100]]
    },
    {
        'id': 'toilet_002',
        'name': 'Metro Station Toilet',
        'lat': 28.6159,
        'lng': 77.2110,
        'address': 'Rajiv Chowk Metro Station, New Delhi',
        'type': 'metro',
        'hygiene_score': 45,
        'status': 'Moderate',
        'last_cleaned': datetime.now() - timedelta(hours=6),
        'next_scheduled': datetime.now() + timedelta(hours=2),
        'cleaner_assigned': 'cleaner@example.com',
        'occupancy': 'high',
        'water_available': True,
        'soap_available': False,
        'paper_available': True,
        'reviews': [],
        'icon': '🚇',
        'path_points': [[28.6159, 77.2110], [28.6165, 77.2115], [28.6170, 77.2120]]
    },
    {
        'id': 'toilet_003',
        'name': 'Shopping Mall Restroom',
        'lat': 28.6179,
        'lng': 77.2070,
        'address': 'City Walk Mall, Saket, New Delhi',
        'type': 'mall',
        'hygiene_score': 25,
        'status': 'Dirty',
        'last_cleaned': datetime.now() - timedelta(hours=8),
        'next_scheduled': datetime.now() - timedelta(hours=1),
        'cleaner_assigned': None,
        'occupancy': 'medium',
        'water_available': False,
        'soap_available': False,
        'paper_available': False,
        'reviews': [
            {'user': 'user@example.com', 'rating': 1, 'comment': 'Very dirty, no water', 'timestamp': datetime.now() - timedelta(hours=2)}
        ],
        'icon': '🏬',
        'path_points': [[28.6179, 77.2070], [28.6185, 77.2075], [28.6190, 77.2080]]
    },
    # New toilets added
    {
        'id': 'toilet_004',
        'name': 'Hospital Restroom',
        'lat': 28.6200,
        'lng': 77.2150,
        'address': 'AIIMS Hospital, New Delhi',
        'type': 'hospital',
        'hygiene_score': 75,
        'status': 'Clean',
        'last_cleaned': datetime.now() - timedelta(hours=1),
        'next_scheduled': datetime.now() + timedelta(hours=3),
        'cleaner_assigned': 'cleaner@example.com',
        'occupancy': 'medium',
        'water_available': True,
        'soap_available': True,
        'paper_available': True,
        'reviews': [],
        'icon': '🏥',
        'path_points': [[28.6200, 77.2150], [28.6205, 77.2155], [28.6210, 77.2160]]
    },
    {
        'id': 'toilet_005',
        'name': 'University Campus Toilet',
        'lat': 28.6080,
        'lng': 77.2050,
        'address': 'Delhi University North Campus',
        'type': 'university',
        'hygiene_score': 35,
        'status': 'Moderate',
        'last_cleaned': datetime.now() - timedelta(hours=5),
        'next_scheduled': datetime.now() + timedelta(hours=1),
        'cleaner_assigned': None,
        'occupancy': 'high',
        'water_available': True,
        'soap_available': False,
        'paper_available': False,
        'reviews': [],
        'icon': '🎓',
        'path_points': [[28.6080, 77.2050], [28.6085, 77.2055], [28.6090, 77.2060]]
    },
    {
        'id': 'toilet_006',
        'name': 'Gas Station Restroom',
        'lat': 28.6250,
        'lng': 77.2200,
        'address': 'Indian Oil Petrol Station, NH8',
        'type': 'gas_station',
        'hygiene_score': 20,
        'status': 'Dirty',
        'last_cleaned': datetime.now() - timedelta(hours=10),
        'next_scheduled': datetime.now() - timedelta(hours=2),
        'cleaner_assigned': None,
        'occupancy': 'low',
        'water_available': False,
        'soap_available': False,
        'paper_available': False,
        'reviews': [],
        'icon': '⛽',
        'path_points': [[28.6250, 77.2200], [28.6255, 77.2205], [28.6260, 77.2210]]
    }
]

# Real-time updates storage
real_time_updates = []

# Background thread for simulating real-time changes
def simulate_real_time_updates():
    """Simulate real-time changes in toilet conditions with enhanced realism"""
    global real_time_updates  # Access the global variable
    while True:
        time.sleep(8)  # Update every 8 seconds for more frequent updates
        
        # Randomly update a toilet condition
        toilet = random.choice(toilets_data)
        
        # Simulate realistic degradation patterns based on toilet type and usage
        degradation_rate = {
            'gas_station': 0.25,      # High degradation
            'university': 0.20,       # High usage
            'metro': 0.18,            # Medium-high usage
            'mall': 0.15,             # Medium usage
            'public': 0.12,             # Standard usage
            'hospital': 0.08          # Lower degradation due to strict maintenance
        }.get(toilet['type'], 0.15)
        
        # Simulate occupancy impact
        occupancy_multiplier = {
            'high': 1.5,
            'medium': 1.0,
            'low': 0.7
        }.get(toilet['occupancy'], 1.0)
        
        effective_degradation = degradation_rate * occupancy_multiplier
        
        # Simulate gradual degradation or improvement
        if toilet['status'] == 'Clean':
            if random.random() < effective_degradation:  # Realistic degradation chance
                score_drop = random.randint(8, 20) * occupancy_multiplier
                toilet['hygiene_score'] = max(50, toilet['hygiene_score'] - int(score_drop))
                toilet['status'] = 'Moderate'
                toilet['last_updated'] = datetime.now()
                
                # Update amenities based on degradation
                if random.random() < 0.3:
                    toilet['soap_available'] = False
                if random.random() < 0.2:
                    toilet['paper_available'] = False
                
                # Create update notification
                update = {
                    'id': str(uuid.uuid4()),
                    'toilet_id': toilet['id'],
                    'toilet_name': toilet['name'],
                    'previous_status': 'Clean',
                    'new_status': 'Moderate',
                    'new_score': toilet['hygiene_score'],
                    'timestamp': datetime.now(),
                    'type': 'status_change',
                    'icon': toilet['icon']
                }
                real_time_updates.append(update)
                
        elif toilet['status'] == 'Moderate':
            if random.random() < effective_degradation * 1.2:  # Higher chance to change from moderate
                if random.random() < 0.4:  # 40% chance to become clean (cleaned by staff)
                    score_increase = random.randint(25, 45)
                    toilet['hygiene_score'] = min(95, toilet['hygiene_score'] + score_increase)
                    toilet['status'] = 'Clean'
                    toilet['last_cleaned'] = datetime.now()
                    toilet['last_updated'] = datetime.now()
                    
                    # Restore amenities when cleaned
                    toilet['water_available'] = True
                    toilet['soap_available'] = True
                    toilet['paper_available'] = True
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Moderate',
                        'new_status': 'Clean',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'cleaned',
                        'icon': toilet['icon']
                    }
                    real_time_updates.append(update)
                else:  # 60% chance to become dirty
                    score_drop = random.randint(15, 35) * occupancy_multiplier
                    toilet['hygiene_score'] = max(10, toilet['hygiene_score'] - int(score_drop))
                    toilet['status'] = 'Dirty'
                    toilet['last_updated'] = datetime.now()
                    
                    # More amenities fail when dirty
                    if random.random() < 0.5:
                        toilet['water_available'] = False
                    toilet['soap_available'] = False
                    if random.random() < 0.4:
                        toilet['paper_available'] = False
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Moderate',
                        'new_status': 'Dirty',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'status_change',
                        'icon': toilet['icon']
                    }
                    real_time_updates.append(update)
                    
        elif toilet['status'] == 'Dirty':
            if random.random() < 0.08:  # Lower chance to improve from dirty (requires cleaning)
                if random.random() < 0.7:  # 70% chance to become moderate
                    toilet['hygiene_score'] = min(60, toilet['hygiene_score'] + random.randint(15, 30))
                    toilet['status'] = 'Moderate'
                    toilet['last_updated'] = datetime.now()
                    
                    # Partial restoration of amenities
                    toilet['water_available'] = True
                    if random.random() < 0.6:
                        toilet['soap_available'] = True
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Dirty',
                        'new_status': 'Moderate',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'status_change',
                        'icon': toilet['icon']
                    }
                    real_time_updates.append(update)
                else:  # 30% chance to become clean (thorough cleaning)
                    toilet['hygiene_score'] = min(90, toilet['hygiene_score'] + random.randint(30, 50))
                    toilet['status'] = 'Clean'
                    toilet['last_cleaned'] = datetime.now()
                    toilet['last_updated'] = datetime.now()
                    
                    # Full restoration
                    toilet['water_available'] = True
                    toilet['soap_available'] = True
                    toilet['paper_available'] = True
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Dirty',
                        'new_status': 'Clean',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'cleaned',
                        'icon': toilet['icon']
                    }
                    real_time_updates.append(update)
        
        # Keep only last 50 updates to prevent memory issues
        if len(real_time_updates) > 50:
            real_time_updates = real_time_updates[-50:]

# Start background thread
update_thread = threading.Thread(target=simulate_real_time_updates, daemon=True)
update_thread.start()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_email' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            user_role = session.get('user_role')
            if user_role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Main landing page - redirect to simplified login"""
    return redirect(url_for('simple_login'))

@app.route('/enhanced')
@login_required
def enhanced_dashboard():
    """Enhanced public dashboard with 3D icons and directions"""
    return render_template('public_dashboard_enhanced.html')

@app.route('/test')
def test():
    """Test route"""
    return "Test route working!"

@app.route('/auth')
def auth():
    """Authentication page"""
    return render_template('auth.html')

@app.route('/simple-login')
def simple_login():
    """Simplified login page"""
    return render_template('simple_auth.html')

@app.route('/simple-signup')
def simple_signup():
    """Simplified signup page"""
    return render_template('simple_signup.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if session.get('user_role') != 'admin':
        return redirect(url_for('simple_login'))
    
    # Get system statistics
    total_users = len(users_db)
    total_toilets = len(toilets)
    
    # Count users by role
    role_counts = {'public': 0, 'cleaner': 0, 'admin': 0}
    for user in users_db.values():
        role_counts[user['role']] += 1
    
    # Get toilet status summary
    status_counts = {'clean': 0, 'dirty': 0, 'moderate': 0}
    for toilet in toilets:
        if toilet['hygiene_score'] >= 70:
            status_counts['clean'] += 1
        elif toilet['hygiene_score'] <= 30:
            status_counts['dirty'] += 1
        else:
            status_counts['moderate'] += 1
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_toilets=total_toilets,
                         role_counts=role_counts,
                         status_counts=status_counts)

@app.route('/login')
def login():
    """Login page"""
    return redirect(url_for('auth'))

@app.route('/dashboard')
def dashboard():
    """Public user dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    if session.get('user_role') == 'cleaner':
        return redirect(url_for('staff_dashboard'))
    return render_template('public_dashboard_improved.html')

@app.route('/staff-dashboard')
def staff_dashboard():
    """Cleaning staff dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    if session.get('user_role') != 'cleaner':
        return redirect(url_for('dashboard'))
    return render_template('staff_dashboard_improved.html')

# Simple login/logout for testing
@app.route('/login-simple', methods=['POST'])
def login_simple():
    """Simple login for testing"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = users_db.get(email)
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_email'] = email
        session['user_role'] = user['role']
        session['user_name'] = user['name']
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'email': email,
                'role': user['role'],
                'name': user['name']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# API Routes for Authentication
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Enhanced API login endpoint with better error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Simple email validation - just check for basic format
        if len(email) < 3 or ' ' in email:
            return jsonify({'error': 'Please enter a valid username or email'}), 400
        
        user = users_db.get(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_email'] = email
        session['user_role'] = user['role']
        session['user_name'] = user['name']
        session.permanent = True  # Make session persistent
        
        # Determine redirect URL based on role
        if user['role'] == 'admin':
            redirect_url = '/admin'
        elif user['role'] == 'cleaner':
            redirect_url = '/staff-dashboard'
        else:
            redirect_url = '/enhanced'
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'email': email,
                'role': user['role'],
                'name': user.get('name', email.split('@')[0].title())
            },
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'An error occurred during login. Please try again.'}), 500

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Enhanced API registration endpoint with better validation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', 'public').lower()
        name = data.get('name', '').strip()
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Simple email validation - just check for basic format
        if len(email) < 3 or ' ' in email:
            return jsonify({'error': 'Please enter a valid username or email'}), 400
        
        # Password validation
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if email already exists
        if email in users_db:
            return jsonify({'error': 'This email is already registered'}), 400
        
        # Validate role
        valid_roles = ['public', 'cleaner', 'admin']
        if role not in valid_roles:
            role = 'public'
        
        # Generate name if not provided
        if not name:
            name = email.split('@')[0].title()
        
        # Create user
        users_db[email] = {
            'password': generate_password_hash(password),
            'role': role,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Auto-login after registration
        session['user_email'] = email
        session['user_role'] = role
        session.permanent = True
        
        # Determine redirect URL
        if role == 'admin':
            redirect_url = '/admin'
        elif role == 'cleaner':
            redirect_url = '/staff-dashboard'
        else:
            redirect_url = '/enhanced'
        
        return jsonify({
            'message': 'Registration successful! Welcome to CleanSeat.',
            'user': {
                'email': email,
                'role': role,
                'name': name
            },
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'An error occurred during registration. Please try again.'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Logout endpoint"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'})
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'An error occurred during logout'}), 500

@app.route('/api/auth/status')
def api_auth_status():
    """Get current authentication status"""
    if 'user_email' in session:
        user = users_db.get(session['user_email'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'email': session['user_email'],
                    'role': session['user_role'],
                    'name': user.get('name', session['user_email'].split('@')[0].title())
                }
            })
    
    return jsonify({'authenticated': False})

# API Routes for Toilet Data
@app.route('/api/toilets')
@api_login_required
def get_toilets():
    """Get all toilets with current status"""
    try:
        # Convert datetime objects to strings for JSON serialization
        toilets_list = []
        for toilet in toilets_data:
            toilet_copy = toilet.copy()
            
            # Handle datetime fields safely
            if isinstance(toilet['last_cleaned'], datetime):
                toilet_copy['last_cleaned'] = toilet['last_cleaned'].isoformat()
            else:
                toilet_copy['last_cleaned'] = str(toilet['last_cleaned'])
                
            if isinstance(toilet['next_scheduled'], datetime):
                toilet_copy['next_scheduled'] = toilet['next_scheduled'].isoformat()
            else:
                toilet_copy['next_scheduled'] = str(toilet['next_scheduled'])
                
            toilet_copy['last_updated'] = datetime.now().isoformat()
            
            # Add reviews timestamps
            if 'reviews' in toilet_copy:
                for review in toilet_copy['reviews']:
                    if 'timestamp' in review:
                        if isinstance(review['timestamp'], datetime):
                            review['timestamp'] = review['timestamp'].isoformat()
                        else:
                            review['timestamp'] = str(review['timestamp'])
            
            toilets_list.append(toilet_copy)
        
        return jsonify({
            'toilets': toilets_list,
            'total': len(toilets_list),
            'summary': {
                'clean': len([t for t in toilets_data if t['status'] == 'Clean']),
                'moderate': len([t for t in toilets_data if t['status'] == 'Moderate']),
                'dirty': len([t for t in toilets_data if t['status'] == 'Dirty'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toilets/<toilet_id>')
@api_login_required
def get_toilet_details(toilet_id):
    """Get detailed information about a specific toilet"""
    try:
        toilet = next((t for t in toilets_data if t['id'] == toilet_id), None)
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Convert datetime objects to strings
        toilet_copy = toilet.copy()
        toilet_copy['last_cleaned'] = toilet['last_cleaned'].isoformat()
        toilet_copy['next_scheduled'] = toilet['next_scheduled'].isoformat()
        toilet_copy['last_updated'] = datetime.now().isoformat()
        
        return jsonify(toilet_copy)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toilets/<toilet_id>/update-status', methods=['POST'])
@api_login_required
def update_toilet_status(toilet_id):
    """Update toilet status (for cleaning staff)"""
    try:
        user_role = session.get('user_role')
        
        # Only cleaners and admins can update status
        if user_role not in ['cleaner', 'admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        hygiene_score = data.get('hygiene_score')
        
        if not new_status or new_status not in ['Clean', 'Moderate', 'Dirty']:
            return jsonify({'error': 'Invalid status'}), 400
        
        toilet = next((t for t in toilets_data if t['id'] == toilet_id), None)
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Store previous status for notification
        previous_status = toilet['status']
        
        # Update toilet data
        toilet['status'] = new_status
        toilet['hygiene_score'] = hygiene_score or toilet['hygiene_score']
        toilet['last_cleaned'] = datetime.now()
        toilet['last_updated'] = datetime.now()
        toilet['cleaner_assigned'] = session.get('user_email')
        
        # Create update notification
        update = {
            'id': str(uuid.uuid4()),
            'toilet_id': toilet_id,
            'toilet_name': toilet['name'],
            'previous_status': previous_status,
            'new_status': new_status,
            'new_score': toilet['hygiene_score'],
            'cleaner_name': session.get('user_name'),
            'cleaner_email': session.get('user_email'),
            'timestamp': datetime.now(),
            'type': 'cleaned'
        }
        real_time_updates.append(update)
        
        return jsonify({
            'message': 'Toilet status updated successfully',
            'toilet': {
                'id': toilet_id,
                'name': toilet['name'],
                'status': new_status,
                'hygiene_score': toilet['hygiene_score'],
                'last_cleaned': toilet['last_cleaned'].isoformat(),
                'cleaner_name': session.get('user_name')
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/toilets/<toilet_id>/reviews', methods=['POST'])
@api_login_required
def add_review(toilet_id):
    """Add user review for a toilet"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        toilet = next((t for t in toilets_data if t['id'] == toilet_id), None)
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        review = {
            'user': session.get('user_email'),
            'rating': rating,
            'comment': comment or '',
            'timestamp': datetime.now()
        }
        
        toilet['reviews'].append(review)
        
        return jsonify({
            'message': 'Review added successfully',
            'review': {
                'user': session.get('user_email'),
                'rating': rating,
                'comment': comment,
                'timestamp': review['timestamp'].isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates')
@api_login_required
def get_real_time_updates():
    """Get real-time updates with immediate cleaning notifications"""
    try:
        # Return last 15 updates to show more history
        recent_updates = real_time_updates[-15:] if real_time_updates else []
        
        # Convert datetime objects to strings and ensure all required fields are present
        updates_list = []
        for update in recent_updates:
            update_copy = update.copy()
            
            # Handle timestamp
            if isinstance(update_copy['timestamp'], datetime):
                update_copy['timestamp'] = update_copy['timestamp'].isoformat()
            else:
                update_copy['timestamp'] = str(update_copy['timestamp'])
            
            # Ensure icon is present for UI display
            if 'icon' not in update_copy:
                update_copy['icon'] = '🚻'
            
            # Ensure type is present
            if 'type' not in update_copy:
                update_copy['type'] = 'update'
                
            updates_list.append(update_copy)
        
        return jsonify({
            'updates': updates_list,
            'total_updates': len(real_time_updates),
            'last_update': updates_list[-1]['timestamp'] if updates_list else None,
            'has_cleaning_updates': any(u.get('type') == 'cleaned' for u in updates_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/directions/<from_lat>/<from_lng>/<to_lat>/<to_lng>')
@api_login_required
def get_directions(from_lat, from_lng, to_lat, to_lng):
    """Get directions between two points (simplified version)"""
    try:
        # Convert to float
        from_lat, from_lng = float(from_lat), float(from_lng)
        to_lat, to_lng = float(to_lat), float(to_lng)
        
        # Generate a simple path (in real app, this would use a routing service)
        path = [
            [from_lat, from_lng],
            [(from_lat + to_lat) / 2, (from_lng + to_lng) / 2],
            [to_lat, to_lng]
        ]
        
        # Calculate distance (simplified)
        distance = ((to_lat - from_lat) ** 2 + (to_lng - from_lng) ** 2) ** 0.5 * 111000  # Approximate meters
        
        return jsonify({
            'path': path,
            'distance': round(distance, 0),
            'duration': round(distance / 80, 0),  # Approximate walking time in seconds
            'instructions': [
                'Start at current location',
                'Walk straight to destination',
                'You have arrived'
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile')
@api_login_required
def get_user_profile():
    """Get current user profile"""
    try:
        return jsonify({
            'email': session.get('user_email'),
            'name': session.get('user_name'),
            'role': session.get('user_role')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket simulation endpoint for real-time updates
@app.route('/api/toilets/stream')
@api_login_required
def stream_toilet_updates():
    """Stream real-time toilet updates (simulated)"""
    def generate():
        while True:
            # Get recent updates
            if real_time_updates:
                recent_update = real_time_updates[-1]
                data = {
                    'type': 'update',
                    'data': {
                        'toilet_id': recent_update['toilet_id'],
                        'toilet_name': recent_update['toilet_name'],
                        'previous_status': recent_update['previous_status'],
                        'new_status': recent_update['new_status'],
                        'new_score': recent_update['new_score'],
                        'timestamp': recent_update['timestamp'].isoformat()
                    }
                }
                yield f"data: {json.dumps(data)}\n\n"
            time.sleep(5)  # Send update every 5 seconds
    
    return Response(generate(), mimetype='text/plain')

# Staff-specific API endpoints
@app.route('/api/staff/priority-toilets')
@api_login_required
def get_priority_toilets():
    """Get toilets prioritized for cleaning staff"""
    try:
        user_role = session.get('user_role')
        
        # Only cleaners and admins can access
        if user_role not in ['cleaner', 'admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Calculate priority based on hygiene score and time since last cleaning
        priority_toilets = []
        for toilet in toilets_data:
            priority = calculate_priority(toilet)
            toilet_copy = toilet.copy()
            toilet_copy['priority'] = priority
            toilet_copy['last_cleaned'] = toilet['last_cleaned'].isoformat()
            toilet_copy['next_scheduled'] = toilet['next_scheduled'].isoformat()
            priority_toilets.append(toilet_copy)
        
        # Sort by priority (high to low)
        priority_toilets.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        return jsonify({
            'toilets': priority_toilets,
            'total': len(priority_toilets)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/tasks')
@api_login_required
def get_staff_tasks():
    """Get cleaning tasks for current staff member"""
    try:
        user_role = session.get('user_role')
        user_email = session.get('user_email')
        user_name = session.get('user_name')
        
        # Only cleaners can access their tasks
        if user_role != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Generate tasks based on toilet priorities
        tasks = []
        for toilet in toilets_data:
            if toilet['cleaner_assigned'] == user_email:
                priority = calculate_priority(toilet)
                
                task = {
                    'id': f"task_{toilet['id']}",
                    'toilet_id': toilet['id'],
                    'toilet_name': toilet['name'],
                    'toilet_address': toilet['address'],
                    'priority': priority,
                    'status': 'pending',  # pending, in_progress, completed
                    'scheduled_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                    'estimated_duration': '30 minutes'
                }
                
                # Update status based on current conditions
                if toilet['status'] == 'Dirty' and priority == 'high':
                    task['status'] = 'in_progress'
                elif toilet['status'] == 'Clean':
                    task['status'] = 'completed'
                
                tasks.append(task)
        
        # Sort by priority and status
        tasks.sort(key=lambda x: (
            {'in_progress': 0, 'pending': 1, 'completed': 2}[x['status']],
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']]
        ))
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks),
            'staff_name': user_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/stats')
@api_login_required
def get_staff_stats():
    """Get statistics for current staff member"""
    try:
        user_role = session.get('user_role')
        user_email = session.get('user_email')
        user_name = session.get('user_name')
        
        # Only cleaners can access their stats
        if user_role != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Calculate stats based on toilet data
        cleaned_today = 0
        tasks_completed = 0
        total_rating = 0
        rating_count = 0
        on_time_count = 0
        total_tasks = 0
        
        for toilet in toilets_data:
            if toilet['cleaner_assigned'] == user_email:
                total_tasks += 1
                
                # Count cleaned toilets (recently cleaned)
                if (datetime.now() - toilet['last_cleaned']).total_seconds() < 86400:  # 24 hours
                    cleaned_today += 1
                
                # Count completed tasks (clean toilets)
                if toilet['status'] == 'Clean':
                    tasks_completed += 1
                
                # Calculate average rating
                for review in toilet['reviews']:
                    total_rating += review['rating']
                    rating_count += 1
                
                # Check if cleaning was on time
                if toilet['status'] == 'Clean':
                    if toilet['last_cleaned'] <= toilet['next_scheduled']:
                        on_time_count += 1
        
        avg_rating = total_rating / rating_count if rating_count > 0 else 0
        on_time_percentage = (on_time_count / total_tasks * 100) if total_tasks > 0 else 0
        
        return jsonify({
            'stats': {
                'cleaned_today': cleaned_today,
                'tasks_completed': tasks_completed,
                'avg_rating': round(avg_rating, 1),
                'on_time_percentage': round(on_time_percentage, 1),
                'total_tasks': total_tasks
            },
            'staff_name': user_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/start-cleaning', methods=['POST'])
@api_login_required
def start_cleaning():
    """Start cleaning a toilet"""
    try:
        user_role = session.get('user_role')
        user_email = session.get('user_email')
        user_name = session.get('user_name')
        
        # Only cleaners can start cleaning
        if user_role != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        toilet_id = data.get('toilet_id')
        
        if not toilet_id:
            return jsonify({'error': 'Toilet ID required'}), 400
        
        toilet = next((t for t in toilets_data if t['id'] == toilet_id), None)
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Check if this toilet is assigned to the current cleaner
        if toilet['cleaner_assigned'] != user_email:
            return jsonify({'error': 'Toilet not assigned to you'}), 403
        
        # Simulate cleaning process
        toilet['status'] = 'In Progress'
        toilet['hygiene_score'] = 50  # Moderate score while cleaning
        toilet['last_updated'] = datetime.now()
        
        # Create update notification
        update = {
            'id': str(uuid.uuid4()),
            'toilet_id': toilet_id,
            'toilet_name': toilet['name'],
            'previous_status': toilet['status'],
            'new_status': 'In Progress',
            'new_score': 50,
            'cleaner_name': user_name,
            'cleaner_email': user_email,
            'timestamp': datetime.now(),
            'type': 'cleaning_started'
        }
        real_time_updates.append(update)
        
        # Simulate completion after 30 seconds
        def complete_cleaning():
            time.sleep(30)
            toilet['status'] = 'Clean'
            toilet['hygiene_score'] = random.randint(80, 95)
            toilet['last_cleaned'] = datetime.now()
            toilet['last_updated'] = datetime.now()
            
            # Create completion update with immediate notification
            completion_update = {
                'id': str(uuid.uuid4()),
                'toilet_id': toilet_id,
                'toilet_name': toilet['name'],
                'previous_status': 'In Progress',
                'new_status': 'Clean',
                'new_score': toilet['hygiene_score'],
                'cleaner_name': user_name,
                'cleaner_email': user_email,
                'timestamp': datetime.now(),
                'type': 'cleaned',
                'icon': toilet.get('icon', '🚻')
            }
            real_time_updates.append(completion_update)
            
            # Ensure the update is immediately available for real-time updates
            print(f"🧽 Toilet cleaned: {toilet['name']} - Score: {toilet['hygiene_score']}/100")
        
        # Start completion in background
        completion_thread = threading.Thread(target=complete_cleaning)
        completion_thread.daemon = True  # Make it a daemon thread
        completion_thread.start()
        
        # Start completion in background
        completion_thread = threading.Thread(target=complete_cleaning)
        completion_thread.start()
        
        return jsonify({
            'message': 'Cleaning started successfully',
            'toilet': {
                'id': toilet_id,
                'name': toilet['name'],
                'status': 'In Progress',
                'estimated_completion': '30 seconds'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/updates')
@api_login_required
def get_staff_updates():
    """Get updates for staff dashboard"""
    try:
        user_role = session.get('user_role')
        user_email = session.get('user_email')
        
        # Only cleaners can access staff updates
        if user_role != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Check for new urgent toilets (high priority)
        new_urgent_toilets = []
        for toilet in toilets_data:
            priority = calculate_priority(toilet)
            if priority == 'high' and toilet['cleaner_assigned'] == user_email:
                # Check if this toilet became urgent recently (last 5 minutes)
                if (datetime.now() - toilet.get('last_updated', datetime.now())).total_seconds() < 300:
                    new_urgent_toilets.append({
                        'id': toilet['id'],
                        'name': toilet['name'],
                        'priority': priority,
                        'status': toilet['status'],
                        'hygiene_score': toilet['hygiene_score']
                    })
        
        # Check if there are any updates since last check
        has_updates = len(new_urgent_toilets) > 0 or len(real_time_updates) > 0
        
        return jsonify({
            'has_updates': has_updates,
            'new_urgent_toilets': new_urgent_toilets,
            'total_updates': len(real_time_updates)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Routes for Directions
@app.route('/api/directions/<from_toilet_id>/to/<to_toilet_id>')
@api_login_required
def get_toilet_directions(from_toilet_id, to_toilet_id):
    """Get directions between two toilets"""
    try:
        from_toilet = next((t for t in toilets_data if t['id'] == from_toilet_id), None)
        to_toilet = next((t for t in toilets_data if t['id'] == to_toilet_id), None)
        
        if not from_toilet or not to_toilet:
            return jsonify({'error': 'One or both toilets not found'}), 404
        
        # Calculate simple distance and path
        from_lat, from_lng = from_toilet['lat'], from_toilet['lng']
        to_lat, to_lng = to_toilet['lat'], to_toilet['lng']
        
        # Calculate distance using simple Euclidean distance (approximation)
        distance = ((to_lat - from_lat) ** 2 + (to_lng - from_lng) ** 2) ** 0.5 * 111000  # Convert to meters (approx)
        
        # Calculate duration (assuming walking speed of 1.4 m/s)
        duration = distance / 84  # Convert to minutes (1.4 m/s * 60 s/min)
        
        # Use pre-defined path points if available, otherwise create simple path
        if 'path_points' in from_toilet and len(from_toilet['path_points']) > 1:
            path = from_toilet['path_points']
        else:
            # Create simple path with intermediate points
            path = [
                [from_lat, from_lng],
                [(from_lat + to_lat) / 2, (from_lng + to_lng) / 2],
                [to_lat, to_lng]
            ]
        
        return jsonify({
            'found': True,
            'from': {
                'id': from_toilet['id'],
                'name': from_toilet['name'],
                'lat': from_lat,
                'lng': from_lng
            },
            'to': {
                'id': to_toilet['id'],
                'name': to_toilet['name'],
                'lat': to_lat,
                'lng': to_lng
            },
            'distance': round(distance, 0),
            'duration': round(duration, 1),
            'path': path,
            'instructions': [
                f"Head to {to_toilet['name']}",
                f"Distance: {round(distance, 0)}m",
                f"Estimated time: {round(duration, 1)} minutes"
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to calculate toilet priority
def calculate_priority(toilet):
    """Calculate priority based on hygiene score and time since last cleaning"""
    hygiene_score = toilet['hygiene_score']
    time_since_cleaned = (datetime.now() - toilet['last_cleaned']).total_seconds() / 3600  # hours
    
    if hygiene_score < 30 or time_since_cleaned > 8:
        return 'high'
    elif hygiene_score < 60 or time_since_cleaned > 4:
        return 'medium'
    else:
        return 'low'

# Error handlers
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized access'}), 401

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({'error': 'Access forbidden'}), 403

if __name__ == '__main__':
    print("🚀 Starting Enhanced Smart Toilet Hygiene System")
    print("🔐 Auth/Login: http://localhost:5000/auth")
    print("📍 Public Dashboard: http://localhost:5000/dashboard")
    print("🧽 Staff Dashboard: http://localhost:5000/staff-dashboard")
    print("👨‍💼 Admin Dashboard: http://localhost:5000/admin-dashboard")
    print("🔐 API Login: POST /api/auth/login")
    print("📍 Get Toilets: GET /api/toilets")
    print("🔄 Real-time Updates: GET /api/updates")
    
    app.run(debug=True, host='0.0.0.0', port=5000)