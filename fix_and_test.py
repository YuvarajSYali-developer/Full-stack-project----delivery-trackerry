#!/usr/bin/env python3
"""
Complete fix and test script for the shipment management system
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path.cwd()))

def reset_and_setup_database():
    """Reset database and create test user"""
    try:
        from app.database import engine, init_db
        from app.schemas import User, Shipment
        from app.auth import get_password_hash
        from sqlmodel import Session, select, SQLModel
        
        print("🔄 Setting up database...")
        
        # Remove existing database
        db_path = Path("sqlite.db")
        if db_path.exists():
            db_path.unlink()
            print("✅ Removed existing database")
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Create test user
        with Session(engine) as session:
            # Create test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            print("✅ Test user created successfully")
            print(f"   Username: testuser")
            print(f"   Password: password123")
            print(f"   User ID: {test_user.id}")
            
            # Create sample shipments
            sample_shipments = [
                {
                    "tracking_number": "ABC123456",
                    "status": "pending",
                    "origin": "New York",
                    "destination": "Los Angeles",
                    "weight": 5.5
                },
                {
                    "tracking_number": "DEF789012",
                    "status": "shipped",
                    "origin": "Chicago",
                    "destination": "Miami",
                    "weight": 12.3
                },
                {
                    "tracking_number": "GHI345678",
                    "status": "delivered",
                    "origin": "Seattle",
                    "destination": "Boston",
                    "weight": 8.7
                }
            ]
            
            for shipment_data in sample_shipments:
                shipment = Shipment(**shipment_data)
                session.add(shipment)
            
            session.commit()
            print("✅ Sample shipments created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """Test backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Backend API...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Please start backend: myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend server timeout")
        return False
    
    # Test 2: Login
    try:
        login_data = "username=testuser&password=password123"
        
        response = requests.post(
            f"{base_url}/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login endpoint working")
            print(f"   Token type: {token_data.get('token_type')}")
            
            # Test 3: Protected endpoint
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            shipments_response = requests.get(f"{base_url}/shipments/", headers=headers, timeout=10)
            
            if shipments_response.status_code == 200:
                shipments = shipments_response.json()
                print(f"✅ Shipments endpoint working ({len(shipments)} shipments found)")
                return True
            else:
                print("❌ Shipments endpoint not working")
                print(f"   Status: {shipments_response.status_code}")
                print(f"   Response: {shipments_response.text}")
                return False
        else:
            print("❌ Login failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    print("🔧 Shipment Management System - Fix & Test Tool")
    print("=" * 60)
    
    # Step 1: Setup database
    if not reset_and_setup_database():
        print("\n❌ Database setup failed")
        return False
    
    print("\n✅ Database setup complete!")
    print("\nNext steps:")
    print("1. Start backend: myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
    print("2. Run this script again to test the API")
    print("3. Start frontend: cd frontend && npm run dev")
    print("4. Open browser to http://localhost:5173")
    print("5. Login with: testuser / password123")
    
    # Ask if user wants to test API
    print("\n" + "=" * 60)
    test_api = input("Do you want to test the API now? (y/n): ").lower().strip()
    
    if test_api == 'y':
        if test_backend_api():
            print("\n🎉 All tests passed! The system is working correctly.")
        else:
            print("\n❌ API tests failed. Please check the backend server.")
    
    return True

if __name__ == "__main__":
    main()
