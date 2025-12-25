#!/usr/bin/env python3
"""
Test script for enhanced real-time updates system
Tests the complete workflow from login to cleaning completion
"""

import requests
import json
import time
import threading
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_CLEANER_EMAIL = "cleaner@example.com"
TEST_CLEANER_PASSWORD = "password123"

def test_login():
    """Test login functionality"""
    print("🔐 Testing login...")
    
    login_data = {
        "email": TEST_CLEANER_EMAIL,
        "password": TEST_CLEANER_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user', {})
            if token:
                print(f"✅ Login successful! Token: {token[:20]}...")
                print(f"   User: {user.get('name')} ({user.get('email')})")
                print(f"   Role: {user.get('role')}")
                return token
            else:
                print(f"❌ Login failed: No token received")
                print(f"   Response data: {data}")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_priority_toilets(token):
    """Test getting priority toilets"""
    print("\n🚻 Testing priority toilets...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/staff/priority-toilets", headers=headers)
        if response.status_code == 200:
            data = response.json()
            priority_toilets = data.get('priority_toilets', [])
            print(f"✅ Found {len(priority_toilets)} priority toilets")
            
            # Show first few toilets
            for i, toilet in enumerate(priority_toilets[:3]):
                print(f"   {i+1}. {toilet['name']} - Score: {toilet['hygiene_score']} - Status: {toilet['status']}")
            
            return priority_toilets
        else:
            print(f"❌ Failed to get priority toilets: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting priority toilets: {e}")
        return []

def test_start_cleaning(token, toilet_id):
    """Test starting cleaning process"""
    print(f"\n🧹 Testing start cleaning for toilet {toilet_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"toilet_id": toilet_id}
    
    try:
        response = requests.post(f"{BASE_URL}/api/staff/start-cleaning", headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cleaning started successfully!")
            print(f"   Message: {result.get('message')}")
            print(f"   Estimated completion: {result.get('toilet', {}).get('estimated_completion')}")
            return True
        else:
            print(f"❌ Failed to start cleaning: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting cleaning: {e}")
        return False

def test_get_updates(token):
    """Test getting real-time updates"""
    print("\n🔄 Testing real-time updates...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/staff/updates", headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Updates retrieved successfully!")
            print(f"   Has updates: {data.get('has_updates')}")
            print(f"   Has cleaning updates: {data.get('has_cleaning_updates')}")
            print(f"   Total updates: {data.get('total_updates')}")
            
            # Show urgent toilets
            urgent_toilets = data.get('new_urgent_toilets', [])
            if urgent_toilets:
                print(f"   🚨 New urgent toilets: {len(urgent_toilets)}")
                for toilet in urgent_toilets:
                    print(f"      - {toilet['icon']} {toilet['name']} (Score: {toilet['hygiene_score']})")
            
            # Show recent cleaning updates
            cleaning_updates = data.get('recent_cleaning_updates', [])
            if cleaning_updates:
                print(f"   🧹 Recent cleaning updates: {len(cleaning_updates)}")
                for update in cleaning_updates:
                    print(f"      - {update['type']}: {update['toilet_name']} - {update['time_ago']}")
                    if update['type'] == 'cleaned':
                        print(f"        New score: {update['new_score']}/100")
            
            return data
        else:
            print(f"❌ Failed to get updates: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
        return None

def test_complete_workflow():
    """Test the complete workflow"""
    print("🚀 Starting enhanced real-time updates test...\n")
    
    # Step 1: Login
    token = test_login()
    if not token:
        return False
    
    # Step 2: Get priority toilets
    priority_toilets = test_get_priority_toilets(token)
    if not priority_toilets:
        print("❌ No priority toilets available for testing")
        return False
    
    # Step 3: Get initial updates
    initial_updates = test_get_updates(token)
    
    # Step 4: Start cleaning a toilet
    test_toilet = priority_toilets[0]
    toilet_id = test_toilet['id']
    toilet_name = test_toilet['name']
    
    print(f"\n🎯 Selected toilet for testing: {toilet_name} (ID: {toilet_id})")
    
    if test_start_cleaning(token, toilet_id):
        print("\n⏳ Waiting 35 seconds for cleaning to complete...")
        time.sleep(35)
        
        # Step 5: Check updates after cleaning
        print("\n📊 Checking updates after cleaning completion...")
        final_updates = test_get_updates(token)
        
        if final_updates:
            cleaning_updates = final_updates.get('recent_cleaning_updates', [])
            cleaning_completed = any(update['type'] == 'cleaned' and update['toilet_id'] == toilet_id 
                                   for update in cleaning_updates)
            
            if cleaning_completed:
                print(f"✅ SUCCESS: Cleaning workflow completed for {toilet_name}!")
                return True
            else:
                print(f"⚠️  Cleaning may not have completed yet for {toilet_name}")
                return False
        else:
            print("❌ Failed to get final updates")
            return False
    else:
        print("❌ Failed to start cleaning")
        return False

def main():
    """Main test function"""
    print("🧪 Enhanced Real-Time Updates Test Suite")
    print("=" * 50)
    
    try:
        success = test_complete_workflow()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 ALL TESTS PASSED! Enhanced real-time updates are working correctly.")
            sys.exit(0)
        else:
            print("❌ Some tests failed. Please check the logs above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()