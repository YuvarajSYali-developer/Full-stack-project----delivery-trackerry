#!/usr/bin/env python3
"""
Simple database setup
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

def main():
    try:
        print("Setting up database...")
        
        from app.database import engine, init_db
        from app.schemas import User, Shipment
        from app.auth import get_password_hash
        from sqlmodel import Session
        
        # Remove existing database
        db_path = Path("sqlite.db")
        if db_path.exists():
            db_path.unlink()
            print("Removed existing database")
        
        # Initialize database
        init_db()
        print("Database initialized")
        
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
            print("Test user created: testuser / password123")
            
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
                )
            ]
            
            for shipment in shipments:
                session.add(shipment)
            session.commit()
            print("Sample shipments created")
        
        print("Database setup complete!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
