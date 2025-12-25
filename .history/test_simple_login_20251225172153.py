#!/usr/bin/env python3
"""
Test script for simplified login system
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_login_system():
    """Test the simplified login system"""
    print("🧪 Testing Simplified Login System")
    print("=" * 50)
    
    # Test 1: Access simplified login page
    print("\n1️⃣ Testing simplified login page access...")
    try:
        response = requests.get(f"{BASE_URL}/simple-login")
        if response.status_code == 200:
            print("✅ Simplified login page accessible")
        else:
            print(f"❌ Login page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Login page error: {e}")
    
    # Test 2: Access simplified signup page
    print("\n2️⃣ Testing simplified signup page access...")
    try:
        response = requests.get(f"{BASE_URL}/simple-signup")
        if response.status_code == 200:
            print("✅ Simplified signup page accessible")
        else:
            print(f"❌ Signup page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Signup page error: {e}")
    
    # Test 3: Test admin login
    print("\n3️⃣ Testing admin login...")
    try:
        login_data = {
            'email': 'admin@example.com',
            'password': 'admin123'
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin login successful")
            print(f"   Message: {result.get('message')}")
            print(f"   User: {result.get('user', {}).get('name')}")
            print(f"   Role: {result.get('user', {}).get('role')}")
            print(f"   Redirect: {result.get('redirect_url')}")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Error: {response.json().get('error')}")
    except Exception as e:
        print(f"❌ Admin login error: {e}")
    
    # Test 4: Test staff login
    print("\n4️⃣ Testing staff login...")
    try:
        login_data = {
            'email': 'cleaner@example.com',
            'password': 'password123'
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Staff login successful")
            print(f"   Redirect: {result.get('redirect_url')}")
        else:
            print(f"❌ Staff login failed: {response.status_code}")
            if response.status_code == 401:
                print(f"   Error: {response.json().get('error')}")
    except Exception as e:
        print(f"❌ Staff login error: {e}")
    
    # Test 5: Test public user login
    print("\n5️⃣ Testing public user login...")
    try:
        login_data = {
            'email': 'user@example.com',
            'password': 'password123'
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Public user login successful")
            print(f"   Redirect: {result.get('redirect_url')}")
        else:
            print(f"❌ Public user login failed: {response.status_code}")
            if response.status_code == 401:
                print(f"   Error: {response.json().get('error')}")
    except Exception as e:
        print(f"❌ Public user login error: {e}")
    
    # Test 6: Test invalid login
    print("\n6️⃣ Testing invalid login...")
    try:
        login_data = {
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json=login_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 401:
            result = response.json()
            print("✅ Invalid login properly rejected")
            print(f"   Error: {result.get('error')}")
        else:
            print(f"❌ Invalid login test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid login test error: {e}")
    
    # Test 7: Test registration
    print("\n7️⃣ Testing user registration...")
    try:
        signup_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'name': 'Test User',
            'role': 'public'
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", 
                               json=signup_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User registration successful")
            print(f"   Message: {result.get('message')}")
            print(f"   User: {result.get('user', {}).get('name')}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.json().get('error')}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test 8: Test auth status
    print("\n8️⃣ Testing authentication status...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status")
        if response.status_code == 200:
            result = response.json()
            if result.get('authenticated'):
                print("✅ User is authenticated")
                print(f"   User: {result.get('user', {}).get('name')}")
                print(f"   Role: {result.get('user', {}).get('role')}")
            else:
                print("ℹ️  No user authenticated")
        else:
            print(f"❌ Auth status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth status error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Login system testing completed!")
    print(f"🌐 Access simplified login at: {BASE_URL}/simple-login")
    print(f"📝 Access simplified signup at: {BASE_URL}/simple-signup")

if __name__ == "__main__":
    test_login_system()