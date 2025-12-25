"""
Smart Public Toilet Hygiene Prediction System - Flask Web App
Interactive web interface for hackathon demonstration
"""

from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import json
from hygiene_prediction_system import HygienePredictionSystem
from real_time_data import RealTimeSensorSimulator
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Initialize the prediction system and real-time simulator
hygiene_system = HygienePredictionSystem()
simulator = RealTimeSensorSimulator()

# Global variables for real-time data
real_time_data = []
latest_reading = None
current_alerts = []
prediction_history = []

# Load the trained model
if not hygiene_system.load_model('hygiene_model.pkl'):
    print("Warning: Model not found. Please run hygiene_prediction_system.py first to train the model.")

# Background thread for continuous data generation
def background_data_generator():
    global latest_reading, current_alerts, prediction_history
    while True:
        try:
            # Generate new reading
            latest_reading = simulator.get_current_readings()
            
            # Generate alerts
            current_alerts = simulator.generate_alert(latest_reading)
            
            # Make prediction
            prediction = hygiene_system.predict_hygiene(latest_reading['sensors'])
            prediction['timestamp'] = latest_reading['timestamp']
            prediction['hour'] = latest_reading['hour']
            
            # Add to history
            prediction_history.append(prediction)
            if len(prediction_history) > 100:  # Keep last 100 predictions
                prediction_history.pop(0)
            
            # Add to real-time data
            real_time_data.append(latest_reading)
            if len(real_time_data) > 50:  # Keep last 50 readings
                real_time_data.pop(0)
            
            time.sleep(3)  # Update every 3 seconds
            
        except Exception as e:
            print(f"Background data generation error: {e}")
            time.sleep(5)

# Start background thread
bg_thread = threading.Thread(target=background_data_generator, daemon=True)
bg_thread.start()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for hygiene prediction"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Make prediction
        result = hygiene_system.predict_hygiene(data)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/demo/<scenario>')
def demo_scenario(scenario):
    """Pre-configured demo scenarios"""
    scenarios = {
        "clean": {
            "ammonia": 12.0, "methane": 8.0, "humidity": 52.0,
            "temperature": 21.0, "footfall": 5.0, "water_flow": 22.0,
            "ph": 7.2, "turbidity": 15.0
        },
        "dirty": {
            "ammonia": 95.0, "methane": 85.0, "humidity": 75.0,
            "temperature": 32.0, "footfall": 45.0, "water_flow": 2.0,
            "ph": 5.5, "turbidity": 350.0
        },
        "moderate": {
            "ammonia": 45.0, "methane": 35.0, "humidity": 58.0,
            "temperature": 24.0, "footfall": 18.0, "water_flow": 15.0,
            "ph": 6.8, "turbidity": 85.0
        }
    }
    
    if scenario not in scenarios:
        return jsonify({"error": "Invalid scenario. Use: clean, dirty, or moderate"}), 400
    
    result = hygiene_system.predict_hygiene(scenarios[scenario])
    result["scenario"] = scenario.title()
    return jsonify(result)

@app.route('/sensor-simulation')
def sensor_simulation():
    """Real-time sensor simulation page"""
    return render_template('sensor_simulation.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics.html')

@app.route('/real-time-data')
def real_time_data_endpoint():
    """Get latest real-time sensor data"""
    if latest_reading:
        # Add prediction to the reading
        prediction = hygiene_system.predict_hygiene(latest_reading['sensors'])
        latest_reading['prediction'] = prediction
        latest_reading['alerts'] = current_alerts
        return jsonify(latest_reading)
    else:
        # Return initial data if no readings yet
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'sensors': simulator.base_values,
            'prediction': hygiene_system.predict_hygiene(simulator.base_values),
            'alerts': [],
            'metadata': {
                'location': 'Public Toilet #1',
                'status': 'initializing',
                'battery_level': 100
            }
        })

@app.route('/prediction-history')
def prediction_history_endpoint():
    """Get prediction history for charts"""
    return jsonify(prediction_history)

@app.route('/api/status')
def api_status():
    """API status and statistics"""
    return jsonify({
        'status': 'running',
        'model_loaded': hygiene_system.model is not None,
        'data_points_collected': len(real_time_data),
        'predictions_made': len(prediction_history),
        'alerts_generated': len(current_alerts),
        'uptime': time.time()
    })

if __name__ == '__main__':
    print("🚀 Starting Smart Toilet Hygiene Prediction Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Demo endpoints available:")
    print("   - /demo/clean")
    print("   - /demo/dirty") 
    print("   - /demo/moderate")
    print("📊 API endpoint: /predict (POST)")
    print("📡 Real-time Data: http://localhost:5000/real-time-data")
    print("📊 Prediction History: http://localhost:5000/prediction-history")
    
    app.run(debug=True, host='0.0.0.0', port=5000)