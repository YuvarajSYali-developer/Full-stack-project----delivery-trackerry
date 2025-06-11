#!/usr/bin/env python3
"""
Enhanced Shipment Management Backend with Full Features
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, SQLModel, create_engine, Field
from datetime import timedelta, datetime
from typing import List, Optional, Dict, Any
from collections import defaultdict
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced models
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    full_name: str | None = Field(default=None, max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = Field(default=None)

class Shipment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True, min_length=5, max_length=50)
    status: str = Field(default="pending")  # pending, shipped, in_transit, delivered, cancelled
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    weight: float = Field(gt=0, le=10000)  # in kg
    description: str | None = Field(default=None, max_length=500)
    estimated_delivery: datetime | None = Field(default=None)
    actual_delivery: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int | None = Field(default=None, foreign_key="user.id")

class ShipmentHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    shipment_id: int = Field(foreign_key="shipment.id")
    status: str
    location: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_by: int | None = Field(default=None, foreign_key="user.id")

# Pydantic models for API
class Token(SQLModel):
    access_token: str
    token_type: str

class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    full_name: str | None = None
    password: str = Field(min_length=6)

class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: str | None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: datetime | None

class ShipmentCreate(SQLModel):
    tracking_number: str = Field(min_length=5, max_length=50)
    status: str = Field(default="pending")
    origin: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    weight: float = Field(gt=0, le=10000)
    description: str | None = None
    estimated_delivery: datetime | None = None

class ShipmentUpdate(SQLModel):
    status: str | None = None
    origin: str | None = None
    destination: str | None = None
    weight: float | None = None
    description: str | None = None
    estimated_delivery: datetime | None = None
    actual_delivery: datetime | None = None

class ShipmentRead(SQLModel):
    id: int
    tracking_number: str
    status: str
    origin: str
    destination: str
    weight: float
    description: str | None
    estimated_delivery: datetime | None
    actual_delivery: datetime | None
    created_at: datetime
    updated_at: datetime
    created_by: int | None

class ShipmentHistoryCreate(SQLModel):
    status: str
    location: str | None = None
    notes: str | None = None

class ShipmentHistoryRead(SQLModel):
    id: int
    shipment_id: int
    status: str
    location: str | None
    notes: str | None
    timestamp: datetime
    updated_by: int | None

# Enhanced auth functions
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import timezone

# Security configuration
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: next(get_session()))):
    username = verify_token(token)
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Database setup
DATABASE_URL = "sqlite:///./shipment_management.db"
engine = create_engine(DATABASE_URL, echo=False)  # Set to True for SQL debugging

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Rate limiting
request_counts: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT = 100  # requests per window
RATE_LIMIT_WINDOW = 60  # seconds

# FastAPI app with enhanced configuration
app = FastAPI(
    title="Advanced Shipment Management API",
    description="A comprehensive shipment tracking and management system with authentication, history tracking, and admin features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Clean old requests
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_WINDOW]

    # Check rate limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )

    # Add current request
    request_counts[client_ip].append(current_time)

    response = await call_next(request)
    return response

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    # Create default users
    with Session(engine) as session:
        # Create test user
        test_user = session.exec(select(User).where(User.username == "testuser")).first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=get_password_hash("password123"),
                is_active=True,
                is_admin=False
            )
            session.add(test_user)
            logger.info("Test user created: testuser / password123")

        # Create admin user
        admin_user = session.exec(select(User).where(User.username == "admin")).first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            session.add(admin_user)
            logger.info("Admin user created: admin / admin123")

        session.commit()

        # Create sample shipments
        sample_shipments = [
            {
                "tracking_number": "SHP001",
                "status": "pending",
                "origin": "New York, NY",
                "destination": "Los Angeles, CA",
                "weight": 5.5,
                "description": "Electronics package",
                "created_by": test_user.id
            },
            {
                "tracking_number": "SHP002",
                "status": "shipped",
                "origin": "Chicago, IL",
                "destination": "Miami, FL",
                "weight": 12.3,
                "description": "Books and documents",
                "created_by": test_user.id
            },
            {
                "tracking_number": "SHP003",
                "status": "delivered",
                "origin": "Seattle, WA",
                "destination": "Boston, MA",
                "weight": 8.7,
                "description": "Clothing items",
                "created_by": test_user.id
            }
        ]

        for shipment_data in sample_shipments:
            existing = session.exec(select(Shipment).where(Shipment.tracking_number == shipment_data["tracking_number"])).first()
            if not existing:
                shipment = Shipment(**shipment_data)
                session.add(shipment)

        session.commit()
        logger.info("Sample data created successfully")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Advanced Shipment Management API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "auth": "/token",
            "users": "/users/",
            "shipments": "/shipments/"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc),
        "database": "connected"
    }

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session)
):
    """Login endpoint that returns JWT token"""
    try:
        logger.info(f"Login attempt for user: {form_data.username}")

        # Find user
        user = db.exec(select(User).where(User.username == form_data.username)).first()

        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.add(user)
        db.commit()

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        logger.info(f"Login successful for user: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User management endpoints
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    """Create a new user"""
    try:
        logger.info(f"User registration attempt for: {user.username}")

        # Check if username exists
        existing_user = db.exec(select(User).where(User.username == user.username)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email exists
        existing_email = db.exec(select(User).where(User.email == user.email)).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"User registered successfully: {user.username}")
        return db_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@app.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.get("/users/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_session)
):
    """Get all users (admin only)"""
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    return users

# Shipment CRUD endpoints
@app.post("/shipments/", response_model=ShipmentRead)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shipment"""
    try:
        logger.info(f"Creating shipment for user: {current_user.username}")

        # Check if tracking number exists
        existing = db.exec(select(Shipment).where(Shipment.tracking_number == shipment.tracking_number)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tracking number already exists")

        # Create shipment
        db_shipment = Shipment(
            **shipment.model_dump(),
            created_by=current_user.id,
            updated_at=datetime.now(timezone.utc)
        )

        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)

        # Create initial history entry
        history = ShipmentHistory(
            shipment_id=db_shipment.id,
            status=db_shipment.status,
            location=db_shipment.origin,
            notes=f"Shipment created by {current_user.username}",
            updated_by=current_user.id
        )
        db.add(history)
        db.commit()

        logger.info(f"Shipment created: {db_shipment.tracking_number}")
        return db_shipment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shipment creation error: {e}")
        raise HTTPException(status_code=500, detail="Error creating shipment")

