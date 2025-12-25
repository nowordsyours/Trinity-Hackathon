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

# Step 2: Get toilets data to get IDs
api_response = session.get(f"{base_url}/api/toilets")
if api_response.status_code == 200:
    toilets_data = api_response.json()
    
    # Test directions between first two toilets
    if len(toilets_data['toilets']) >= 2:
        from_toilet = toilets_data['toilets'][0]
        to_toilet = toilets_data['toilets'][1]
        
        print(f"Testing directions from {from_toilet['name']} to {to_toilet['name']}")
        
        # Test directions API
        directions_response = session.get(f"{base_url}/api/directions/{from_toilet['id']}/to/{to_toilet['id']}")
        print(f"Directions API status: {directions_response.status_code}")
        
        if directions_response.status_code == 200:
            directions_data = directions_response.json()
            print(f"Directions found: {directions_data.get('found', False)}")
            if directions_data.get('found'):
                print(f"Distance: {directions_data.get('distance', 'N/A')} meters")
                print(f"Duration: {directions_data.get('duration', 'N/A')} minutes")
                print(f"Path points: {len(directions_data.get('path', []))} coordinates")
            else:
                print("Using fallback path points from toilet data")
        else:
            print(f"Directions error: {directions_response.text}")

print("\nDirections functionality test completed!")