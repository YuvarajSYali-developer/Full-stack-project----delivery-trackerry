#!/usr/bin/env python3
"""
Direct test of login functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

def test_direct_login():
    try:
        print("Testing direct login...")
        
        # Import everything we need
        from app.database import engine, init_db, get_db
        from app.schemas import User
        from app.auth import get_password_hash, verify_password
        from sqlmodel import Session, select
        from fastapi.security import OAuth2PasswordRequestForm
        
        # Initialize database
        init_db()
        
        # Create test user if not exists
        with Session(engine) as session:
            # Check if user exists
            user = session.exec(select(User).where(User.username == "testuser")).first()
            
            if not user:
                print("Creating test user...")
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
                user = test_user
                print("Test user created")
            else:
                print("Test user already exists")
            
            print(f"User: {user.username}")
            print(f"Email: {user.email}")
            print(f"Active: {user.is_active}")
            print(f"Password hash: {user.hashed_password[:20]}...")
            
            # Test password verification
            if verify_password("password123", user.hashed_password):
                print("✅ Password verification works!")
            else:
                print("❌ Password verification failed!")
                return False
            
            # Test the actual login logic
            print("\nTesting login logic...")
            
            # Simulate form data
            class MockFormData:
                def __init__(self, username, password):
                    self.username = username
                    self.password = password
            
            form_data = MockFormData("testuser", "password123")
            
            # Test user lookup
            stmt = select(User).where(User.username == form_data.username)
            found_user = session.exec(stmt).first()
            
            if found_user:
                print("✅ User lookup works!")
                print(f"Found user: {found_user.username}")
                
                # Test password verification
                if verify_password(form_data.password, found_user.hashed_password):
                    print("✅ Password verification in login flow works!")
                    
                    # Test token creation
                    from app.auth import create_access_token
                    from datetime import timedelta
                    from app.config import get_settings
                    
                    settings = get_settings()
                    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": found_user.username}, expires_delta=access_token_expires
                    )
                    
                    print("✅ Token creation works!")
                    print(f"Token: {access_token[:50]}...")
                    
                    return True
                else:
                    print("❌ Password verification in login flow failed!")
                    return False
            else:
                print("❌ User lookup failed!")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_direct_login():
        print("\n🎉 All login components work!")
        print("The issue might be in the FastAPI endpoint or server setup.")
    else:
        print("\n❌ Login components have issues.")
