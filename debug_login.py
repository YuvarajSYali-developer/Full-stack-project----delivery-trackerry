#!/usr/bin/env python3
"""
Debug login issue
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path.cwd()))

def test_database_connection():
    """Test database connection and user lookup"""
    try:
        from app.database import engine, get_db
        from app.schemas import User
        from app.auth import get_password_hash, verify_password
        from sqlmodel import Session, select
        
        print("🔍 Testing database connection...")
        
        with Session(engine) as session:
            # Check if testuser exists
            stmt = select(User).where(User.username == "testuser")
            user = session.exec(stmt).first()
            
            if user:
                print("✅ Test user found in database")
                print(f"   Username: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   Active: {user.is_active}")
                print(f"   Password hash: {user.hashed_password[:20]}...")
                
                # Test password verification
                if verify_password("password123", user.hashed_password):
                    print("✅ Password verification works")
                else:
                    print("❌ Password verification failed")
                    
                return True
            else:
                print("❌ Test user not found in database")
                print("Creating test user...")
                
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
                print("✅ Test user created")
                return True
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_endpoint():
    """Test the login endpoint directly"""
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        print("\n🧪 Testing login endpoint...")
        
        client = TestClient(app)
        
        # Test login
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login endpoint works")
            return True
        else:
            print("❌ Login endpoint failed")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Login Debug Tool")
    print("=" * 40)
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database test failed")
        return
    
    # Test login endpoint
    if not test_login_endpoint():
        print("\n❌ Login endpoint test failed")
        return
    
    print("\n🎉 All tests passed!")
    print("\nIf you're still getting 500 errors, check:")
    print("1. Backend server logs")
    print("2. Make sure backend is running on port 8000")
    print("3. Try restarting the backend server")

if __name__ == "__main__":
    main()
