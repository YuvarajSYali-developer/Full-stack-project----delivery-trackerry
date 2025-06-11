import random
from faker import Faker
from sqlmodel import Session, SQLModel, create_engine, select
from app.database import engine, init_db
from app.schemas import User, Shipment, ShipmentCreate
from app.auth import get_password_hash
from app.logger import logger

fake = Faker()

def seed_users(session, n=5):
    """
    Seed users into the database.
    The first user will be a test user with known credentials.
    """
    logger.info(f"Seeding {n} users...")
    try:
        # First, check if test user exists
        existing_test_user = session.execute(
            select(User).where(User.username == "testuser")
        ).first()
        
        if not existing_test_user:
            # Create test user
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role="customer",
                phone="+1-555-0001",
                address="123 Test St, Test City, TC 12345",
                company="Test Company",
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(test_user)
            logger.info("Test user created successfully!")
        
        # Create additional random users
        for i in range(n - 1):
            username = fake.user_name()
            email = fake.email()
            password = "password123"
            full_name = fake.name()

            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role="customer",
                phone=fake.phone_number(),
                address=fake.address().replace('\n', ', '),
                company=fake.company(),
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(user)
            logger.info(f"Seeded user: {username}")
        
        session.commit()
        logger.info("Users seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding users: {str(e)}")
        raise

def seed_shipments(session, n=10):
    """
    Seed shipments into the database.
    """
    logger.info(f"Seeding {n} shipments...")
    try:
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]

        for _ in range(n):
            origin_city = random.choice(cities)
            destination_city = random.choice([c for c in cities if c != origin_city])

            shipment = Shipment(
                tracking_number=fake.unique.bothify(text='ABC######'),
                status=random.choice(["pending", "shipped", "delivered"]),
                priority="normal",
                origin_address=fake.street_address(),
                destination_address=fake.street_address(),
                origin_city=origin_city,
                destination_city=destination_city,
                origin_country="USA",
                destination_country="USA",
                weight=round(random.uniform(1, 100), 2),
                dimensions=f"{random.randint(10,50)}x{random.randint(10,50)}x{random.randint(5,30)}",
                declared_value=round(random.uniform(50, 1000), 2),
                insurance_required=random.choice([True, False]),
                fragile=random.choice([True, False]),
                description=fake.text(max_nb_chars=100)
            )
            session.add(shipment)
        session.commit()
        logger.info("Shipments seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding shipments: {str(e)}")
        raise

def seed_database():
    """
    Initialize and seed the database with test data.
    """
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully.")
        
        # Create a session and seed data
        with Session(engine) as session:
            seed_users(session)
            seed_shipments(session)
        
        logger.info("Database seeded successfully!")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        raise

if __name__ == "__main__":
    seed_database() 