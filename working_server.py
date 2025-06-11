#!/usr/bin/env python3
"""
Enhanced Shipment Management API Server
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine, select, Field, or_, and_
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
from datetime import datetime, timedelta, date
from enum import Enum
import random
import uuid
from pydantic import BaseModel

# Database setup
DATABASE_URL = "sqlite:///./indian_shipment.db"
engine = create_engine(DATABASE_URL, echo=False)

# Enums
class ShipmentStatus(str, Enum):
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"

class ShipmentPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CUSTOMER = "customer"

# Enhanced User model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    hashed_password: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

# Customer model
class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = None
    company: Optional[str] = None
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None
    status: str = "active"  # active, inactive, suspended
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_shipments: int = 0
    total_value: float = 0.0

# Enhanced Shipment model
class Shipment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    customer_id: Optional[int] = Field(foreign_key="customer.id")

    # Status and Priority
    status: ShipmentStatus = ShipmentStatus.PENDING
    priority: ShipmentPriority = ShipmentPriority.NORMAL

    # Origin and Destination
    origin_address: str
    origin_city: str
    origin_country: str
    origin_postal_code: Optional[str] = None

    destination_address: str
    destination_city: str
    destination_country: str
    destination_postal_code: Optional[str] = None

    # Package Details
    weight: float  # in kg
    dimensions: Optional[str] = None  # "LxWxH"
    declared_value: Optional[float] = None
    insurance_required: bool = False
    fragile: bool = False
    description: Optional[str] = None
    special_instructions: Optional[str] = None

    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    pickup_date: Optional[datetime] = None
    estimated_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[datetime] = None

    # Costs
    shipping_cost: Optional[float] = None
    insurance_cost: Optional[float] = None
    total_cost: Optional[float] = None

    # Tracking
    current_location: Optional[str] = None
    last_update: datetime = Field(default_factory=datetime.utcnow)

# Tracking Event model
class TrackingEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shipment_id: int = Field(foreign_key="shipment.id")
    status: ShipmentStatus
    location: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

# Notification model
class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(foreign_key="user.id")
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Pydantic models for API
class ShipmentCreate(BaseModel):
    customer_id: Optional[int] = None
    priority: ShipmentPriority = ShipmentPriority.NORMAL
    origin_address: str
    origin_city: str
    origin_country: str
    origin_postal_code: Optional[str] = None
    destination_address: str
    destination_city: str
    destination_country: str
    destination_postal_code: Optional[str] = None
    weight: float
    dimensions: Optional[str] = None
    declared_value: Optional[float] = None
    insurance_required: bool = False
    fragile: bool = False
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    estimated_delivery_date: Optional[date] = None

class ShipmentUpdate(BaseModel):
    status: Optional[ShipmentStatus] = None
    priority: Optional[ShipmentPriority] = None
    current_location: Optional[str] = None
    estimated_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[datetime] = None
    special_instructions: Optional[str] = None

class CustomerCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    address: str
    city: str
    country: str
    postal_code: Optional[str] = None

class TrackingEventCreate(BaseModel):
    status: ShipmentStatus
    location: str
    description: str
    created_by: Optional[str] = None

class DashboardStats(BaseModel):
    total_shipments: int
    pending_shipments: int
    in_transit_shipments: int
    delivered_shipments: int
    total_customers: int
    total_revenue: float
    avg_delivery_time: float
    on_time_delivery_rate: float

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_tracking_number() -> str:
    """Generate a unique tracking number"""
    return f"ST{random.randint(100000, 999999)}"

def create_sample_customers(session: Session):
    """Create sample customers with realistic Indian data"""
    customers_data = [
        {
            "name": "Rajesh Kumar",
            "email": "rajesh.kumar@techsolutions.in",
            "phone": "+91-98765-43210",
            "company": "TechSolutions India Pvt Ltd",
            "address": "Plot 123, Cyber City, Sector 24",
            "city": "Gurgaon",
            "country": "India",
            "postal_code": "122002",
            "status": "active"
        },
        {
            "name": "Priya Sharma",
            "email": "priya.sharma@retailhub.in",
            "phone": "+91-98765-43211",
            "company": "RetailHub India",
            "address": "456, Commercial Complex, Connaught Place",
            "city": "New Delhi",
            "country": "India",
            "postal_code": "110001",
            "status": "active"
        },
        {
            "name": "Amit Patel",
            "email": "amit.patel@logisticsplus.in",
            "phone": "+91-98765-43212",
            "company": "LogisticsPlus India Ltd",
            "address": "789, Industrial Area, MIDC",
            "city": "Pune",
            "country": "India",
            "postal_code": "411019",
            "status": "active"
        },
        {
            "name": "Sneha Reddy",
            "email": "sneha.reddy@ecommerceking.in",
            "phone": "+91-98765-43213",
            "company": "E-Commerce King",
            "address": "321, IT Park, Electronic City",
            "city": "Bangalore",
            "country": "India",
            "postal_code": "560100",
            "status": "active"
        },
        {
            "name": "Vikram Singh",
            "email": "vikram.singh@fashionista.in",
            "phone": "+91-98765-43214",
            "company": "Fashionista India",
            "address": "654, Fashion Street, Linking Road",
            "city": "Mumbai",
            "country": "India",
            "postal_code": "400050",
            "status": "active"
        },
        {
            "name": "Deepika Agarwal",
            "email": "deepika.agarwal@autoworld.in",
            "phone": "+91-98765-43215",
            "company": "AutoWorld India",
            "address": "987, Industrial Estate, Udyog Vihar",
            "city": "Chennai",
            "country": "India",
            "postal_code": "600032",
            "status": "active"
        },
        {
            "name": "Arjun Gupta",
            "email": "arjun.gupta@healthcarepro.in",
            "phone": "+91-98765-43216",
            "company": "HealthCare Pro India",
            "address": "147, Medical Complex, Civil Lines",
            "city": "Jaipur",
            "country": "India",
            "postal_code": "302006",
            "status": "active"
        },
        {
            "name": "Kavya Nair",
            "email": "kavya.nair@foodexpress.in",
            "phone": "+91-98765-43217",
            "company": "Food Express India",
            "address": "258, Spice Market, MG Road",
            "city": "Kochi",
            "country": "India",
            "postal_code": "682035",
            "status": "active"
        }
    ]

    for customer_data in customers_data:
        customer = Customer(**customer_data)
        session.add(customer)

    session.commit()

def create_sample_shipments(session: Session):
    """Create sample shipments with realistic data"""
    customers = session.exec(select(Customer)).all()

    # Sample Indian cities for origins and destinations
    cities = [
        ("Mumbai", "India", "400001"),
        ("Delhi", "India", "110001"),
        ("Bangalore", "India", "560001"),
        ("Hyderabad", "India", "500001"),
        ("Chennai", "India", "600001"),
        ("Kolkata", "India", "700001"),
        ("Pune", "India", "411001"),
        ("Ahmedabad", "India", "380001"),
        ("Jaipur", "India", "302001"),
        ("Surat", "India", "395001"),
        ("Lucknow", "India", "226001"),
        ("Kanpur", "India", "208001"),
        ("Nagpur", "India", "440001"),
        ("Indore", "India", "452001"),
        ("Thane", "India", "400601"),
        ("Bhopal", "India", "462001"),
        ("Visakhapatnam", "India", "530001"),
        ("Pimpri-Chinchwad", "India", "411017"),
        ("Patna", "India", "800001"),
        ("Vadodara", "India", "390001"),
        ("Ghaziabad", "India", "201001"),
        ("Ludhiana", "India", "141001"),
        ("Agra", "India", "282001"),
        ("Nashik", "India", "422001"),
        ("Faridabad", "India", "121001"),
        ("Meerut", "India", "250001"),
        ("Rajkot", "India", "360001"),
        ("Kalyan-Dombivali", "India", "421201"),
        ("Vasai-Virar", "India", "401201"),
        ("Varanasi", "India", "221001")
    ]

    statuses = [
        ShipmentStatus.PENDING,
        ShipmentStatus.PICKED_UP,
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.OUT_FOR_DELIVERY,
        ShipmentStatus.DELIVERED,
    ]

    priorities = [
        ShipmentPriority.LOW,
        ShipmentPriority.NORMAL,
        ShipmentPriority.HIGH,
        ShipmentPriority.URGENT
    ]

    descriptions = [
        "Electronics - Mobile Phone",
        "Clothing - Ethnic Wear",
        "Books - Educational Materials",
        "Ayurvedic Medicines",
        "Auto Parts - Two Wheeler Components",
        "Spices and Food Products",
        "Furniture - Wooden Chair",
        "Cricket Equipment",
        "Kitchen Appliances",
        "Handicrafts and Art Items",
        "Industrial Machinery Parts",
        "Pharmaceutical Products",
        "IT Hardware and Accessories",
        "Cotton Textile Materials",
        "Chemical and Laboratory Samples",
        "Jewelry and Ornaments",
        "Agricultural Products",
        "Solar Panel Equipment",
        "Traditional Handicrafts",
        "Organic Food Products"
    ]

    # Create 50 sample shipments
    for i in range(50):
        customer = random.choice(customers)
        origin_city, origin_country, origin_postal = random.choice(cities)
        dest_city, dest_country, dest_postal = random.choice(cities)

        # Ensure origin and destination are different
        while dest_city == origin_city:
            dest_city, dest_country, dest_postal = random.choice(cities)

        status = random.choice(statuses)
        priority = random.choice(priorities)

        # Calculate dates based on status
        created_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        pickup_date = None
        estimated_delivery = None
        actual_delivery = None

        if status != ShipmentStatus.PENDING:
            pickup_date = created_date + timedelta(hours=random.randint(2, 24))
            estimated_delivery = (created_date + timedelta(days=random.randint(3, 10))).date()

            if status == ShipmentStatus.DELIVERED:
                actual_delivery = created_date + timedelta(days=random.randint(2, 8))

        weight = round(random.uniform(0.5, 50.0), 2)
        declared_value = round(random.uniform(50, 5000), 2)
        shipping_cost = round(weight * random.uniform(2, 8), 2)

        shipment = Shipment(
            tracking_number=generate_tracking_number(),
            customer_id=customer.id,
            status=status,
            priority=priority,
            origin_address=f"{random.randint(1, 999)} {random.choice(['MG Road', 'Brigade Road', 'Commercial Street', 'Residency Road', 'Church Street', 'Linking Road', 'SV Road', 'FC Road', 'JM Road', 'Banjara Hills Road'])}",
            origin_city=origin_city,
            origin_country=origin_country,
            origin_postal_code=origin_postal,
            destination_address=f"{random.randint(1, 999)} {random.choice(['Nehru Place', 'Karol Bagh', 'Lajpat Nagar', 'Saket', 'Vasant Kunj', 'Sector 18', 'City Centre', 'Mall Road', 'Civil Lines', 'Model Town'])}",
            destination_city=dest_city,
            destination_country=dest_country,
            destination_postal_code=dest_postal,
            weight=weight,
            dimensions=f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 30)}",
            declared_value=declared_value,
            insurance_required=random.choice([True, False]),
            fragile=random.choice([True, False]),
            description=random.choice(descriptions),
            special_instructions=random.choice([None, "Handle with care", "Signature required", "Call before delivery", "Fragile - This side up", "Do not bend", "Keep dry", "Deliver to security guard"]),
            created_at=created_date,
            pickup_date=pickup_date,
            estimated_delivery_date=estimated_delivery,
            actual_delivery_date=actual_delivery,
            shipping_cost=shipping_cost,
            insurance_cost=round(declared_value * 0.01, 2) if random.choice([True, False]) else 0,
            total_cost=shipping_cost + (round(declared_value * 0.01, 2) if random.choice([True, False]) else 0),
            current_location=f"{random.choice(cities)[0]} Distribution Center" if status in [ShipmentStatus.IN_TRANSIT, ShipmentStatus.OUT_FOR_DELIVERY] else None,
            last_update=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        )

        session.add(shipment)

    session.commit()

    # Update customer statistics
    for customer in customers:
        customer_shipments = session.exec(
            select(Shipment).where(Shipment.customer_id == customer.id)
        ).all()

        customer.total_shipments = len(customer_shipments)
        customer.total_value = sum(s.declared_value or 0 for s in customer_shipments)
        session.add(customer)

    session.commit()

# Create app
app = FastAPI(title="Working Shipment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database session
def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def create_db_and_tables():
    print("🚀 Starting Enhanced Shipment Management API...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create test users
        existing_user = session.exec(select(User).where(User.username == "testuser")).first()
        if not existing_user:
            users = [
                User(
                    username="admin",
                    email="admin@shiptrack.in",
                    full_name="Rahul Sharma",
                    hashed_password=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    phone="+91-98765-00001",
                    company="ShipTrack India Pvt Ltd",
                    address="Cyber Hub, Sector 26, Gurgaon, Haryana",
                    is_active=True
                ),
                User(
                    username="manager",
                    email="manager@shiptrack.in",
                    full_name="Anita Desai",
                    hashed_password=get_password_hash("manager123"),
                    role=UserRole.MANAGER,
                    phone="+91-98765-00002",
                    company="ShipTrack India Pvt Ltd",
                    address="Bandra Kurla Complex, Mumbai, Maharashtra",
                    is_active=True
                ),
                User(
                    username="employee",
                    email="employee@shiptrack.in",
                    full_name="Suresh Kumar",
                    hashed_password=get_password_hash("employee123"),
                    role=UserRole.EMPLOYEE,
                    phone="+91-98765-00003",
                    company="ShipTrack India Pvt Ltd",
                    address="Electronic City, Bangalore, Karnataka",
                    is_active=True
                ),
                User(
                    username="testuser",
                    email="test@shiptrack.in",
                    full_name="Demo User",
                    hashed_password=get_password_hash("password123"),
                    role=UserRole.CUSTOMER,
                    phone="+91-98765-00004",
                    company="Test Customer",
                    address="Connaught Place, New Delhi",
                    is_active=True
                )
            ]

            for user in users:
                session.add(user)
            session.commit()
            print("✅ Test users created")

        # Create sample customers
        existing_customers = session.exec(select(Customer)).first()
        if not existing_customers:
            create_sample_customers(session)
            print("✅ Sample customers created")

        # Create sample shipments
        existing_shipments = session.exec(select(Shipment)).first()
        if not existing_shipments:
            create_sample_shipments(session)
            print("✅ Sample shipments created")

    print("🌐 Server running at: http://localhost:8001")
    print("📚 API docs at: http://localhost:8001/docs")
    print("🔑 Login credentials:")
    print("   Admin: admin / admin123 (Rahul Sharma)")
    print("   Manager: manager / manager123 (Anita Desai)")
    print("   Employee: employee / employee123 (Suresh Kumar)")
    print("   Customer: testuser / password123 (Demo User)")

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint"""
    try:
        print(f"🔐 Login attempt for user: {form_data.username}")
        
        user = db.exec(select(User).where(User.username == form_data.username)).first()
        if not user:
            print(f"❌ User not found: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        if not verify_password(form_data.password, user.hashed_password):
            print(f"❌ Invalid password for user: {form_data.username}")
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        
        print(f"✅ Login successful for user: {form_data.username}")
        
        # Simple token (not secure for production)
        token = f"token_{user.username}_{user.id}"
        return {"access_token": token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Login error")

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Working Shipment API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Shipment Endpoints
@app.get("/shipments", response_model=List[Dict[str, Any]])
def get_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get shipments with filtering and pagination"""
    query = select(Shipment)

    # Apply filters
    if status:
        query = query.where(Shipment.status == status)
    if priority:
        query = query.where(Shipment.priority == priority)
    if customer_id:
        query = query.where(Shipment.customer_id == customer_id)
    if search:
        query = query.where(
            or_(
                Shipment.tracking_number.contains(search),
                Shipment.description.contains(search),
                Shipment.origin_city.contains(search),
                Shipment.destination_city.contains(search)
            )
        )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    shipments = db.exec(query).all()

    # Convert to dict format for frontend compatibility
    result = []
    for shipment in shipments:
        shipment_dict = {
            "id": shipment.id,
            "tracking_number": shipment.tracking_number,
            "status": shipment.status,
            "priority": shipment.priority,
            "origin": f"{shipment.origin_city}, {shipment.origin_country}",
            "destination": f"{shipment.destination_city}, {shipment.destination_country}",
            "weight": shipment.weight,
            "description": shipment.description,
            "estimated_delivery": shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
            "created_at": shipment.created_at.isoformat(),
            "customer_id": shipment.customer_id,
            "declared_value": shipment.declared_value,
            "current_location": shipment.current_location,
            "fragile": shipment.fragile,
            "insurance_required": shipment.insurance_required
        }
        result.append(shipment_dict)

    return result

@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """Get a specific shipment by ID"""
    shipment = db.exec(select(Shipment).where(Shipment.id == shipment_id)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return {
        "id": shipment.id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "priority": shipment.priority,
        "origin": f"{shipment.origin_city}, {shipment.origin_country}",
        "destination": f"{shipment.destination_city}, {shipment.destination_country}",
        "weight": shipment.weight,
        "description": shipment.description,
        "estimated_delivery": shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
        "created_at": shipment.created_at.isoformat(),
        "customer_id": shipment.customer_id,
        "declared_value": shipment.declared_value,
        "current_location": shipment.current_location,
        "fragile": shipment.fragile,
        "insurance_required": shipment.insurance_required,
        "origin_address": shipment.origin_address,
        "destination_address": shipment.destination_address,
        "dimensions": shipment.dimensions,
        "special_instructions": shipment.special_instructions,
        "shipping_cost": shipment.shipping_cost,
        "total_cost": shipment.total_cost
    }

@app.post("/shipments")
def create_shipment(shipment_data: ShipmentCreate, db: Session = Depends(get_db)):
    """Create a new shipment"""
    shipment = Shipment(
        tracking_number=generate_tracking_number(),
        **shipment_data.dict()
    )

    # Calculate shipping cost based on weight and distance (simplified)
    base_cost = 10.0
    weight_cost = shipment.weight * 2.5
    shipment.shipping_cost = round(base_cost + weight_cost, 2)

    if shipment.insurance_required and shipment.declared_value:
        shipment.insurance_cost = round(shipment.declared_value * 0.01, 2)
    else:
        shipment.insurance_cost = 0.0

    shipment.total_cost = shipment.shipping_cost + shipment.insurance_cost

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return {"message": "Shipment created successfully", "tracking_number": shipment.tracking_number, "id": shipment.id}

@app.put("/shipments/{shipment_id}")
def update_shipment(shipment_id: int, shipment_data: ShipmentUpdate, db: Session = Depends(get_db)):
    """Update a shipment"""
    shipment = db.exec(select(Shipment).where(Shipment.id == shipment_id)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    update_data = shipment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shipment, field, value)

    shipment.last_update = datetime.utcnow()

    db.add(shipment)
    db.commit()

    return {"message": "Shipment updated successfully"}

@app.delete("/shipments/{shipment_id}")
def delete_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """Delete a shipment"""
    shipment = db.exec(select(Shipment).where(Shipment.id == shipment_id)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    db.delete(shipment)
    db.commit()

    return {"message": "Shipment deleted successfully"}

@app.get("/shipments/track/{tracking_number}")
def track_shipment(tracking_number: str, db: Session = Depends(get_db)):
    """Track a shipment by tracking number"""
    shipment = db.exec(select(Shipment).where(Shipment.tracking_number == tracking_number)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Get tracking events
    tracking_events = db.exec(
        select(TrackingEvent).where(TrackingEvent.shipment_id == shipment.id).order_by(TrackingEvent.timestamp)
    ).all()

    return {
        "id": shipment.id,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "priority": shipment.priority,
        "origin": f"{shipment.origin_city}, {shipment.origin_country}",
        "destination": f"{shipment.destination_city}, {shipment.destination_country}",
        "weight": shipment.weight,
        "description": shipment.description,
        "estimated_delivery": shipment.estimated_delivery_date.isoformat() if shipment.estimated_delivery_date else None,
        "current_location": shipment.current_location,
        "tracking_events": [
            {
                "status": event.status,
                "location": event.location,
                "description": event.description,
                "timestamp": event.timestamp.isoformat()
            }
            for event in tracking_events
        ]
    }

@app.get("/users/me")
def get_current_user():
    """Get current user (simplified)"""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@shiptrack.in",
        "full_name": "Rahul Sharma",
        "role": "admin",
        "company": "ShipTrack India Pvt Ltd",
        "phone": "+91-98765-00001",
        "is_active": True
    }

# Customer Endpoints
@app.get("/customers")
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get customers with filtering and pagination"""
    query = select(Customer)

    if search:
        query = query.where(
            or_(
                Customer.name.contains(search),
                Customer.email.contains(search),
                Customer.company.contains(search)
            )
        )

    if status:
        query = query.where(Customer.status == status)

    query = query.offset(skip).limit(limit)
    customers = db.exec(query).all()

    result = []
    for customer in customers:
        result.append({
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "company": customer.company,
            "address": customer.address,
            "city": customer.city,
            "country": customer.country,
            "status": customer.status,
            "shipmentCount": customer.total_shipments,
            "totalValue": customer.total_value,
            "created_at": customer.created_at.isoformat()
        })

    return result

@app.post("/customers")
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer"""
    # Check if email already exists
    existing_customer = db.exec(select(Customer).where(Customer.email == customer_data.email)).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")

    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {"message": "Customer created successfully", "id": customer.id}

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer by ID"""
    customer = db.exec(select(Customer).where(Customer.id == customer_id)).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get customer's shipments
    shipments = db.exec(select(Shipment).where(Shipment.customer_id == customer_id)).all()

    return {
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "company": customer.company,
        "address": customer.address,
        "city": customer.city,
        "country": customer.country,
        "status": customer.status,
        "total_shipments": len(shipments),
        "total_value": sum(s.declared_value or 0 for s in shipments),
        "created_at": customer.created_at.isoformat(),
        "recent_shipments": [
            {
                "id": s.id,
                "tracking_number": s.tracking_number,
                "status": s.status,
                "created_at": s.created_at.isoformat()
            }
            for s in shipments[-5:]  # Last 5 shipments
        ]
    }

# Analytics Endpoints
@app.get("/analytics/dashboard")
def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics"""
    # Get all shipments
    shipments = db.exec(select(Shipment)).all()
    customers = db.exec(select(Customer)).all()

    # Calculate statistics
    total_shipments = len(shipments)
    pending_shipments = len([s for s in shipments if s.status == ShipmentStatus.PENDING])
    in_transit_shipments = len([s for s in shipments if s.status in [ShipmentStatus.IN_TRANSIT, ShipmentStatus.PICKED_UP, ShipmentStatus.OUT_FOR_DELIVERY]])
    delivered_shipments = len([s for s in shipments if s.status == ShipmentStatus.DELIVERED])

    total_revenue = sum(s.total_cost or 0 for s in shipments)

    # Calculate average delivery time for delivered shipments
    delivered_with_dates = [s for s in shipments if s.status == ShipmentStatus.DELIVERED and s.actual_delivery_date and s.created_at]
    if delivered_with_dates:
        avg_delivery_time = sum(
            (s.actual_delivery_date - s.created_at).days
            for s in delivered_with_dates
        ) / len(delivered_with_dates)
    else:
        avg_delivery_time = 0

    # Calculate on-time delivery rate
    on_time_deliveries = len([
        s for s in delivered_with_dates
        if s.estimated_delivery_date and s.actual_delivery_date.date() <= s.estimated_delivery_date
    ])
    on_time_delivery_rate = (on_time_deliveries / len(delivered_with_dates) * 100) if delivered_with_dates else 0

    return {
        "total_shipments": total_shipments,
        "pending_shipments": pending_shipments,
        "in_transit_shipments": in_transit_shipments,
        "delivered_shipments": delivered_shipments,
        "total_customers": len(customers),
        "total_revenue": round(total_revenue, 2),
        "avg_delivery_time": round(avg_delivery_time, 1),
        "on_time_delivery_rate": round(on_time_delivery_rate, 1)
    }

@app.get("/analytics/shipments-by-status")
def get_shipments_by_status(db: Session = Depends(get_db)):
    """Get shipment count by status"""
    shipments = db.exec(select(Shipment)).all()

    status_counts = {}
    for status in ShipmentStatus:
        status_counts[status.value] = len([s for s in shipments if s.status == status])

    return status_counts

@app.get("/analytics/revenue-by-month")
def get_revenue_by_month(db: Session = Depends(get_db)):
    """Get revenue by month for the last 12 months"""
    shipments = db.exec(select(Shipment)).all()

    # Group by month
    monthly_revenue = {}
    for shipment in shipments:
        if shipment.total_cost and shipment.created_at:
            month_key = shipment.created_at.strftime("%Y-%m")
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += shipment.total_cost

    return monthly_revenue

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Enhanced API is working", "version": "2.0.0"}

if __name__ == "__main__":
    print("🚀 Starting Enhanced Shipment Management Server...")
    print("📊 Features included:")
    print("   - Complete CRUD operations for shipments")
    print("   - Customer management")
    print("   - Real-time tracking")
    print("   - Analytics and reporting")
    print("   - 50+ sample shipments")
    print("   - 8 sample customers")
    print("   - Multiple user roles")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
