"""
Smart Toilet Hygiene Prediction System - Web App Launcher
Quick launcher for the Flask web application
"""

import subprocess
import webbrowser
import time
import sys

def main():
    print("🚀 Launching Smart Toilet Hygiene Prediction Web App...")
    print("=" * 60)
    
    # Check if model exists
    try:
        import joblib
        joblib.load('hygiene_model.pkl')
        print(" Trained model loaded successfully!")
    except FileNotFoundError:
        print(" Model not found. Training the model first...")
        print("Running: python hygiene_prediction_system.py")
        subprocess.run([sys.executable, 'hygiene_prediction_system.py'])
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    print("\n🌐 Starting Flask web server...")
    print("📱 Web App will be available at: http://localhost:5000")
    print("📊 Analytics Dashboard: http://localhost:5000/analytics")
    print("\n🎯 Features available:")
    print("   • Interactive sensor controls")
    print("   • Real-time hygiene predictions")
    print("   • Demo scenarios (Clean/Moderate/Dirty)")
    print("   • Beautiful visualizations")
    print("   • Explainable AI insights")
    print("   • Analytics dashboard")
    print("\n⚡ Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening web browser...")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask app
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Trying alternative method...")
        subprocess.run([sys.executable, 'app.py'])

if __name__ == "__main__":
    main()