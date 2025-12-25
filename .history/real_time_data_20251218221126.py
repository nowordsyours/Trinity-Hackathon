"""
Real-time IoT Sensor Data Simulator
Generates realistic sensor readings with trends and anomalies
"""

import random
import time
import json
from datetime import datetime, timedelta
import numpy as np

class RealTimeSensorSimulator:
    def __init__(self):
        # More realistic base values for Indian public washrooms
        self.base_values = {
            'ammonia': 55.0,     # Higher baseline (urine odors common)
            'methane': 45.0,     # Higher baseline (sewage issues)
            'humidity': 75.0,    # Higher humidity in tropical climate
            'temperature': 32.0, # Higher temperature (Indian climate)
            'footfall': 25.0,    # Higher footfall in public toilets
            'water_flow': 8.0,   # Lower water flow (water conservation issues)
            'ph': 8.5,           # More alkaline (cleaning chemicals)
            'turbidity': 120.0   # Higher turbidity (poor water quality)
        }
        
        # Trends that reflect real maintenance issues
        self.trends = {
            'ammonia': 1.2,      # Rapidly increasing (poor cleaning)
            'methane': 0.8,      # Increasing (sewage problems)
            'humidity': 0.5,     # Increasing (poor ventilation)
            'temperature': 0.3,  # Gradually increasing (overcrowding)
            'footfall': 2.0,     # High peaks during rush hours
            'water_flow': -1.0,  # Rapidly decreasing (water issues)
            'ph': 0.2,           # Gradually becoming more alkaline
            'turbidity': 2.5     # Rapidly increasing (filter failure)
        }
        
        self.anomaly_probability = 0.15  # 15% chance of anomaly (more realistic)
        self.peak_hours = [7, 8, 9, 12, 13, 18, 19, 20, 21]  # Extended rush hours
        
    def generate_sensor_reading(self, sensor_type, current_hour):
        """Generate realistic sensor reading with trends and noise"""
        base = self.base_values[sensor_type]
        trend = self.trends[sensor_type]
        
        # Add time-based trend
        value = base + (trend * random.gauss(1, 0.1))
        
        # Realistic hourly patterns for Indian public toilets
        if sensor_type == 'footfall':
            # Heavy usage during rush hours, moderate during day, minimal at night
            if current_hour in [7, 8, 9, 12, 13, 18, 19, 20, 21]:  # Extended rush hours
                value += random.uniform(35, 55)  # Heavy footfall
            elif current_hour in [10, 11, 14, 15, 16, 17, 22]:  # Moderate usage
                value += random.uniform(15, 30)  # Moderate footfall
            elif 6 <= current_hour <= 23:  # Occasional usage
                value += random.uniform(5, 15)
            else:  # Late night/early morning
                value = max(0, value - random.uniform(10, 20))  # Minimal usage
        
        elif sensor_type == 'water_flow':
            # Water supply issues common in India
            if current_hour in [6, 12, 18]:  # Supposed cleaning times
                if random.random() < 0.3:  # Only 30% chance of actual cleaning
                    value += random.uniform(5, 15)  # Minimal cleaning water
                else:
                    value = max(0, value - random.uniform(10, 20))  # No cleaning water
            elif current_hour in [7, 8, 13, 14, 19, 20]:  # Peak usage times
                value += random.uniform(8, 18)  # User water consumption
            else:
                # Water conservation issues - often minimal flow
                if random.random() < 0.4:  # 40% chance of water shortage
                    value = max(0, value - random.uniform(15, 25))
        
        elif sensor_type == 'ammonia':
            # Realistic ammonia patterns - higher after heavy usage
            if current_hour in [9, 10, 14, 15, 21, 22]:  # After morning/noon/evening rush
                value += random.uniform(25, 45)  # Strong urine buildup
            elif current_hour in [6, 7, 23, 0, 1, 2, 3, 4, 5]:  # Early morning/late night
                value += random.uniform(35, 60)  # Accumulated odors from poor overnight cleaning
        
        elif sensor_type == 'turbidity':
            # Water quality issues throughout the day
            if current_hour in [6, 7, 12, 13, 18, 19]:  # During supposed cleaning times
                if random.random() < 0.4:  # Only 40% of time actually cleaned
                    value += random.uniform(30, 80)  # Poor cleaning water quality
            elif current_hour in [8, 14, 20]:  # Peak usage times
                value += random.uniform(40, 90)  # User contamination
        
        # Add random noise
        noise = random.gauss(0, base * 0.05)  # 5% noise
        value += noise
        
        # More realistic anomalies for Indian public washrooms
        if random.random() < self.anomaly_probability:
            if sensor_type == 'ammonia':
                # Strong urine odors, cleaning chemical buildup
                value += random.uniform(40, 80)  # Much higher spikes
            elif sensor_type == 'methane':
                # Sewage gas buildup, poor ventilation
                value += random.uniform(35, 70)  # Higher methane spikes
            elif sensor_type == 'ph':
                # Harsh cleaning chemicals or contamination
                value += random.uniform(-1, 3) if random.random() < 0.5 else random.uniform(1, 4)
            elif sensor_type == 'water_flow':
                # Water supply issues, clogged pipes
                value = max(0, value - random.uniform(20, 35))  # Severe drops
            elif sensor_type == 'turbidity':
                # Severe water contamination, algae growth
                value += random.uniform(100, 250)  # Extreme turbidity spikes
            elif sensor_type == 'humidity':
                # Poor ventilation, water leakage
                value += random.uniform(15, 30)  # High humidity spikes
            elif sensor_type == 'temperature':
                # Overcrowding, poor ventilation, equipment overheating
                value += random.uniform(5, 12)  # Temperature spikes
        
        # Clamp to realistic ranges
        return self.clamp_value(sensor_type, value)
    
    def clamp_value(self, sensor_type, value):
        """Ensure values stay within realistic ranges"""
        ranges = {
            'ammonia': (0, 100),
            'methane': (0, 100),
            'humidity': (30, 90),
            'temperature': (15, 45),
            'footfall': (0, 50),
            'water_flow': (0, 30),
            'ph': (4, 9),
            'turbidity': (0, 500)
        }
        
        min_val, max_val = ranges[sensor_type]
        return max(min_val, min(max_val, value))
    
    def get_current_readings(self):
        """Get current sensor readings with timestamp"""
        current_hour = datetime.now().hour
        readings = {}
        
        for sensor in self.base_values.keys():
            readings[sensor] = self.generate_sensor_reading(sensor, current_hour)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'hour': current_hour,
            'sensors': readings,
            'metadata': {
                'location': 'Public Toilet #1',
                'status': 'active',
                'battery_level': random.uniform(75, 100)
            }
        }
    
    def simulate_data_stream(self, duration_minutes=60, interval_seconds=5):
        """Simulate continuous data stream for demo purposes"""
        print("🔄 Starting Real-time Sensor Data Stream...")
        print("=" * 50)
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        data_history = []
        
        while datetime.now() < end_time:
            reading = self.get_current_readings()
            data_history.append(reading)
            
            # Print current status
            print(f"\n🕐 {reading['timestamp'][11:19]} | Hour: {reading['hour']:2d}")
            print("📊 Sensor Readings:")
            for sensor, value in reading['sensors'].items():
                status = self.get_sensor_status(sensor, value)
                print(f"  {sensor:12}: {value:6.1f} {status}")
            
            # Simulate hygiene prediction
            from hygiene_prediction_system import HygienePredictionSystem
            system = HygienePredictionSystem()
            system.load_model('hygiene_model.pkl')
            
            prediction = system.predict_hygiene(reading['sensors'])
            if 'hygiene_score' in prediction:
                print(f"🎯 Hygiene Score: {prediction['hygiene_score']} ({prediction['hygiene_status']})")
            
            time.sleep(interval_seconds)
        
        print(f"\n✅ Data stream completed. Collected {len(data_history)} readings.")
        return data_history
    
    def get_sensor_status(self, sensor_type, value):
        """Get sensor status indicator"""
        thresholds = {
            'ammonia': [(0, 30, '✅'), (30, 60, '⚠️'), (60, 100, '❌')],
            'methane': [(0, 25, '✅'), (25, 50, '⚠️'), (50, 100, '❌')],
            'humidity': [(30, 60, '✅'), (60, 80, '⚠️'), (80, 90, '❌')],
            'temperature': [(20, 26, '✅'), (15, 20, '⚠️'), (26, 45, '⚠️')],
            'footfall': [(0, 20, '✅'), (20, 35, '⚠️'), (35, 50, '❌')],
            'water_flow': [(15, 30, '✅'), (5, 15, '⚠️'), (0, 5, '❌')],
            'ph': [(6.5, 7.5, '✅'), (6, 6.5, '⚠️'), (7.5, 9, '⚠️')],
            'turbidity': [(0, 50, '✅'), (50, 150, '⚠️'), (150, 500, '❌')]
        }
        
        for min_val, max_val, indicator in thresholds[sensor_type]:
            if min_val <= value <= max_val:
                return indicator
        
        return '❓'
    
    def generate_alert(self, readings):
        """Generate alerts based on sensor readings"""
        alerts = []
        sensors = readings['sensors']
        
        # Critical alerts
        if sensors['ammonia'] > 80:
            alerts.append({'type': 'critical', 'message': 'High ammonia levels detected!'})
        
        if sensors['methane'] > 70:
            alerts.append({'type': 'critical', 'message': 'High methane levels detected!'})
        
        if sensors['turbidity'] > 300:
            alerts.append({'type': 'critical', 'message': 'Water contamination detected!'})
        
        if sensors['water_flow'] < 3:
            alerts.append({'type': 'warning', 'message': 'Low water flow - cleaning system may need maintenance'})
        
        if sensors['ph'] < 5.5 or sensors['ph'] > 8.5:
            alerts.append({'type': 'warning', 'message': 'pH levels outside optimal range'})
        
        if sensors['footfall'] > 40:
            alerts.append({'type': 'info', 'message': 'High usage detected - consider more frequent cleaning'})
        
        return alerts

if __name__ == "__main__":
    simulator = RealTimeSensorSimulator()
    
    # Run a 5-minute demo
    print("🚀 Starting 5-minute Real-time Data Demo...")
    data = simulator.simulate_data_stream(duration_minutes=5, interval_seconds=10)
    
    # Save sample data
    with open('real_time_sensor_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\n📊 Sample data saved to real_time_sensor_data.json")