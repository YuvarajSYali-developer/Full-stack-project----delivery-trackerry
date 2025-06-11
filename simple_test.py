#!/usr/bin/env python3
"""
Simple test to check what's wrong
"""

print("Testing imports...")

try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path.cwd()))
    print("✅ Basic imports OK")
    
    from sqlmodel import Session, select
    print("✅ SQLModel imports OK")
    
    from app.database import engine, init_db
    print("✅ Database imports OK")
    
    from app.schemas import User
    print("✅ Schema imports OK")
    
    from app.auth import get_password_hash, verify_password
    print("✅ Auth imports OK")
    
    # Test database initialization
    init_db()
    print("✅ Database initialization OK")
    
    # Test user creation
    with Session(engine) as session:
        # Check if user exists
        stmt = select(User).where(User.username == "testuser")
        existing_user = session.exec(stmt).first()
        
        if existing_user:
            print("✅ Test user already exists")
        else:
            # Create user
            user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(user)
            session.commit()
            print("✅ Test user created")
    
    print("\n🎉 All basic tests passed!")
    print("\nNow try starting the backend:")
    print("myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
