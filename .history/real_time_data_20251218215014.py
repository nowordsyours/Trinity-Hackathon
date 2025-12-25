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
        self.base_values = {
            'ammonia': 30.0,
            'methane': 25.0,
            'humidity': 55.0,
            'temperature': 23.0,
            'footfall': 15.0,
            'water_flow': 18.0,
            'ph': 7.0,
            'turbidity': 45.0
        }
        
        self.trends = {
            'ammonia': 0.5,      # Gradually increasing
            'methane': 0.3,      # Gradually increasing
            'humidity': 0.2,     # Stable with small variations
            'temperature': 0.1,  # Stable
            'footfall': 1.0,     # Peak during certain hours
            'water_flow': -0.3,  # Gradually decreasing (maintenance needed)
            'ph': 0.0,           # Stable around neutral
            'turbidity': 0.8     # Increasing (filter needs replacement)
        }
        
        self.anomaly_probability = 0.05  # 5% chance of anomaly
        self.peak_hours = [8, 12, 18, 20]  # High footfall hours
        
    def generate_sensor_reading(self, sensor_type, current_hour):
        """Generate realistic sensor reading with trends and noise"""
        base = self.base_values[sensor_type]
        trend = self.trends[sensor_type]
        
        # Add time-based trend
        value = base + (trend * random.gauss(1, 0.1))
        
        # Add hourly patterns
        if sensor_type == 'footfall':
            if current_hour in self.peak_hours:
                value += random.uniform(20, 35)
            elif 6 <= current_hour <= 22:
                value += random.uniform(5, 15)
            else:
                value = max(0, value - random.uniform(5, 10))
        
        elif sensor_type == 'water_flow':
            if current_hour in [6, 12, 18]:  # Cleaning times
                value += random.uniform(10, 20)
        
        elif sensor_type == 'ammonia':
            # Higher after peak hours
            if current_hour in [9, 13, 21]:
                value += random.uniform(10, 25)
        
        elif sensor_type == 'turbidity':
            # Higher during cleaning
            if current_hour in [6, 12, 18]:
                value += random.uniform(20, 40)
        
        # Add random noise
        noise = random.gauss(0, base * 0.05)  # 5% noise
        value += noise
        
        # Occasional anomalies
        if random.random() < self.anomaly_probability:
            if sensor_type in ['ammonia', 'methane']:
                value += random.uniform(30, 60)  # Sudden spike
            elif sensor_type == 'ph':
                value += random.uniform(-2, 2)   # Drastic pH change
            elif sensor_type == 'water_flow':
                value = max(0, value - random.uniform(15, 25))  # Sudden drop
        
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