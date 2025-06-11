#!/usr/bin/env python3
"""
Quick start script to setup and test the application
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path.cwd()))

def setup_database():
    """Setup database with test user"""
    try:
        print("🔄 Setting up database...")
        
        from app.database import engine, init_db
        from app.schemas import User, Shipment
        from app.auth import get_password_hash
        from sqlmodel import Session, select
        
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
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(test_user)
            session.commit()
            print("✅ Test user created: testuser / password123")
            
            # Create sample shipments
            shipments = [
                Shipment(
                    tracking_number="ABC123456",
                    status="pending",
                    origin="New York",
                    destination="Los Angeles",
                    weight=5.5
                ),
                Shipment(
                    tracking_number="DEF789012",
                    status="shipped",
                    origin="Chicago",
                    destination="Miami",
                    weight=12.3
                ),
                Shipment(
                    tracking_number="GHI345678",
                    status="delivered",
                    origin="Seattle",
                    destination="Boston",
                    weight=8.7
                )
            ]
            
            for shipment in shipments:
                session.add(shipment)
            session.commit()
            print("✅ Sample shipments created")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test if all imports work"""
    try:
        print("🧪 Testing imports...")
        
        from app.main import app
        from app.database import engine
        from app.schemas import User, Shipment
        from app.auth import get_password_hash, verify_password
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 Quick Start - Shipment Management System")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your environment.")
        return
    
    # Setup database
    if not setup_database():
        print("\n❌ Database setup failed.")
        return
    
    print("\n🎉 Setup complete!")
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Start Backend Server:")
    print("   myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    print("2. Start Frontend Server (in new terminal):")
    print("   cd frontend")
    print("   npm run dev")
    print()
    print("3. Open Browser:")
    print("   http://localhost:5173 or http://localhost:5174")
    print()
    print("4. Login Credentials:")
    print("   Username: testuser")
    print("   Password: password123")
    print()
    print("=" * 60)
    print("🔧 TROUBLESHOOTING:")
    print("- If you get CORS errors, make sure frontend port matches backend CORS config")
    print("- If login fails, check backend logs for detailed error messages")
    print("- If 500 errors persist, restart both servers")
    print("=" * 60)

if __name__ == "__main__":
    main()
