"""
Enhanced Smart Toilet Hygiene Prediction System with Real-time Data
This version includes advanced IoT simulation and real-time monitoring capabilities
"""

from flask import Flask, render_template, jsonify, request, Response
import json
import random
import numpy as np
from datetime import datetime, timedelta
import threading
import time
import csv
import io
from hygiene_prediction_system import HygienePredictionSystem
from real_time_data import RealTimeSensorSimulator

app = Flask(__name__)

# Initialize the prediction system and real-time simulator
system = HygienePredictionSystem()
simulator = RealTimeSensorSimulator()

# Global variables for real-time data
real_time_data = []
latest_reading = None
current_alerts = []
prediction_history = []
sensor_data_log = []
system_stats = {
    'total_predictions': 0,
    'clean_predictions': 0,
    'moderate_predictions': 0,
    'dirty_predictions': 0,
    'alerts_generated': 0,
    'start_time': datetime.now()
}

# Background thread for continuous data generation
def background_data_generator():
    global latest_reading, current_alerts, prediction_history, sensor_data_log
    
    while True:
        try:
            # Generate new reading
            latest_reading = simulator.get_current_readings()
            
            # Generate alerts
            current_alerts = simulator.generate_alert(latest_reading)
            
            # Make prediction
            prediction = system.predict_hygiene(latest_reading['sensors'])
            
            # Ensure prediction has required fields
            if 'error' not in prediction:
                prediction['timestamp'] = latest_reading['timestamp']
                prediction['hour'] = latest_reading['hour']
            else:
                # Handle prediction error
                prediction = {
                    'hygiene_score': 50.0,
                    'hygiene_status': 'Moderate',
                    'confidence': 0.5,
                    'explanation': 'Prediction system error - using default values',
                    'timestamp': latest_reading['timestamp'],
                    'hour': latest_reading['hour']
                }
            
            # Update system statistics
            system_stats['total_predictions'] += 1
            if 'hygiene_status' in prediction:
                if prediction['hygiene_status'] == 'Clean':
                    system_stats['clean_predictions'] += 1
                elif prediction['hygiene_status'] == 'Moderate':
                    system_stats['moderate_predictions'] += 1
                elif prediction['hygiene_status'] == 'Dirty':
                    system_stats['dirty_predictions'] += 1
            
            system_stats['alerts_generated'] = len(current_alerts)
            
            # Add to history
            prediction_history.append(prediction)
            if len(prediction_history) > 200:  # Keep last 200 predictions
                prediction_history.pop(0)
            
            # Add to real-time data
            real_time_data.append(latest_reading)
            if len(real_time_data) > 100:  # Keep last 100 readings
                real_time_data.pop(0)
            
            # Log sensor data for CSV export
            sensor_log_entry = {
                'timestamp': latest_reading['timestamp'],
                'hygiene_score': prediction['hygiene_score'],
                'hygiene_status': prediction['hygiene_status'],
                **latest_reading['sensors']
            }
            sensor_data_log.append(sensor_log_entry)
            if len(sensor_data_log) > 500:  # Keep last 500 entries
                sensor_data_log.pop(0)
            
            time.sleep(2)  # Update every 2 seconds for faster response
            
        except Exception as e:
            print(f"Background data generation error: {e}")
            time.sleep(3)

# Start background thread
print("🔄 Starting background data generation thread...")
bg_thread = threading.Thread(target=background_data_generator, daemon=True)
bg_thread.start()

@app.route('/')
def index():
    """Main real-time dashboard"""
    return render_template('real_time_dashboard.html')

@app.route('/iot-simulator')
def iot_simulator():
    """Interactive IoT sensor simulator"""
    return render_template('iot_simulator.html')

