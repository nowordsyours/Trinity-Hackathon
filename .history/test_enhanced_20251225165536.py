import requests
import json

# Base URL
base_url = "http://localhost:5000"

# Step 1: Login to get session
login_data = {
    "email": "user1",
    "password": "password123"
}

# Create a session to maintain cookies
session = requests.Session()

# Login
login_response = session.post(f"{base_url}/api/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")
print(f"Login response: {login_response.text}")

# Step 2: Access enhanced dashboard
enhanced_response = session.get(f"{base_url}/enhanced")
print(f"\nEnhanced dashboard status: {enhanced_response.status_code}")
print(f"Enhanced dashboard content length: {len(enhanced_response.text)}")

# Step 3: Test API endpoints
api_response = session.get(f"{base_url}/api/toilets")
print(f"\nAPI toilets status: {api_response.status_code}")
if api_response.status_code == 200:
    toilets_data = api_response.json()
    print(f"Toilets count: {toilets_data['total']}")
    print(f"Summary: {toilets_data['summary']}")
else:
    print(f"API error: {api_response.text}")