@app.get("/shipments/", response_model=List[ShipmentRead])
def read_shipments(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    search: str = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get shipments with optional filtering"""
    query = select(Shipment)

    # Apply filters
    if status:
        query = query.where(Shipment.status == status)

    if search:
        query = query.where(
            (Shipment.tracking_number.contains(search)) |
            (Shipment.origin.contains(search)) |
            (Shipment.destination.contains(search)) |
            (Shipment.description.contains(search))
        )

    # Non-admin users can only see their own shipments
    if not current_user.is_admin:
        query = query.where(Shipment.created_by == current_user.id)

    shipments = db.exec(query.offset(skip).limit(limit)).all()
    return shipments

@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def read_shipment(
    shipment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific shipment"""
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Check permissions
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return shipment

@app.get("/shipments/track/{tracking_number}", response_model=ShipmentRead)
def track_shipment(
    tracking_number: str,
    db: Session = Depends(get_session)
):
    """Public endpoint to track shipment by tracking number"""
    shipment = db.exec(select(Shipment).where(Shipment.tracking_number == tracking_number)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    return shipment

@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a shipment"""
    try:
        db_shipment = db.get(Shipment, shipment_id)
        if not db_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")

        # Check permissions
        if not current_user.is_admin and db_shipment.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Update fields
        update_data = shipment_update.model_dump(exclude_unset=True)
        old_status = db_shipment.status

        for field, value in update_data.items():
            setattr(db_shipment, field, value)

        db_shipment.updated_at = datetime.now(timezone.utc)

        # If status changed, create history entry
        if "status" in update_data and update_data["status"] != old_status:
            history = ShipmentHistory(
                shipment_id=shipment_id,
                status=update_data["status"],
                notes=f"Status updated by {current_user.username}",
                updated_by=current_user.id
            )
            db.add(history)

        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)

        logger.info(f"Shipment updated: {db_shipment.tracking_number}")
        return db_shipment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shipment update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating shipment")

@app.delete("/shipments/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a shipment"""
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Check permissions
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete related history first
    history_records = db.exec(select(ShipmentHistory).where(ShipmentHistory.shipment_id == shipment_id)).all()
    for history in history_records:
        db.delete(history)

    db.delete(shipment)
    db.commit()

    logger.info(f"Shipment deleted: {shipment.tracking_number}")
    return {"message": "Shipment deleted successfully"}

# Analytics endpoint
@app.get("/analytics/dashboard")
def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """Get dashboard analytics"""
    # Base query
    base_query = select(Shipment)
    if not current_user.is_admin:
        base_query = base_query.where(Shipment.created_by == current_user.id)

    # Get counts by status
    status_counts = {}
    for status in ["pending", "shipped", "in_transit", "delivered", "cancelled"]:
        count = len(db.exec(base_query.where(Shipment.status == status)).all())
        status_counts[status] = count

    # Get total shipments
    total_shipments = len(db.exec(base_query).all())

    # Get recent shipments
    recent_shipments = db.exec(
        base_query.order_by(Shipment.created_at.desc()).limit(5)
    ).all()

    return {
        "total_shipments": total_shipments,
        "status_counts": status_counts,
        "recent_shipments": [
            {
                "id": s.id,
                "tracking_number": s.tracking_number,
                "status": s.status,
                "origin": s.origin,
                "destination": s.destination,
                "created_at": s.created_at
            } for s in recent_shipments
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("minimal_backend:app", host="0.0.0.0", port=8001, reload=True)