@app.route('/analytics')
def analytics():
    """Advanced analytics dashboard"""
    return render_template('analytics.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Make hygiene prediction from sensor data"""
    try:
        data = request.get_json()
        result = system.predict_hygiene(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/demo/<scenario>')
def demo(scenario):
    """Demo scenarios with realistic Indian public washroom conditions"""
    scenarios = {
        'clean': {
            'ammonia': 35, 'methane': 30, 'humidity': 65, 'temperature': 28,
            'footfall': 10, 'water_flow': 15, 'ph': 7.5, 'turbidity': 80
        },
        'moderate': {
            'ammonia': 55, 'methane': 45, 'humidity': 78, 'temperature': 32,
            'footfall': 25, 'water_flow': 8, 'ph': 8.2, 'turbidity': 150
        },
        'dirty': {
            'ammonia': 85, 'methane': 70, 'humidity': 88, 'temperature': 36,
            'footfall': 45, 'water_flow': 2, 'ph': 9.1, 'turbidity': 280
        },
        'emergency': {
            'ammonia': 95, 'methane': 90, 'humidity': 85, 'temperature': 32,
            'footfall': 45, 'water_flow': 1, 'ph': 9.0, 'turbidity': 450
        },
        # Realistic Indian public toilet scenarios
        'morning_rush': {
            'ammonia': 75, 'methane': 55, 'humidity': 82, 'temperature': 31,
            'footfall': 42, 'water_flow': 6, 'ph': 8.8, 'turbidity': 200
        },
        'poor_maintenance': {
            'ammonia': 90, 'methane': 75, 'humidity': 85, 'temperature': 34,
            'footfall': 30, 'water_flow': 3, 'ph': 9.2, 'turbidity': 320
        },
        'water_shortage': {
            'ammonia': 65, 'methane': 50, 'humidity': 80, 'temperature': 33,
            'footfall': 35, 'water_flow': 0.5, 'ph': 8.5, 'turbidity': 180
        },
        'peak_evening': {
            'ammonia': 80, 'methane': 65, 'humidity': 87, 'temperature': 35,
            'footfall': 48, 'water_flow': 4, 'ph': 8.9, 'turbidity': 250
        },
        'extreme_dirty': {
            'ammonia': 95, 'methane': 85, 'humidity': 92, 'temperature': 39,
            'footfall': 35, 'water_flow': 1, 'ph': 9.5, 'turbidity': 400
        }
    }
    
    if scenario not in scenarios:
        return jsonify({'error': 'Invalid scenario'}), 400
    
    prediction = system.predict_hygiene(scenarios[scenario])
    
    # Add realistic descriptions
    descriptions = {
        'clean': 'Well-maintained toilet with regular cleaning',
        'moderate': 'Average public toilet with some maintenance issues',
        'dirty': 'Poorly maintained toilet requiring immediate attention',
        'emergency': 'Critical hygiene emergency - immediate intervention needed',
        'morning_rush': 'Morning rush hour with accumulated overnight odors',
        'poor_maintenance': 'Severely neglected facility with multiple hygiene issues',
        'water_shortage': 'Water crisis making proper cleaning impossible',
        'peak_evening': 'Evening peak usage with rising contamination',
        'extreme_dirty': 'Extremely unsanitary conditions - health hazard'
    }
    
    return jsonify({
        'scenario': scenario,
        'sensors': scenarios[scenario],
        'prediction': prediction,
        'description': descriptions.get(scenario, f'{scenario.title()} toilet conditions'),
        'location_context': 'Indian Public Washroom'
    })

@app.route('/real-time-data')
def real_time_data_endpoint():
    """Get latest real-time sensor data with prediction"""
    if latest_reading:
        prediction = system.predict_hygiene(latest_reading['sensors'])
        latest_reading['prediction'] = prediction
        latest_reading['alerts'] = current_alerts
        latest_reading['statistics'] = system_stats
        return jsonify(latest_reading)
    else:
        # Return initial data if no readings yet
        initial_data = {
            'timestamp': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'sensors': simulator.base_values,
            'prediction': system.predict_hygiene(simulator.base_values),
            'alerts': [],
            'statistics': system_stats,
            'metadata': {
                'location': 'Public Toilet #1',
                'status': 'initializing',
                'battery_level': 100
            }
        }
        return jsonify(initial_data)

@app.route('/prediction-history')
def prediction_history_endpoint():
    """Get prediction history for charts"""
    return jsonify(prediction_history)

@app.route('/sensor-history')
def sensor_history_endpoint():
    """Get sensor data history"""
    return jsonify(sensor_data_log)

@app.route('/system-stats')
def system_stats_endpoint():
    """Get system statistics"""
    uptime = datetime.now() - system_stats['start_time']
    stats = {
        **system_stats,
        'uptime_seconds': uptime.total_seconds(),
        'uptime_formatted': str(uptime).split('.')[0],
        'data_collection_rate': len(real_time_data) / max(1, uptime.total_seconds()) * 60,  # per minute
        'prediction_accuracy_trend': calculate_accuracy_trend()
    }
    return jsonify(stats)

@app.route('/export-data')
def export_data():
    """Export sensor data as CSV"""
    if not sensor_data_log:
        return jsonify({'error': 'No data available'}), 404
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ['timestamp', 'hygiene_score', 'hygiene_status', 'ammonia', 'methane', 
                  'humidity', 'temperature', 'footfall', 'water_flow', 'ph', 'turbidity']
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for entry in sensor_data_log:
        writer.writerow({field: entry.get(field, '') for field in fieldnames})
    
    # Create response
    response = Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=toilet_sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )
    
    return response

@app.route('/api/status')
def api_status():
    """API status and health check"""
    uptime = datetime.now() - system_stats['start_time']
    return jsonify({
        'status': 'running',
        'model_loaded': system.model is not None,
        'data_points_collected': len(real_time_data),
        'predictions_made': len(prediction_history),
        'alerts_generated': len(current_alerts),
        'uptime_seconds': uptime.total_seconds(),
        'system_health': 'healthy' if len(real_time_data) > 0 else 'initializing'
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_status': 'loaded' if system.model is not None else 'missing',
        'data_status': 'active' if latest_reading else 'inactive'
    })

def calculate_accuracy_trend():
    """Calculate prediction accuracy trend"""
    if len(prediction_history) < 10:
        return 0.0
    
    # Simple trend calculation based on recent predictions
    recent = prediction_history[-10:]
    scores = [p['hygiene_score'] for p in recent]
    
    # Calculate trend (simplified)
    if len(scores) >= 2:
        trend = (scores[-1] - scores[0]) / len(scores)
        return round(trend, 2)
    
    return 0.0

if __name__ == '__main__':
    print("🚀 Starting Enhanced Smart Toilet Hygiene Prediction System...")
    print("📊 Real-time Dashboard: http://localhost:5000")
    print("🔬 IoT Simulator: http://localhost:5000/iot-simulator")
    print("📈 Analytics Dashboard: http://localhost:5000/analytics")
    print("🔧 API Demo: http://localhost:5000/demo/clean")
    print("📡 Real-time Data: http://localhost:5000/real-time-data")
    print("📊 Prediction History: http://localhost:5000/prediction-history")
    print("📈 System Stats: http://localhost:5000/system-stats")
    print("💾 Export Data: http://localhost:5000/export-data")
    print("🏥 Health Check: http://localhost:5000/api/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)