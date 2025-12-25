"""
🚀 Real-Time Smart Toilet Hygiene Monitoring System Launcher
This script launches the enhanced system with live data simulation
"""

import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def check_model_exists():
    """Check if the trained model exists"""
    model_file = Path('hygiene_model.pkl')
    if not model_file.exists():
        print("⚠️  Trained model not found! Training a new model...")
        try:
            import hygiene_prediction_system
            system = hygiene_prediction_system.HygienePredictionSystem()
            dataset = system.generate_synthetic_dataset(n_samples=3000)
            system.train_model(dataset)
            system.save_model('hygiene_model.pkl')
            print("✅ Model trained and saved successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to train model: {e}")
            return False
    return True

def launch_system():
    """Launch the enhanced real-time system"""
    print("🚀 Launching Real-Time Smart Toilet Hygiene Monitoring System")
    print("=" * 70)
    
    # Check model
    if not check_model_exists():
        print("❌ Cannot start system without trained model")
        return False
    
    print("📡 Starting enhanced web server with real-time data simulation...")
    
    try:
        # Start the enhanced web application
        process = subprocess.Popen(
            [sys.executable, 'enhanced_web_app.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("\n🌐 System URLs:")
        print("├─ 📊 Real-time Dashboard: http://localhost:5000")
        print("├─ 🔬 IoT Simulator: http://localhost:5000/iot-simulator")
        print("├─ 📈 Analytics Dashboard: http://localhost:5000/analytics")
        print("├─ 🔧 API Demo: http://localhost:5000/demo/clean")
        print("├─ 📡 Real-time Data: http://localhost:5000/real-time-data")
        print("├─ 📊 Prediction History: http://localhost:5000/prediction-history")
        print("├─ 📈 System Stats: http://localhost:5000/system-stats")
        print("├─ 💾 Export Data: http://localhost:5000/export-data")
        print("└─ 🏥 Health Check: http://localhost:5000/api/health")
        
        print("\n🎯 Opening dashboards in browser...")
        
        # Open main dashboard
        webbrowser.open('http://localhost:5000', new=2)
        time.sleep(1)
        
        # Open IoT simulator
        webbrowser.open('http://localhost:5000/iot-simulator', new=2)
        time.sleep(1)
        
        # Open analytics dashboard
        webbrowser.open('http://localhost:5000/analytics', new=2)
        
        print("\n✅ System launched successfully!")
        print("\n🎮 Demo Instructions:")
        print("1. Start with the Real-time Dashboard to see live data")
        print("2. Use IoT Simulator to manually control sensor values")
        print("3. Check Analytics Dashboard for trends and statistics")
        print("4. Use quick scenario buttons for instant demos")
        print("5. Export data for analysis and reporting")
        
        print("\n📊 Key Features:")
        print("✨ Real-time sensor data simulation with trends")
        print("✨ Interactive IoT sensor controls")
        print("✨ Live charts and visualizations")
        print("✨ Automated alert system")
        print("✨ Data export capabilities")
        print("✨ System health monitoring")
        print("✨ Prediction history tracking")
        
        print("\n⏹️  Press Ctrl+C to stop the system")
        
        # Wait for process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping system...")
            process.terminate()
            process.wait()
            print("✅ System stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch system: {e}")
        return False

if __name__ == "__main__":
    print("🚽 Real-Time Smart Toilet Hygiene Monitoring System")
    print("🎯 Hackathon-Ready Demo Platform")
    print("=" * 70)
    
    success = launch_system()
    
    if success:
        print("\n🎉 System ready for hackathon demonstration!")
    else:
        print("\n❌ System launch failed. Check error messages above.")
        sys.exit(1)