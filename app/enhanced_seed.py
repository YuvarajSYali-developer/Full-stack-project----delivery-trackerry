import random
from faker import Faker
from sqlmodel import Session, SQLModel, create_engine, select
from app.database import engine, init_db
from app.schemas import (
    User, Shipment, TrackingHistory, Notification, Document,
    UserRole, ShipmentStatus, ShipmentPriority, NotificationType, NotificationStatus, DocumentType
)
from app.auth import get_password_hash
from app.logger import logger
from datetime import datetime, timedelta
import uuid

fake = Faker()

def seed_users(session, n=20):
    """Seed users with different roles."""
    logger.info(f"Seeding {n} users with various roles...")
    try:
        # Check if admin user exists
        existing_admin = session.exec(
            select(User).where(User.username == "admin")
        ).first()
        
        if not existing_admin:
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@shipment.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                phone="+1-555-0001",
                address="123 Admin St, Admin City, AC 12345",
                company="Shipment Management Corp",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            session.add(admin_user)
            logger.info("Admin user created successfully!")
        
        # Check if manager user exists
        existing_manager = session.exec(
            select(User).where(User.username == "manager")
        ).first()
        
        if not existing_manager:
            # Create manager user
            manager_user = User(
                username="manager",
                email="manager@shipment.com",
                full_name="Operations Manager",
                role=UserRole.MANAGER,
                phone="+1-555-0002",
                address="456 Manager Ave, Manager City, MC 23456",
                company="Shipment Management Corp",
                hashed_password=get_password_hash("manager123"),
                is_active=True
            )
            session.add(manager_user)
            logger.info("Manager user created successfully!")
        
        # Check if employee user exists
        existing_employee = session.exec(
            select(User).where(User.username == "employee")
        ).first()
        
        if not existing_employee:
            # Create employee user
            employee_user = User(
                username="employee",
                email="employee@shipment.com",
                full_name="Warehouse Employee",
                role=UserRole.EMPLOYEE,
                phone="+1-555-0003",
                address="789 Employee Rd, Employee City, EC 34567",
                company="Shipment Management Corp",
                hashed_password=get_password_hash("employee123"),
                is_active=True
            )
            session.add(employee_user)
            logger.info("Employee user created successfully!")
        
        # Check if test customer exists
        existing_customer = session.exec(
            select(User).where(User.username == "testuser")
        ).first()
        
        if not existing_customer:
            # Create test customer
            customer_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test Customer",
                role=UserRole.CUSTOMER,
                phone="+1-555-0004",
                address="321 Customer Blvd, Customer City, CC 45678",
                company="Test Company Inc",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(customer_user)
            logger.info("Test customer created successfully!")
        
        # Create additional random users
        roles = [UserRole.CUSTOMER, UserRole.EMPLOYEE, UserRole.CUSTOMER, UserRole.CUSTOMER]  # More customers
        for i in range(n - 4):
            username = fake.user_name()
            email = fake.email()
            password = "password123"
            full_name = fake.name()
            role = random.choice(roles)
            phone = fake.phone_number()
            address = fake.address().replace('\n', ', ')
            company = fake.company() if role == UserRole.CUSTOMER else "Shipment Management Corp"

            # Check if username already exists
            existing = session.exec(select(User).where(User.username == username)).first()
            if existing:
                continue

            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                phone=phone,
                address=address,
                company=company,
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(user)
            logger.info(f"Seeded user: {username} with role: {role}")
        
        session.commit()
        logger.info("Users seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding users: {str(e)}")
        raise

