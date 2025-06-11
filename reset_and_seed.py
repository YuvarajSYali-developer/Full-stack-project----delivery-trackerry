#!/usr/bin/env python3
"""
Reset database and seed with test data
"""

import os
from sqlmodel import SQLModel, create_engine, Session
from app.database import engine
from app.schemas import User, Shipment
from app.auth import get_password_hash
from faker import Faker
import random

fake = Faker()

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    print("🗑️  Resetting database...")
    
    # Remove existing database file if it exists
    db_files = ["sqlite.db", "test.db"]
    for db_file in db_files:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"   Removed {db_file}")
    
    # Create all tables
    print("📋 Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")

def seed_basic_data():
    """Seed the database with basic test data"""
    print("🌱 Seeding database with test data...")
    
    with Session(engine) as session:
        # Create test users with different roles
        users_data = [
            {
                "username": "admin",
                "email": "admin@shipment.com",
                "full_name": "System Administrator",
                "role": "admin",
                "phone": "+1-555-0001",
                "address": "123 Admin St, Admin City, AC 12345",
                "company": "Shipment Management Corp",
                "password": "admin123"
            },
            {
                "username": "manager",
                "email": "manager@shipment.com", 
                "full_name": "Operations Manager",
                "role": "manager",
                "phone": "+1-555-0002",
                "address": "456 Manager Ave, Manager City, MC 23456",
                "company": "Shipment Management Corp",
                "password": "manager123"
            },
            {
                "username": "employee",
                "email": "employee@shipment.com",
                "full_name": "Warehouse Employee", 
                "role": "employee",
                "phone": "+1-555-0003",
                "address": "789 Employee Rd, Employee City, EC 34567",
                "company": "Shipment Management Corp",
                "password": "employee123"
            },
            {
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test Customer",
                "role": "customer",
                "phone": "+1-555-0004", 
                "address": "321 Customer Blvd, Customer City, CC 45678",
                "company": "Test Company Inc",
                "password": "password123"
            }
        ]
        
        # Create users
        for user_data in users_data:
            password = user_data.pop("password")
            hashed_password = get_password_hash(password)
            
            user = User(
                **user_data,
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(user)
            print(f"   Created user: {user.username} ({user.role})")
        
        # Create some sample shipments
        shipments_data = [
            {
                "tracking_number": "SHP001",
                "status": "pending",
                "priority": "normal",
                "origin_address": "123 Origin St",
                "destination_address": "456 Dest Ave",
                "origin_city": "New York",
                "destination_city": "Los Angeles",
                "origin_country": "USA",
                "destination_country": "USA",
                "weight": 5.5,
                "dimensions": "30x20x15",
                "declared_value": 150.0,
                "insurance_required": False,
                "fragile": False,
                "description": "Sample package",
                "customer_id": 4  # testuser
            },
            {
                "tracking_number": "SHP002", 
                "status": "in_transit",
                "priority": "high",
                "origin_address": "789 Start Rd",
                "destination_address": "321 End Blvd",
                "origin_city": "Chicago",
                "destination_city": "Miami",
                "origin_country": "USA",
                "destination_country": "USA", 
                "weight": 12.3,
                "dimensions": "40x30x25",
                "declared_value": 500.0,
                "insurance_required": True,
                "fragile": True,
                "description": "Fragile electronics",
                "customer_id": 4  # testuser
            }
        ]
        
        for shipment_data in shipments_data:
            shipment = Shipment(**shipment_data)
            session.add(shipment)
            print(f"   Created shipment: {shipment.tracking_number}")
        
        session.commit()
        print("✅ Database seeded successfully!")

def main():
    """Main function"""
    print("🚀 Database Reset and Seed Script")
    print("=" * 40)
    
    try:
        reset_database()
        seed_basic_data()
        
        print("\n🎉 Database reset and seeding completed!")
        print("\nTest Login Credentials:")
        print("  Admin:    admin / admin123")
        print("  Manager:  manager / manager123") 
        print("  Employee: employee / employee123")
        print("  Customer: testuser / password123")
        print("\n✅ Ready to start the server!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
