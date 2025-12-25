#!/usr/bin/env python3
"""
Dual Interface Startup Script
Starts both Public Interface (Port 5001) and Staff Interface (Port 5002)
"""

import subprocess
import time
import sys
import os
from threading import Thread
import signal

def run_public_interface():
    """Run the public interface Flask application"""
    print("🚀 Starting Public Interface on port 5001...")
    try:
        subprocess.run([
            sys.executable, 'public_app.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n🛑 Public Interface stopped")
    except Exception as e:
        print(f"❌ Public Interface error: {e}")

def run_staff_interface():
    """Run the staff interface Flask application"""
    print("🧹 Starting Staff Interface on port 5002...")
    try:
        subprocess.run([
            sys.executable, 'staff_app.py'
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\n🛑 Staff Interface stopped")
    except Exception as e:
        print(f"❌ Staff Interface error: {e}")

def main():
    """Main function to start both interfaces"""
    print("🌟 Starting Dual Interface System")
    print("=" * 50)
    print("📍 Public Interface: http://localhost:5001/dashboard")
    print("🔐 Staff Interface: http://localhost:5002/login")
    print("🔄 Real-time sync enabled between interfaces")
    print("=" * 50)
    print()
    
    # Create threads for both interfaces
    public_thread = Thread(target=run_public_interface, daemon=True)
    staff_thread = Thread(target=run_staff_interface, daemon=True)
    
    # Start both threads
    public_thread.start()
    staff_thread.start()
    
    print("✅ Both interfaces are starting...")
    print("⏰ Press Ctrl+C to stop both interfaces")
    print()
    
    try:
        # Wait for both threads
        public_thread.join()
        staff_thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping both interfaces...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == '__main__':
    main()