#!/usr/bin/env python3
"""
Test script to verify authentication fix and enhanced features
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_login():
    """Test login functionality"""
    print("Testing login functionality...")
    
    # Test login with correct credentials
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"Access token: {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on port 8001")
        return None
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoints"""
    print("\nTesting protected endpoints...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test getting current user
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Protected endpoint access successful!")
            print(f"Current user: {user_data['username']} ({user_data['email']})")
            return True
        else:
            print(f"❌ Protected endpoint access failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")
        return False

def test_shipments(token):
    """Test shipment endpoints"""
    print("\nTesting shipment endpoints...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test getting shipments
        response = requests.get(f"{BASE_URL}/shipments/", headers=headers)
        
        if response.status_code == 200:
            shipments = response.json()
            print(f"✅ Retrieved {len(shipments)} shipments")
            
            if shipments:
                print(f"Sample shipment: {shipments[0]['tracking_number']} - {shipments[0]['status']}")
            
            return True
        else:
            print(f"❌ Shipments retrieval failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving shipments: {e}")
        return False

def test_create_shipment(token):
    """Test creating a new shipment"""
    print("\nTesting shipment creation...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    shipment_data = {
        "tracking_number": f"TEST{int(time.time())}",
        "status": "pending",
        "origin": "New York",
        "destination": "Los Angeles",
        "weight": 5.5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/shipments/",
            json=shipment_data,
            headers=headers
        )
        
        if response.status_code == 200:
            created_shipment = response.json()
            print("✅ Shipment created successfully!")
            print(f"Created shipment: {created_shipment['tracking_number']}")
            return created_shipment['id']
        else:
            print(f"❌ Shipment creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating shipment: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting authentication and API tests...\n")
    
    # Test login
    token = test_login()
    if not token:
        print("\n❌ Login test failed. Cannot proceed with other tests.")
        return
    
    # Test protected endpoints
    if not test_protected_endpoint(token):
        print("\n❌ Protected endpoint test failed.")
        return
    
    # Test shipments
    if not test_shipments(token):
        print("\n❌ Shipments test failed.")
        return
    
    # Test shipment creation
    shipment_id = test_create_shipment(token)
    if shipment_id:
        print(f"\n✅ All tests passed! Created shipment ID: {shipment_id}")
    else:
        print("\n⚠️ Most tests passed, but shipment creation failed.")
    
    print("\n🎉 Authentication fix verification complete!")

if __name__ == "__main__":
    main()
