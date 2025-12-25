"""
🚽 Realistic Indian Public Washroom Demo
Shows typical poor hygiene conditions with realistic sensor readings
"""

import requests
import time
import json

def demo_realistic_conditions():
    """Demonstrate realistic poor hygiene conditions"""
    
    print("🚽 Realistic Indian Public Washroom Conditions Demo")
    print("=" * 60)
    print("This demo shows typical poor hygiene conditions found in")
    print("Indian public washrooms with realistic sensor readings.\n")
    
    # Test the real-time data endpoint
    try:
        print("📡 Fetching current sensor data...")
        response = requests.get('http://localhost:5000/real-time-data')
        
        if response.status_code == 200:
            data = response.json()
            sensors = data['sensors']
            
            print(f"\n🕐 Current Time: {data['timestamp'][:19]}")
            print(f"📍 Location: {data['metadata']['location']}")
            print(f"🔋 Battery: {sensors.get('battery_level', 'N/A')}%\n")
            
            print("📊 Current Sensor Readings (Realistic Indian Public Toilet):")
            print("-" * 60)
            
            # Ammonia (urine odors - typically high)
            ammonia = sensors['ammonia']
            ammonia_status = "🔴 CRITICAL" if ammonia > 70 else "🟡 WARNING" if ammonia > 50 else "🟢 OK"
            print(f"💨 Ammonia (Urine Odor):     {ammonia:6.1f} ppm   {ammonia_status}")
            print(f"   💡 Note: High levels indicate poor cleaning/ventilation")
            
            # Methane (sewage gas)
            methane = sensors['methane']
            methane_status = "🔴 CRITICAL" if methane > 60 else "🟡 WARNING" if methane > 45 else "🟢 OK"
            print(f"💨 Methane (Sewage Gas):     {methane:6.1f} ppm   {methane_status}")
            print(f"   💡 Note: Indicates sewage system issues")
            
            # Water quality indicators
            turbidity = sensors['turbidity']
            turbidity_status = "🔴 CRITICAL" if turbidity > 200 else "🟡 WARNING" if turbidity > 100 else "🟢 OK"
            print(f"💧 Turbidity (Water Clarity): {turbidity:6.1f} NTU  {turbidity_status}")
            print(f"   💡 Note: High turbidity = contaminated water")
            
            ph = sensors['ph']
            ph_status = "🔴 CRITICAL" if ph > 9 else "🟡 WARNING" if ph > 8.5 else "🟢 OK"
            print(f"⚗️  pH (Water Chemistry):     {ph:6.1f}      {ph_status}")
            print(f"   💡 Note: Alkaline = harsh cleaning chemicals")
            
            # Usage patterns
            water_flow = sensors['water_flow']
            flow_status = "🔴 CRITICAL" if water_flow < 5 else "🟡 WARNING" if water_flow < 8 else "🟢 OK"
            print(f"🚿 Water Flow Rate:         {water_flow:6.1f} L/min {flow_status}")
            print(f"   💡 Note: Low flow = water shortage/maintenance issues")
            
            footfall = sensors['footfall']
            foot_status = "🔴 HIGH" if footfall > 35 else "🟡 MODERATE" if footfall > 20 else "🟢 LOW"
            print(f"👥 Footfall (Usage):        {footfall:6.1f} people {foot_status}")
            print(f"   💡 Note: High usage = more frequent cleaning needed")
            
            # Environmental conditions
            humidity = sensors['humidity']
            humid_status = "🔴 CRITICAL" if humidity > 85 else "🟡 WARNING" if humidity > 75 else "🟢 OK"
            print(f"💧 Humidity:                {humidity:6.1f} %    {humid_status}")
            print(f"   💡 Note: High humidity = poor ventilation")
            
            temperature = sensors['temperature']
            temp_status = "🔴 CRITICAL" if temperature > 38 else "🟡 WARNING" if temperature > 32 else "🟢 OK"
            print(f"🌡️  Temperature:             {temperature:6.1f} °C   {temp_status}")
            print(f"   💡 Note: High temp = overcrowding/poor ventilation")
            
            print("\n" + "=" * 60)
            
            # Get hygiene prediction
            print("🎯 Hygiene Assessment:")
            try:
                pred_response = requests.post('http://localhost:5000/predict', 
                                            json={'sensors': sensors})
                if pred_response.status_code == 200:
                    prediction = pred_response.json()
                    score = prediction.get('hygiene_score', 0)
                    status = prediction.get('hygiene_status', 'Unknown')
                    confidence = prediction.get('confidence', 0)
                    explanation = prediction.get('explanation', '')
                    
                    if score < 30:
                        hygiene_display = f"🔴 DIRTY (Score: {score:.1f})"
                    elif score < 70:
                        hygiene_display = f"🟡 MODERATE (Score: {score:.1f})"
                    else:
                        hygiene_display = f"🟢 CLEAN (Score: {score:.1f})"
                    
                    print(f"   Status: {hygiene_display}")
                    print(f"   Confidence: {confidence:.1%}")
                    print(f"   Explanation: {explanation}")
                else:
                    print("   ❌ Could not get hygiene prediction")
            except Exception as e:
                print(f"   ❌ Prediction error: {e}")
            
            print("\n" + "=" * 60)
            print("🔍 Realistic Scenario Analysis:")
            print("• High ammonia: Poor cleaning, urine accumulation")
            print("• Low water flow: Water shortage, maintenance issues")
            print("• High turbidity: Contaminated water supply")
            print("• High temperature/humidity: Poor ventilation, overcrowding")
            print("• High footfall: Heavy usage requiring frequent cleaning")
            print("\n💡 This represents typical conditions in many Indian public toilets")
            print("   where maintenance is irregular and hygiene standards are poor.")
            
        else:
            print(f"❌ Failed to fetch data: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the web app is running.")
        print("   Start with: python enhanced_web_app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_scenarios():
    """Show different realistic scenarios"""
    scenarios = {
        'morning_rush': {
            'description': 'Morning Rush Hour (8 AM)',
            'expected_conditions': 'Heavy usage, accumulated overnight odors'
        },
        'poor_maintenance': {
            'description': 'Poor Maintenance Day',
            'expected_conditions': 'High ammonia, low water flow, contaminated water'
        },
        'water_shortage': {
            'description': 'Water Shortage Crisis',
            'expected_conditions': 'Very low water flow, hygiene severely compromised'
        },
        'peak_evening': {
            'description': 'Evening Peak (7 PM)',
            'expected_conditions': 'High usage, rising odors, temperature issues'
        }
    }
    
    print("\n🎭 Realistic Scenarios for Indian Public Toilets:")
    print("=" * 60)
    
    for key, scenario in scenarios.items():
        print(f"\n📅 {scenario['description']}:")
        print(f"   Expected: {scenario['expected_conditions']}")
        print(f"   Demo URL: http://localhost:5000/demo/{key}")

if __name__ == "__main__":
    demo_realistic_conditions()
    demo_scenarios()
    
    print(f"\n🌐 Open these URLs in your browser:")
    print(f"   📊 Real-time Dashboard: http://localhost:5000")
    print(f"   🔬 IoT Simulator: http://localhost:5000/iot-simulator")
    print(f"   📈 Analytics: http://localhost:5000/analytics")
    print(f"\n🎯 The system now shows realistic poor hygiene conditions")
    print(f"   commonly found in Indian public washrooms!")