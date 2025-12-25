#!/usr/bin/env python3
"""
Staff Interface Flask Application  
Port: 5002 - Staff Dashboard for cleaners and supervisors
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import random
import uuid
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
app.secret_key = 'staff-interface-secret-key'
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load data
with open('toilets_data.json', 'r') as f:
    toilets_data = json.load(f)

with open('staff_data.json', 'r') as f:
    staff_data = json.load(f)

# Real-time updates storage for staff interface
staff_updates = []

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Redirect to login"""
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Staff login interface"""
    return render_template('staff_login_enhanced.html')

@app.route('/staff-dashboard')
@login_required
def staff_dashboard():
    """Staff dashboard interface"""
    return render_template('staff_dashboard_improved.html')

# Authentication APIs
@app.route('/api/auth/login', methods=['POST'])
def login_api():
    """Staff login API"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Find user
        user = None
        for staff in staff_data:
            if staff['email'] == email:
                user = staff
                break
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password (for demo, we'll accept any password)
        # In production, use: check_password_hash(user['password'], password)
        if password != user['password']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_email'] = email
        session['user_name'] = user['name']
        session['user_role'] = user['role']
        session['user_id'] = user['id']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'id': user['id']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout_api():
    """Staff logout API"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/auth/check-session')
def check_session():
    """Check if user has an active session"""
    if 'user_email' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'name': session['user_name'],
                'email': session['user_email'],
                'role': session['user_role'],
                'id': session['user_id']
            }
        })
    return jsonify({'authenticated': False})

# Staff APIs
@app.route('/api/staff/priority-toilets')
@login_required
def get_staff_priority_toilets():
    """Get priority toilets for current staff member"""
    try:
        user_email = session['user_email']
        priority_toilets = []
        
        for toilet in toilets_data:
            # Only show toilets assigned to current staff
            if toilet['cleaner_assigned'] == user_email:
                # Calculate urgency score
                urgency_score = calculate_urgency_score(toilet)
                
                toilet_info = {
                    'id': toilet['id'],
                    'name': toilet['name'],
                    'address': toilet['address'],
                    'lat': toilet['lat'],
                    'lng': toilet['lng'],
                    'status': toilet['status'],
                    'hygiene_score': toilet['hygiene_score'],
                    'last_cleaned': toilet['last_cleaned'].isoformat(),
                    'urgency_score': urgency_score,
                    'priority': get_priority_level(urgency_score),
                    'icon': toilet.get('icon', '🚻'),
                    'cleaner_assigned': toilet['cleaner_assigned']
                }
                
                # Only include toilets that need attention
                if urgency_score > 0:
                    priority_toilets.append(toilet_info)
        
        # Sort by urgency score (highest first)
        priority_toilets.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return jsonify({
            'toilets': priority_toilets,
            'total': len(priority_toilets),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/tasks')
@login_required
def get_staff_tasks():
    """Get tasks for current staff member"""
    try:
        user_email = session['user_email']
        tasks = []
        
        for toilet in toilets_data:
            if toilet['cleaner_assigned'] == user_email:
                # Create task for each assigned toilet
                task = {
                    'id': f"task_{toilet['id']}",
                    'toilet_id': toilet['id'],
                    'toilet_name': toilet['name'],
                    'toilet_address': toilet['address'],
                    'status': 'pending' if toilet['status'] in ['Dirty', 'Needs Cleaning'] else 'completed',
                    'priority': get_priority_level(calculate_urgency_score(toilet)),
                    'assigned_date': datetime.now().isoformat(),
                    'estimated_time': random.randint(15, 45),
                    'icon': toilet.get('icon', '🚻')
                }
                tasks.append(task)
        
        return jsonify({
            'tasks': tasks,
            'total': len(tasks),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/start-cleaning', methods=['POST'])
@login_required
def start_cleaning():
    """Start cleaning a toilet"""
    try:
        data = request.get_json()
        toilet_id = data.get('toilet_id')
        user_email = session['user_email']
        
        # Find toilet
        toilet = None
        for t in toilets_data:
            if t['id'] == toilet_id:
                toilet = t
                break
        
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Check if assigned to current user
        if toilet['cleaner_assigned'] != user_email:
            return jsonify({'error': 'Toilet not assigned to you'}), 403
        
        # Update toilet status
        previous_status = toilet['status']
        toilet['status'] = 'Cleaning in Progress'
        
        # Create update record
        update = {
            'id': str(uuid.uuid4()),
            'toilet_id': toilet_id,
            'toilet_name': toilet['name'],
            'type': 'cleaning_started',
            'previous_status': previous_status,
            'new_status': 'Cleaning in Progress',
            'new_score': toilet['hygiene_score'],
            'cleaner_name': session['user_name'],
            'timestamp': datetime.now(),
            'icon': toilet.get('icon', '🚻')
        }
        
        staff_updates.append(update)
        
        # Send update to public interface
        send_update_to_public(update)
        
        print(f"🧹 Started cleaning: {toilet['name']} by {session['user_name']}")
        
        return jsonify({
            'message': 'Cleaning started successfully',
            'toilet_id': toilet_id,
            'status': 'Cleaning in Progress'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/complete-cleaning', methods=['POST'])
@login_required
def complete_cleaning():
    """Complete cleaning a toilet"""
    try:
        data = request.get_json()
        toilet_id = data.get('toilet_id')
        user_email = session['user_email']
        
        # Find toilet
        toilet = None
        for t in toilets_data:
            if t['id'] == toilet_id:
                toilet = t
                break
        
        if not toilet:
            return jsonify({'error': 'Toilet not found'}), 404
        
        # Check if assigned to current user
        if toilet['cleaner_assigned'] != user_email:
            return jsonify({'error': 'Toilet not assigned to you'}), 403
        
        # Update toilet status and score
        previous_status = toilet['status']
        toilet['status'] = 'Clean'
        toilet['hygiene_score'] = random.randint(85, 100)
        toilet['last_cleaned'] = datetime.now()
        
        # Create update record
        update = {
            'id': str(uuid.uuid4()),
            'toilet_id': toilet_id,
            'toilet_name': toilet['name'],
            'type': 'cleaning_completed',
            'previous_status': previous_status,
            'new_status': 'Clean',
            'new_score': toilet['hygiene_score'],
            'cleaner_name': session['user_name'],
            'timestamp': datetime.now(),
            'icon': toilet.get('icon', '🚻')
        }
        
        staff_updates.append(update)
        
        # Send update to public interface
        send_update_to_public(update)
        
        print(f"✅ Completed cleaning: {toilet['name']} by {session['user_name']}")
        
        return jsonify({
            'message': 'Cleaning completed successfully',
            'toilet_id': toilet_id,
            'status': 'Clean',
            'new_score': toilet['hygiene_score']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/updates')
@login_required
def get_staff_updates():
    """Get real-time updates for staff dashboard"""
    try:
        user_email = session['user_email']
        
        # Get recent updates (last 30 minutes)
        recent_updates = []
        current_time = datetime.now()
        
        for update in staff_updates[-20:]:  # Last 20 updates
            if isinstance(update['timestamp'], datetime):
                time_diff = (current_time - update['timestamp']).total_seconds() / 60  # minutes
                if time_diff <= 30:  # Only include updates from last 30 minutes
                    recent_updates.append({
                        'id': update['id'],
                        'toilet_id': update['toilet_id'],
                        'toilet_name': update['toilet_name'],
                        'type': update['type'],
                        'previous_status': update['previous_status'],
                        'new_status': update['new_status'],
                        'new_score': update['new_score'],
                        'cleaner_name': update['cleaner_name'],
                        'timestamp': update['timestamp'].isoformat(),
                        'icon': update['icon'],
                        'time_ago': f"{int(time_diff)} minutes ago" if time_diff < 60 else f"{int(time_diff/60)} hours ago"
                    })
        
        return jsonify({
            'has_updates': len(recent_updates) > 0,
            'updates': recent_updates,
            'total_updates': len(staff_updates),
            'last_checked': current_time.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/staff/stats')
@login_required
def get_staff_stats():
    """Get staff performance statistics"""
    try:
        user_email = session['user_email']
        
        # Calculate stats for current user
        total_cleaned = len([u for u in staff_updates 
                           if u['cleaner_name'] == session['user_name'] and 
                           u['type'] == 'cleaning_completed'])
        
        total_assigned = len([t for t in toilets_data if t['cleaner_assigned'] == user_email])
        
        # Calculate average score for cleaned toilets
        cleaned_scores = [u['new_score'] for u in staff_updates 
                         if u['cleaner_name'] == session['user_name'] and 
                         u['type'] == 'cleaning_completed']
        
        avg_score = sum(cleaned_scores) / len(cleaned_scores) if cleaned_scores else 0
        
        return jsonify({
            'total_cleaned': total_cleaned,
            'total_assigned': total_assigned,
            'average_score': round(avg_score, 1),
            'efficiency': round((total_cleaned / max(total_assigned, 1)) * 100, 1),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Sync endpoint for public interface
@app.route('/api/sync/public')
def sync_with_public():
    """Sync data with public interface"""
    try:
        # Get recent updates for public interface
        recent_updates = []
        current_time = datetime.now()
        
        for update in staff_updates[-10:]:  # Last 10 updates
            if isinstance(update['timestamp'], datetime):
                time_diff = (current_time - update['timestamp']).total_seconds() / 60
                if time_diff <= 60:  # Include updates from last hour
                    recent_updates.append({
                        'toilet_id': update['toilet_id'],
                        'toilet_name': update['toilet_name'],
                        'type': update['type'],
                        'previous_status': update['previous_status'],
                        'new_status': update['new_status'],
                        'new_score': update['new_score'],
                        'cleaner_name': update['cleaner_name'],
                        'timestamp': update['timestamp'].isoformat(),
                        'icon': update['icon']
                    })
        
        return jsonify({
            'has_updates': len(recent_updates) > 0,
            'updates': recent_updates,
            'last_updated': current_time.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions
def calculate_urgency_score(toilet):
    """Calculate urgency score for a toilet"""
    score = 0
    
    # Status-based scoring
    if toilet['status'] == 'Dirty':
        score += 50
    elif toilet['status'] == 'Needs Cleaning':
        score += 30
    elif toilet['status'] == 'Moderate':
        score += 10
    
    # Hygiene score-based scoring
    if toilet['hygiene_score'] < 50:
        score += 30
    elif toilet['hygiene_score'] < 70:
        score += 20
    
    # Time-based scoring
    time_since_cleaned = (datetime.now() - toilet['last_cleaned']).total_seconds() / 3600  # hours
    if time_since_cleaned > 8:
        score += 20
    elif time_since_cleaned > 4:
        score += 10
    
    return min(score, 100)  # Cap at 100

def get_priority_level(urgency_score):
    """Get priority level based on urgency score"""
    if urgency_score >= 70:
        return 'high'
    elif urgency_score >= 40:
        return 'medium'
    else:
        return 'low'

def send_update_to_public(update_data):
    """Send real-time update to public interface"""
    try:
        # Prepare update data for public interface
        update_payload = {
            'toilet_id': update_data['toilet_id'],
            'toilet_name': update_data['toilet_name'],
            'type': update_data['type'],
            'previous_status': update_data['previous_status'],
            'new_status': update_data['new_status'],
            'new_score': update_data['new_score'],
            'cleaner_name': update_data['cleaner_name'],
            'timestamp': update_data['timestamp'].isoformat(),
            'icon': update_data['icon']
        }
        
        # Send to public interface webhook
        response = requests.post(
            'http://localhost:5001/api/webhook/update',
            json=update_payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"📡 Successfully sent update to public interface: {update_data['toilet_name']}")
        else:
            print(f"⚠️  Failed to send update to public interface: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending update to public interface: {e}")

if __name__ == '__main__':
    print("🧹 Starting Staff Interface Application")
    print("🔐 Staff Login: http://localhost:5002/login")
    print("📊 Staff Dashboard: http://localhost:5002/staff-dashboard")
    print("🔄 Real-time Updates: GET /api/staff/updates")
    print("📡 Sync with Public: GET /api/sync/public")
    
    app.run(debug=True, host='0.0.0.0', port=5002)