"""
Smart Public Toilet Hygiene Prediction System - Flask Web App
Interactive web interface for hackathon demonstration
"""

from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import json
from hygiene_prediction_system import HygienePredictionSystem

app = Flask(__name__)

# Initialize the prediction system
hygiene_system = HygienePredictionSystem()

# Load the trained model
if not hygiene_system.load_model('hygiene_model.pkl'):
    print("Warning: Model not found. Please run hygiene_prediction_system.py first to train the model.")

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

if __name__ == '__main__':
    print("🚀 Starting Smart Toilet Hygiene Prediction Web App...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔧 Demo endpoints available:")
    print("   - /demo/clean")
    print("   - /demo/dirty") 
    print("   - /demo/moderate")
    print("📊 API endpoint: /predict (POST)")
    
    app.run(debug=True, host='0.0.0.0', port=5000)