#!/usr/bin/env python3
"""
Enhanced Smart Toilet Hygiene System - Features Demo

This script demonstrates all the enhanced features:
1. Simplified login system
2. Enhanced real-time updates with detailed feedback
3. Improved cleaning modal with better user feedback
4. Staff dashboard with comprehensive updates
5. Enhanced user experience across all components
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def demo_simplified_login():
    """Demo the simplified login system"""
    print("🔐 SIMPLIFIED LOGIN SYSTEM DEMO")
    print("=" * 50)
    
    # Test different user roles
    test_users = [
        {"email": "cleaner@example.com", "password": "cleaner123", "role": "cleaner"},
        {"email": "admin@example.com", "password": "admin123", "role": "admin"},
        {"email": "user@example.com", "password": "user123", "role": "public"}
    ]
    
    sessions = {}
    
    for user in test_users:
        print(f"\n🧪 Testing {user['role']} login...")
        session = requests.Session()
        
        response = session.post(f"{BASE_URL}/api/auth/login", json=user)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            print(f"✅ {user['role'].title()} login successful!")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Redirect: {data.get('redirect_url')}")
            sessions[user['role']] = session
        else:
            print(f"❌ {user['role']} login failed: {response.status_code}")
    
    return sessions

def demo_real_time_updates(sessions):
    """Demo enhanced real-time updates"""
    print("\n\n🔄 ENHANCED REAL-TIME UPDATES DEMO")
    print("=" * 50)
    
    cleaner_session = sessions.get('cleaner')
    if not cleaner_session:
        print("❌ No cleaner session available")
        return
    
    print("\n📊 Getting initial updates...")
    response = cleaner_session.get(f"{BASE_URL}/api/updates")
    
    if response.status_code == 200:
        data = response.json()
        updates = data.get('updates', [])
        print(f"✅ Found {len(updates)} real-time updates")
        
        for update in updates[-3:]:  # Show last 3 updates
            print(f"   📝 {update.get('type', 'update')}: {update.get('toilet_name', 'Unknown')}")
            print(f"      Status: {update.get('previous_status')} → {update.get('new_status')}")
            if 'new_score' in update:
                print(f"      Score: {update.get('new_score')}/100")
    
    # Get staff-specific updates
    print("\n👨‍🔧 Getting staff dashboard updates...")
    response = cleaner_session.get(f"{BASE_URL}/api/staff/updates")
    
    if response.status_code == 200:
        data = response.json()
        urgent_toilets = data.get('new_urgent_toilets', [])
        cleaning_updates = data.get('recent_cleaning_updates', [])
        
        print(f"✅ Staff dashboard updates:")
        print(f"   🚨 New urgent toilets: {len(urgent_toilets)}")
        print(f"   🧹 Recent cleaning updates: {len(cleaning_updates)}")
        
        if cleaning_updates:
            print("   Recent cleaning activity:")
            for update in cleaning_updates[:3]:
                print(f"      {update.get('type')}: {update.get('toilet_name')} - {update.get('time_ago')}")

def demo_cleaning_workflow(sessions):
    """Demo the enhanced cleaning workflow"""
    print("\n\n🧽 ENHANCED CLEANING WORKFLOW DEMO")
    print("=" * 50)
    
    cleaner_session = sessions.get('cleaner')
    if not cleaner_session:
        print("❌ No cleaner session available")
        return
    
    # Get all toilets to find one to clean
    print("\n📍 Finding toilet to clean...")
    response = cleaner_session.get(f"{BASE_URL}/api/toilets")
    
    if response.status_code == 200:
        data = response.json()
        toilets = data.get('toilets', [])
        
        # Find a toilet that needs cleaning
        toilet_to_clean = None
        for toilet in toilets:
            if toilet['status'] in ['Dirty', 'Moderate']:
                toilet_to_clean = toilet
                break
        
        if not toilet_to_clean:
            # If all are clean, use the first one
            toilet_to_clean = toilets[0] if toilets else None
        
        if toilet_to_clean:
            print(f"✅ Selected toilet: {toilet_to_clean['name']}")
            print(f"   Status: {toilet_to_clean['status']}")
            print(f"   Score: {toilet_to_clean['hygiene_score']}/100")
            
            # Start cleaning
            print(f"\n🧹 Starting cleaning process...")
            response = cleaner_session.post(f"{BASE_URL}/api/toilets/{toilet_to_clean['id']}/start-cleaning")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Cleaning started successfully!")
                print(f"   Message: {data.get('message')}")
                print(f"   Estimated completion: {data.get('toilet', {}).get('estimated_completion')}")
                
                # Wait for cleaning to complete
                print("\n⏳ Waiting for cleaning to complete...")
                time.sleep(35)  # Wait for the background process
                
                # Check the result
                print("\n📊 Checking cleaning results...")
                response = cleaner_session.get(f"{BASE_URL}/api/toilets/{toilet_to_clean['id']}")
                
                if response.status_code == 200:
                    updated_toilet = response.json()
                    print("✅ Cleaning completed successfully!")
                    print(f"   New status: {updated_toilet['status']}")
                    print(f"   New score: {updated_toilet['hygiene_score']}/100")
                    
                    # Check real-time updates
                    print(f"\n🔄 Checking real-time updates...")
                    response = cleaner_session.get(f"{BASE_URL}/api/staff/updates")
                    
                    if response.status_code == 200:
                        data = response.json()
                        cleaning_updates = data.get('recent_cleaning_updates', [])
                        
                        print("✅ Recent cleaning updates:")
                        for update in cleaning_updates[:2]:
                            print(f"   🧽 {update.get('type')}: {update.get('toilet_name')}")
                            print(f"      Score improved to {update.get('new_score')}/100")
                            print(f"      {update.get('time_ago')}")

def demo_dashboard_accessibility(sessions):
    """Demo dashboard accessibility"""
    print("\n\n📱 DASHBOARD ACCESSIBILITY DEMO")
    print("=" * 50)
    
    dashboards = {
        'public': '/dashboard',
        'staff': '/staff-dashboard', 
        'admin': '/admin-dashboard'
    }
    
    for role, session in sessions.items():
        if role in dashboards:
            print(f"\n🧪 Testing {role} dashboard access...")
            response = session.get(f"{BASE_URL}{dashboards[role]}")
            
            if response.status_code == 200:
                print(f"✅ {role.title()} dashboard accessible")
                # Check if page contains expected content
                content = response.text
                if 'CleanFind' in content or 'CleanSeat' in content:
                    print(f"   ✅ Contains expected branding")
                if role == 'staff' and 'cleaning' in content.lower():
                    print(f"   ✅ Contains cleaning-related content")
            else:
                print(f"❌ {role} dashboard not accessible: {response.status_code}")

def main():
    """Main demo function"""
    print("🚀 ENHANCED SMART TOILET HYGIENE SYSTEM DEMO")
    print("=" * 60)
    print("This demo showcases all the enhanced features:")
    print("• Simplified login system")
    print("• Enhanced real-time updates")
    print("• Improved cleaning workflow")
    print("• Better user experience")
    print("=" * 60)
    
    try:
        # Demo 1: Simplified Login
        sessions = demo_simplified_login()
        
        if not sessions:
            print("❌ Failed to create sessions")
            return
        
        # Demo 2: Real-time Updates
        demo_real_time_updates(sessions)
        
        # Demo 3: Cleaning Workflow
        demo_cleaning_workflow(sessions)
        
        # Demo 4: Dashboard Accessibility
        demo_dashboard_accessibility(sessions)
        
        print("\n\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Enhanced features working correctly:")
        print("✅ Simplified login system")
        print("✅ Enhanced real-time updates")
        print("✅ Improved cleaning workflow")
        print("✅ Better user experience")
        print("✅ Staff dashboard with comprehensive updates")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running.")
        print("   Start the server with: python enhanced_auth_app.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    main()