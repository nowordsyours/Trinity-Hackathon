#!/usr/bin/env python3
"""
Public Interface Flask Application
Port: 5001 - Public Dashboard for general users
"""

from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import json
import random
from datetime import datetime, timedelta
import uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = 'public-interface-secret-key'
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load toilet data
with open('toilets_data.json', 'r') as f:
    toilets_data = json.load(f)

# Real-time updates storage
real_time_updates = []

# API authentication decorator
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        # For public interface, we'll accept basic token
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Redirect to public dashboard"""
    return render_template('public_dashboard_enhanced.html')

@app.route('/dashboard')
def public_dashboard():
    """Public dashboard interface"""
    return render_template('public_dashboard_enhanced.html')

# API Routes
@app.route('/api/toilets')
@api_login_required
def get_toilets():
    """Get all toilets with current status"""
    try:
        toilets = []
        for toilet in toilets_data:
            toilet_info = {
                'id': toilet['id'],
                'name': toilet['name'],
                'address': toilet['address'],
                'lat': toilet['lat'],
                'lng': toilet['lng'],
                'status': toilet['status'],
                'hygiene_score': toilet['hygiene_score'],
                'last_cleaned': toilet['last_cleaned'].isoformat(),
                'icon': toilet.get('icon', '🚻'),
                'reviews': toilet['reviews'][-3:]  # Last 3 reviews
            }
            toilets.append(toilet_info)
        
        return jsonify({
            'toilets': toilets,
            'total': len(toilets),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/updates')
@api_login_required
def get_updates():
    """Get real-time updates"""
    try:
        # Get recent updates (last 30 minutes)
        recent_updates = []
        current_time = datetime.now()
        
        for update in real_time_updates[-20:]:  # Last 20 updates
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
                        'cleaner_name': update.get('cleaner_name', 'Unknown'),
                        'timestamp': update['timestamp'].isoformat(),
                        'icon': update.get('icon', '🚻'),
                        'time_ago': f"{int(time_diff)} minutes ago" if time_diff < 60 else f"{int(time_diff/60)} hours ago"
                    })
        
        return jsonify({
            'has_updates': len(recent_updates) > 0,
            'updates': recent_updates,
            'total_updates': len(real_time_updates),
            'last_checked': current_time.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Webhook endpoint for receiving updates from staff interface
@app.route('/api/webhook/update', methods=['POST'])
def receive_update():
    """Receive real-time updates from staff interface"""
    try:
        data = request.get_json()
        
        # Validate the update data
        required_fields = ['toilet_id', 'toilet_name', 'type', 'previous_status', 'new_status', 'timestamp']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Add to real-time updates
        update = {
            'id': str(uuid.uuid4()),
            'toilet_id': data['toilet_id'],
            'toilet_name': data['toilet_name'],
            'type': data['type'],
            'previous_status': data['previous_status'],
            'new_status': data['new_status'],
            'new_score': data.get('new_score', 0),
            'cleaner_name': data.get('cleaner_name', 'Unknown'),
            'timestamp': datetime.fromisoformat(data['timestamp']) if isinstance(data['timestamp'], str) else datetime.now(),
            'icon': data.get('icon', '🚻')
        }
        
        real_time_updates.append(update)
        
        print(f"📡 Public Interface received update: {data['toilet_name']} - {data['type']}")
        
        return jsonify({
            'message': 'Update received successfully',
            'update_id': update['id']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper function to sync with staff interface
def sync_with_staff_interface():
    """Sync data with staff interface"""
    try:
        import requests
        
        # Request staff interface for updates
        response = requests.get('http://localhost:5002/api/sync/public', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('has_updates'):
                for update_data in data['updates']:
                    # Process each update
                    update = {
                        'id': str(uuid.uuid4()),
                        'toilet_id': update_data['toilet_id'],
                        'toilet_name': update_data['toilet_name'],
                        'type': update_data['type'],
                        'previous_status': update_data['previous_status'],
                        'new_status': update_data['new_status'],
                        'new_score': update_data.get('new_score', 0),
                        'cleaner_name': update_data.get('cleaner_name', 'Unknown'),
                        'timestamp': datetime.fromisoformat(update_data['timestamp']) if isinstance(update_data['timestamp'], str) else datetime.now(),
                        'icon': update_data.get('icon', '🚻')
                    }
                    real_time_updates.append(update)
                
                print(f"🔄 Synced {len(data['updates'])} updates from staff interface")
    except Exception as e:
        print(f"❌ Failed to sync with staff interface: {e}")

if __name__ == '__main__':
    print("🚀 Starting Public Interface Application")
    print("📍 Public Dashboard: http://localhost:5001/dashboard")
    print("🔄 Real-time Updates: GET /api/updates")
    print("📡 Webhook Endpoint: POST /api/webhook/update")
    print("🔌 Sync with Staff: GET /api/sync/public")
    
    app.run(debug=True, host='0.0.0.0', port=5001)