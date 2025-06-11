#!/usr/bin/env python3
"""
Quick test to verify backend is working
"""

import requests
import json

def test_backend():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend API...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure to run: myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        return False
    
    # Test 2: Login
    try:
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        response = requests.post(
            f"{base_url}/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login endpoint working")
            print(f"   Token type: {token_data.get('token_type')}")
            
            # Test 3: Protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            shipments_response = requests.get(f"{base_url}/shipments/", headers=headers)
            
            if shipments_response.status_code == 200:
                shipments = shipments_response.json()
                print(f"✅ Shipments endpoint working ({len(shipments)} shipments found)")
                return True
            else:
                print("❌ Shipments endpoint not working")
                print(f"   Status: {shipments_response.status_code}")
                return False
        else:
            print("❌ Login failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

if __name__ == "__main__":
    success = test_backend()
    if success:
        print("\n🎉 Backend is working correctly!")
        print("\nNext steps:")
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Open browser to http://localhost:5173")
        print("3. Login with: testuser / password123")
    else:
        print("\n❌ Backend has issues. Please check the server logs.")
