#!/usr/bin/env python3
"""
Simple login test
"""

import requests
import json

def test_login():
    """Test login with simple approach"""
    print("🔐 Testing Login...")
    
    url = "http://localhost:8001/token"
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"Token: {token_data.get('access_token', 'No token')[:50]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the server is running on http://localhost:8001")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint"""
    if not token:
        print("❌ No token available for testing protected endpoint")
        return
    
    print("\n🔒 Testing Protected Endpoint...")
    
    url = "http://localhost:8001/users/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Protected endpoint access successful!")
            print(f"User: {user_data.get('username')} ({user_data.get('email')})")
        else:
            print(f"❌ Protected endpoint failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")

if __name__ == "__main__":
    print("🚀 Simple Login Test")
    print("=" * 30)
    
    token = test_login()
    test_protected_endpoint(token)
    
    print("\n✅ Test completed!")