def seed_shipments(session, n=50):
    """Seed shipments with realistic data."""
    logger.info(f"Seeding {n} shipments...")
    try:
        # Get all customers for assigning shipments
        customers = session.exec(select(User).where(User.role == UserRole.CUSTOMER)).all()
        if not customers:
            logger.warning("No customers found, creating shipments without customer assignment")
        
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
            "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
            "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle"
        ]
        
        statuses = list(ShipmentStatus)
        priorities = list(ShipmentPriority)
        
        for i in range(n):
            tracking_number = f"SHP{uuid.uuid4().hex[:8].upper()}"
            
            # Check if tracking number already exists
            existing = session.exec(select(Shipment).where(Shipment.tracking_number == tracking_number)).first()
            if existing:
                continue
            
            origin_city = random.choice(cities)
            destination_city = random.choice([c for c in cities if c != origin_city])
            
            shipment = Shipment(
                tracking_number=tracking_number,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                origin_address=fake.street_address(),
                destination_address=fake.street_address(),
                origin_city=origin_city,
                destination_city=destination_city,
                origin_country="USA",
                destination_country="USA",
                weight=round(random.uniform(0.5, 100.0), 2),
                dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)}",
                declared_value=round(random.uniform(50.0, 5000.0), 2),
                insurance_required=random.choice([True, False]),
                fragile=random.choice([True, False]),
                description=fake.text(max_nb_chars=100),
                special_instructions=fake.text(max_nb_chars=50) if random.choice([True, False]) else None,
                estimated_delivery_date=fake.date_time_between(start_date='+1d', end_date='+30d'),
                customer_id=random.choice(customers).id if customers else None,
                created_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            session.add(shipment)
        
        session.commit()
        logger.info("Shipments seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding shipments: {str(e)}")
        raise

def seed_tracking_history(session, n=200):
    """Seed tracking history for shipments."""
    logger.info(f"Seeding {n} tracking history entries...")
    try:
        shipments = session.exec(select(Shipment)).all()
        if not shipments:
            logger.warning("No shipments found, skipping tracking history seeding")
            return
        
        locations = [
            "Origin Facility", "Sorting Center", "Transit Hub", "Local Facility",
            "Out for Delivery", "Delivery Truck", "Customer Location", "Return Center"
        ]
        
        for i in range(n):
            shipment = random.choice(shipments)
            status = random.choice(list(ShipmentStatus))
            location = random.choice(locations)
            
            tracking = TrackingHistory(
                shipment_id=shipment.id,
                status=status,
                location=location,
                description=f"Package {status.value} at {location}",
                timestamp=fake.date_time_between(start_date=shipment.created_at, end_date='now')
            )
            session.add(tracking)
        
        session.commit()
        logger.info("Tracking history seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding tracking history: {str(e)}")
        raise

def seed_notifications(session, n=100):
    """Seed notifications for users."""
    logger.info(f"Seeding {n} notifications...")
    try:
        users = session.exec(select(User)).all()
        if not users:
            logger.warning("No users found, skipping notifications seeding")
            return
        
        notification_types = list(NotificationType)
        statuses = list(NotificationStatus)
        
        messages = [
            "Your shipment has been picked up",
            "Your package is out for delivery",
            "Delivery completed successfully",
            "Shipment delayed due to weather",
            "Package requires signature",
            "Delivery attempt failed",
            "Package returned to sender",
            "New shipment created"
        ]
        
        for i in range(n):
            user = random.choice(users)
            message = random.choice(messages)
            
            notification = Notification(
                user_id=user.id,
                title="Shipment Update",
                message=message,
                notification_type=random.choice(notification_types),
                status=random.choice(statuses),
                created_at=fake.date_time_between(start_date='-7d', end_date='now'),
                sent_at=fake.date_time_between(start_date='-7d', end_date='now') if random.choice([True, False]) else None,
                read_at=fake.date_time_between(start_date='-7d', end_date='now') if random.choice([True, False]) else None
            )
            session.add(notification)
        
        session.commit()
        logger.info("Notifications seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding notifications: {str(e)}")
        raise

def seed_database():
    """Initialize and seed the database with comprehensive test data."""
    try:
        logger.info("Starting enhanced database initialization...")
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
        
        # Create a session and seed data
        with Session(engine) as session:
            seed_users(session, 20)
            seed_shipments(session, 50)
            seed_tracking_history(session, 200)
            seed_notifications(session, 100)
        
        logger.info("Enhanced database seeded successfully!")
        logger.info("Default login credentials:")
        logger.info("Admin: admin / admin123")
        logger.info("Manager: manager / manager123")
        logger.info("Employee: employee / employee123")
        logger.info("Customer: testuser / password123")
        
    except Exception as e:
        logger.error(f"Error during enhanced database initialization: {str(e)}")
        raise

if __name__ == "__main__":
    seed_database()
