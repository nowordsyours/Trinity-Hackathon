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
            prediction['timestamp'] = latest_reading['timestamp']
            prediction['hour'] = latest_reading['hour']
            
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
    """Pre-configured demo scenarios"""
    scenarios = {
        'clean': {
            'ammonia': 15.0, 'methane': 10.0, 'humidity': 45.0, 'temperature': 22.0,
            'footfall': 5.0, 'water_flow': 25.0, 'ph': 7.0, 'turbidity': 20.0
        },
        'moderate': {
            'ammonia': 45.0, 'methane': 35.0, 'humidity': 65.0, 'temperature': 24.0,
            'footfall': 20.0, 'water_flow': 15.0, 'ph': 7.2, 'turbidity': 80.0
        },
        'dirty': {
            'ammonia': 85.0, 'methane': 75.0, 'humidity': 80.0, 'temperature': 28.0,
            'footfall': 35.0, 'water_flow': 5.0, 'ph': 8.5, 'turbidity': 180.0
        },
        'emergency': {
            'ammonia': 95.0, 'methane': 90.0, 'humidity': 85.0, 'temperature': 32.0,
            'footfall': 45.0, 'water_flow': 1.0, 'ph': 9.0, 'turbidity': 450.0
        }
    }
    
    if scenario not in scenarios:
        return jsonify({'error': 'Invalid scenario'}), 400
    
    result = system.predict_hygiene(scenarios[scenario])
    return jsonify(result)

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