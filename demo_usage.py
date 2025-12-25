"""
Demo script for Smart Public Toilet Hygiene Prediction System
Shows how to use the trained model for predictions
"""

import json
from hygiene_prediction_system import HygienePredictionSystem

def main():
    print("HYGIENE PREDICTION SYSTEM - DEMO USAGE")
    print("=" * 50)
    
    # Initialize system and load trained model
    hygiene_system = HygienePredictionSystem()
    
    if not hygiene_system.load_model('hygiene_model.pkl'):
        print("Failed to load model. Please train the model first.")
        return
    
    # Demo 1: Dirty toilet scenario
    print("\n📊 DEMO 1: DIRTY TOILET SCENARIO")
    dirty_toilet = {
        "ammonia": 95.0,
        "methane": 85.0,
        "humidity": 75.0,
        "temperature": 32.0,
        "footfall": 45.0,
        "water_flow": 2.0,
        "ph": 5.5,
        "turbidity": 350.0
    }
    
    result1 = hygiene_system.predict_hygiene(dirty_toilet)
    print("Input sensor data:")
    for key, value in dirty_toilet.items():
        print(f"  {key}: {value}")
    print(f"Prediction: {json.dumps(result1, indent=2)}")
    
    # Demo 2: Clean toilet scenario
    print("\n📊 DEMO 2: CLEAN TOILET SCENARIO")
    clean_toilet = {
        "ammonia": 12.0,
        "methane": 8.0,
        "humidity": 52.0,
        "temperature": 21.0,
        "footfall": 5.0,
        "water_flow": 22.0,
        "ph": 7.2,
        "turbidity": 15.0
    }
    
    result2 = hygiene_system.predict_hygiene(clean_toilet)
    print("Input sensor data:")
    for key, value in clean_toilet.items():
        print(f"  {key}: {value}")
    print(f"Prediction: {json.dumps(result2, indent=2)}")
    
    # Demo 3: Moderate toilet scenario
    print("\n📊 DEMO 3: MODERATE TOILET SCENARIO")
    moderate_toilet = {
        "ammonia": 45.0,
        "methane": 35.0,
        "humidity": 58.0,
        "temperature": 24.0,
        "footfall": 18.0,
        "water_flow": 15.0,
        "ph": 6.8,
        "turbidity": 85.0
    }
    
    result3 = hygiene_system.predict_hygiene(moderate_toilet)
    print("Input sensor data:")
    for key, value in moderate_toilet.items():
        print(f"  {key}: {value}")
    print(f"Prediction: {json.dumps(result3, indent=2)}")
    
    # Demo 4: Real-time API usage example
    print("\n📡 DEMO 4: API USAGE EXAMPLE")
    api_input = json.dumps({
        "ammonia": 28.5,
        "methane": 22.1,
        "humidity": 61.2,
        "temperature": 26.8,
        "footfall": 12.3,
        "water_flow": 18.7,
        "ph": 7.0,
        "turbidity": 42.1
    })
    
    api_result = hygiene_system.predict_hygiene(api_input)
    print("API Input (JSON string):")
    print(f"  {api_input}")
    print(f"API Response: {json.dumps(api_result, indent=2)}")
    
    print("\n" + "=" * 50)
    print("✅ DEMO COMPLETE - SYSTEM READY FOR INTEGRATION!")
    print("=" * 50)

if __name__ == "__main__":
    main()