#!/usr/bin/env python3
"""
Reset database and create test user
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path.cwd()))

def reset_database():
    try:
        from app.database import engine, init_db
        from app.schemas import User
        from app.auth import get_password_hash
        from sqlmodel import Session, select, SQLModel
        
        print("🔄 Resetting database...")
        
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
            # Check if user already exists
            existing_user = session.exec(
                select(User).where(User.username == "testuser")
            ).first()
            
            if existing_user:
                print("ℹ️  Test user already exists")
            else:
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
                print(f"   Email: test@example.com")
                print(f"   User ID: {test_user.id}")
        
        # Seed some sample shipments
        from app.seed import seed_shipments
        with Session(engine) as session:
            seed_shipments(session, 5)
            print("✅ Sample shipments created")
        
        print("\n🎉 Database reset complete!")
        print("\nTest credentials:")
        print("Username: testuser")
        print("Password: password123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_user():
    """Verify the test user can be found and password verified"""
    try:
        from app.database import engine
        from app.schemas import User
        from app.auth import verify_password
        from sqlmodel import Session, select
        
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.username == "testuser")
            ).first()
            
            if not user:
                print("❌ Test user not found in database")
                return False
            
            print(f"✅ Test user found: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Active: {user.is_active}")
            
            # Test password verification
            if verify_password("password123", user.hashed_password):
                print("✅ Password verification works")
                return True
            else:
                print("❌ Password verification failed")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Database Reset Tool")
    print("=" * 50)
    
    if reset_database():
        print("\n🔍 Verifying test user...")
        if verify_user():
            print("\n✅ Everything looks good!")
            print("\nNext steps:")
            print("1. Start backend: myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
            print("2. Start frontend: cd frontend && npm run dev")
            print("3. Login with: testuser / password123")
        else:
            print("\n❌ User verification failed")
    else:
        print("\n❌ Database reset failed")
