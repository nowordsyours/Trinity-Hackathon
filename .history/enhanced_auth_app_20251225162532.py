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
    'user1': {
        'password': generate_password_hash('password123'),
        'role': 'public',
        'name': 'Public User'
    },
    'cleaner1': {
        'password': generate_password_hash('password123'),
        'role': 'cleaner',
        'name': 'Cleaning Staff'
    },
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'System Admin'
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
        'cleaner_assigned': 'cleaner1',
        'occupancy': 'low',
        'water_available': True,
        'soap_available': True,
        'paper_available': True,
        'reviews': [
            {'user': 'user1', 'rating': 4, 'comment': 'Very clean', 'timestamp': datetime.now() - timedelta(days=1)}
        ]
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
        'cleaner_assigned': 'cleaner1',
        'occupancy': 'high',
        'water_available': True,
        'soap_available': False,
        'paper_available': True,
        'reviews': []
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
            {'user': 'user2', 'rating': 1, 'comment': 'Very dirty, no water', 'timestamp': datetime.now() - timedelta(hours=2)}
        ]
    }
]

# Real-time updates storage
real_time_updates = []

# Background thread for simulating real-time changes
def simulate_real_time_updates():
    """Simulate real-time changes in toilet conditions"""
    while True:
        time.sleep(10)  # Update every 10 seconds
        
        # Randomly update a toilet condition
        toilet = random.choice(toilets_data)
        
        # Simulate gradual degradation or improvement
        if toilet['status'] == 'Clean':
            if random.random() < 0.1:  # 10% chance to become moderate
                toilet['hygiene_score'] = max(40, toilet['hygiene_score'] - random.randint(5, 15))
                toilet['status'] = 'Moderate'
                toilet['last_updated'] = datetime.now()
                
                # Create update notification
                update = {
                    'id': str(uuid.uuid4()),
                    'toilet_id': toilet['id'],
                    'toilet_name': toilet['name'],
                    'previous_status': 'Clean',
                    'new_status': 'Moderate',
                    'new_score': toilet['hygiene_score'],
                    'timestamp': datetime.now(),
                    'type': 'status_change'
                }
                real_time_updates.append(update)
                
        elif toilet['status'] == 'Moderate':
            if random.random() < 0.15:  # 15% chance to change
                if random.random() < 0.5:  # 50% chance to become clean (cleaned)
                    toilet['hygiene_score'] = min(95, toilet['hygiene_score'] + random.randint(20, 40))
                    toilet['status'] = 'Clean'
                    toilet['last_cleaned'] = datetime.now()
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Moderate',
                        'new_status': 'Clean',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'cleaned'
                    }
                    real_time_updates.append(update)
                else:  # 50% chance to become dirty
                    toilet['hygiene_score'] = max(15, toilet['hygiene_score'] - random.randint(10, 25))
                    toilet['status'] = 'Dirty'
                    
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': toilet['id'],
                        'toilet_name': toilet['name'],
                        'previous_status': 'Moderate',
                        'new_status': 'Dirty',
                        'new_score': toilet['hygiene_score'],
                        'timestamp': datetime.now(),
                        'type': 'status_change'
                    }
                    real_time_updates.append(update)

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
    """Main landing page - redirect to auth"""
    return redirect(url_for('auth'))

@app.route('/test')
def test():
    """Test route"""
    return "Test route working!"

@app.route('/auth')
def auth():
    """Auth page"""
    return render_template('auth.html')

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
    """Session-based login endpoint"""
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

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """Registration endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'public')  # Default to public user
        
        if not email or not password or not name:
            return jsonify({'error': 'All fields required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'User already exists'}), 409
        
        users_db[email] = {
            'password': generate_password_hash(password),
            'role': role,
            'name': name
        }
        
        return jsonify({'message': 'User registered successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            toilet_copy['last_cleaned'] = toilet['last_cleaned'].isoformat()
            toilet_copy['next_scheduled'] = toilet['next_scheduled'].isoformat()
            toilet_copy['last_updated'] = datetime.now().isoformat()
            
            # Add reviews timestamps
            if 'reviews' in toilet_copy:
                for review in toilet_copy['reviews']:
                    if 'timestamp' in review:
                        review['timestamp'] = review['timestamp'].isoformat()
            
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
    """Get real-time updates"""
    try:
        # Return last 10 updates
        recent_updates = real_time_updates[-10:] if real_time_updates else []
        
        # Convert datetime objects to strings
        updates_list = []
        for update in recent_updates:
            update_copy = update.copy()
            update_copy['timestamp'] = update['timestamp'].isoformat()
            updates_list.append(update_copy)
        
        return jsonify({
            'updates': updates_list,
            'total_updates': len(real_time_updates)
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
@jwt_required()
def get_staff_stats():
    """Get statistics for current staff member"""
    try:
        current_user = get_jwt_identity()
        
        # Only cleaners can access their stats
        if current_user['role'] != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Calculate stats based on toilet data
        cleaned_today = 0
        tasks_completed = 0
        total_rating = 0
        rating_count = 0
        on_time_count = 0
        total_tasks = 0
        
        for toilet in toilets_data:
            if toilet['cleaner_assigned'] == current_user['email']:
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
            'staff_name': current_user['name']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/start-cleaning', methods=['POST'])
@jwt_required()
def start_cleaning():
    """Start cleaning a toilet"""
    try:
        current_user = get_jwt_identity()
        
        # Only cleaners can start cleaning
        if current_user['role'] != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        toilet_id = data.get('toilet_id')
        
        if not toilet_id:
            return jsonify({'error': 'Toilet ID required'}), 400
        
        toilet = next((t for t in toilets_data if t['id'] == toilet_id), None)
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Check if this toilet is assigned to the current cleaner
        if toilet['cleaner_assigned'] != current_user['email']:
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
            'cleaner_name': current_user['name'],
            'cleaner_email': current_user['email'],
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
            
            # Create completion update
            completion_update = {
                'id': str(uuid.uuid4()),
                'toilet_id': toilet_id,
                'toilet_name': toilet['name'],
                'previous_status': 'In Progress',
                'new_status': 'Clean',
                'new_score': toilet['hygiene_score'],
                'cleaner_name': current_user['name'],
                'cleaner_email': current_user['email'],
                'timestamp': datetime.now(),
                'type': 'cleaned'
            }
            real_time_updates.append(completion_update)
        
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
@jwt_required()
def get_staff_updates():
    """Get updates for staff dashboard"""
    try:
        current_user = get_jwt_identity()
        
        # Only cleaners can access staff updates
        if current_user['role'] != 'cleaner':
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Check for new urgent toilets (high priority)
        new_urgent_toilets = []
        for toilet in toilets_data:
            priority = calculate_priority(toilet)
            if priority == 'high' and toilet['cleaner_assigned'] == current_user['email']:
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
@jwt_manager.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt_manager.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt_manager.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token required'}), 401

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