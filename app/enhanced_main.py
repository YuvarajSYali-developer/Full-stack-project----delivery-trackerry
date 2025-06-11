# enhanced_main.py - Enhanced version with additional business logic
from typing import Any, Optional, Dict, List, DefaultDict
from fastapi import FastAPI, HTTPException, status, Depends, Request, Query, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select, func, and_, or_
from datetime import timedelta, datetime
from app.database import get_db, init_db
from app.schemas import (
    ShipmentCreate, ShipmentUpdate, User, UserCreate, UserRead, Token, Shipment, ShipmentRead,
    TrackingHistory, TrackingHistoryCreate, TrackingHistoryRead,
    Document, DocumentCreate, DocumentRead, DocumentType,
    Notification, NotificationCreate, NotificationRead,
    DashboardAnalytics, ShipmentStatus, ShipmentPriority, UserRole
)
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
)
from app.config import get_settings
from app.logger import logger
from app.middleware import setup_middleware
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import os
import uuid
from pathlib import Path

settings = get_settings()
app = FastAPI(
    title="Advanced Shipment Management API",
    description="A comprehensive FastAPI backend for managing shipments with advanced business logic",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Rate limiting middleware
request_counts: DefaultDict[str, List[float]] = defaultdict(list)
RATE_LIMIT = 100
RATE_LIMIT_WINDOW = 60

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()
    
    request_counts[client_ip] = [t for t in request_counts[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
    
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )
    
    request_counts[client_ip].append(current_time)
    response = await call_next(request)
    return response

setup_middleware(app)

# Initialize database on startup
@app.on_event("startup")
async def on_startup():
    logger.info("Starting up the enhanced application...")
    try:
        from app.seed import seed_database
        seed_database()
        logger.info("Enhanced application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down the enhanced application...")

# Helper function to check user permissions
def check_permission(current_user: User, required_roles: List[UserRole]):
    if current_user.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

# Authentication endpoints (same as before but with role support)
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token login with role-based access."""
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        if not form_data.username or not form_data.password:
            logger.warning("Login attempt with empty username or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
        
        stmt = select(User).where(User.username == form_data.username)
        user = db.exec(stmt).first()

        if not user:
            logger.warning(f"Login failed: User '{form_data.username}' not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: Incorrect password for user '{form_data.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {user.username} with role: {user.role}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with role assignment."""
    try:
        logger.info(f"User registration attempt for: {user.username}")
        
        if not user.username or not user.password or not user.email:
            logger.warning("User registration attempt with missing required fields")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username, password, and email are required"
            )
        
        # Check if username exists
        stmt = select(User).where(User.username == user.username)
        existing_user = db.exec(stmt).first()
        if existing_user:
            logger.warning(f"Username already exists: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")

        # Check if email exists
        stmt = select(User).where(User.email == user.email)
        existing_email = db.exec(stmt).first()
        if existing_email:
            logger.warning(f"Email already exists: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            phone=user.phone,
            address=user.address,
            company=user.company,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User registered successfully: {user.username} with role: {user.role}")
            return UserRead.model_validate(db_user)
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error during user creation: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@app.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    logger.info(f"Fetching current user info for: {current_user.username}")
    return current_user

# Enhanced Analytics Endpoints
@app.get("/analytics/dashboard", response_model=DashboardAnalytics)
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics."""
    check_permission(current_user, [UserRole.ADMIN, UserRole.MANAGER])
    
    try:
        # Total shipments
        total_shipments = db.exec(select(func.count(Shipment.id))).first()
        
        # Shipments by status
        pending_shipments = db.exec(
            select(func.count(Shipment.id)).where(Shipment.status == ShipmentStatus.PENDING)
        ).first()
        
        in_transit_shipments = db.exec(
            select(func.count(Shipment.id)).where(Shipment.status == ShipmentStatus.IN_TRANSIT)
        ).first()
        
        delivered_shipments = db.exec(
            select(func.count(Shipment.id)).where(Shipment.status == ShipmentStatus.DELIVERED)
        ).first()
        
        # Revenue calculations (based on declared value)
        total_revenue = db.exec(
            select(func.sum(Shipment.declared_value)).where(Shipment.declared_value.is_not(None))
        ).first() or 0.0
        
        # Monthly revenue (current month)
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = db.exec(
            select(func.sum(Shipment.declared_value)).where(
                and_(
                    Shipment.declared_value.is_not(None),
                    Shipment.created_at >= current_month_start
                )
            )
        ).first() or 0.0
        
        # Top destinations
        top_destinations_query = db.exec(
            select(Shipment.destination_city, func.count(Shipment.id).label('count'))
            .group_by(Shipment.destination_city)
            .order_by(func.count(Shipment.id).desc())
            .limit(5)
        ).all()
        
        top_destinations = [
            {"city": dest[0], "count": dest[1]} for dest in top_destinations_query
        ]
        
        # Recent shipments
        recent_shipments_query = db.exec(
            select(Shipment)
            .order_by(Shipment.created_at.desc())
            .limit(10)
        ).all()
        
        recent_shipments = [
            {
                "id": ship.id,
                "tracking_number": ship.tracking_number,
                "status": ship.status,
                "destination": ship.destination_city,
                "created_at": ship.created_at.isoformat()
            } for ship in recent_shipments_query
        ]
        
        return DashboardAnalytics(
            total_shipments=total_shipments or 0,
            pending_shipments=pending_shipments or 0,
            in_transit_shipments=in_transit_shipments or 0,
            delivered_shipments=delivered_shipments or 0,
            total_revenue=total_revenue,
            monthly_revenue=monthly_revenue,
            average_delivery_time=3.5,  # Placeholder - would calculate from actual data
            customer_satisfaction=4.2,  # Placeholder - would come from feedback system
            top_destinations=top_destinations,
            recent_shipments=recent_shipments
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching analytics data"
        )

# Enhanced Shipment Endpoints
@app.post("/shipments/", response_model=ShipmentRead)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shipment with enhanced tracking."""
    try:
        logger.info(f"Creating new shipment for user: {current_user.username}")

        # Generate unique tracking number if not provided
        if not shipment.tracking_number:
            shipment.tracking_number = f"SHP{uuid.uuid4().hex[:8].upper()}"

        # Check if tracking number already exists
        existing = db.exec(select(Shipment).where(Shipment.tracking_number == shipment.tracking_number)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tracking number already exists")

        shipment_data = shipment.dict()

        # Set customer_id based on current user role
        if current_user.role == UserRole.CUSTOMER:
            shipment_data["customer_id"] = current_user.id

        db_shipment = Shipment(**shipment_data)

        try:
            db.add(db_shipment)
            db.commit()
            db.refresh(db_shipment)

            # Create initial tracking history
            initial_tracking = TrackingHistory(
                shipment_id=db_shipment.id,
                status=ShipmentStatus.PENDING,
                location="Origin Facility",
                description="Shipment created and pending pickup",
                timestamp=datetime.utcnow()
            )
            db.add(initial_tracking)
            db.commit()

            logger.info(f"Shipment created successfully with ID: {db_shipment.id}")
            return ShipmentRead.model_validate(db_shipment)
        except Exception as db_error:
            db.rollback()
            logger.error(f"Database error during shipment creation: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating shipment"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during shipment creation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@app.get("/shipments/", response_model=List[ShipmentRead])
def read_shipments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ShipmentStatus] = None,
    priority: Optional[ShipmentPriority] = None,
    search: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get shipments with advanced filtering."""
    logger.info(f"Fetching shipments for user: {current_user.username}")

    query = select(Shipment)

    # Apply role-based filtering
    if current_user.role == UserRole.CUSTOMER:
        query = query.where(Shipment.customer_id == current_user.id)
    elif customer_id and current_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
        query = query.where(Shipment.customer_id == customer_id)

    # Apply filters
    if status:
        query = query.where(Shipment.status == status)
    if priority:
        query = query.where(Shipment.priority == priority)
    if search:
        query = query.where(
            or_(
                Shipment.tracking_number.contains(search),
                Shipment.origin_city.contains(search),
                Shipment.destination_city.contains(search),
                Shipment.description.contains(search)
            )
        )

    query = query.offset(skip).limit(limit).order_by(Shipment.created_at.desc())
    shipments = db.exec(query).all()
    return shipments

@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def read_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific shipment with access control."""
    logger.info(f"Fetching shipment {shipment_id} for user: {current_user.username}")
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Check access permissions
    if current_user.role == UserRole.CUSTOMER and shipment.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ShipmentRead.model_validate(shipment)

@app.get("/shipments/track/{tracking_number}", response_model=ShipmentRead)
def track_shipment(
    tracking_number: str,
    db: Session = Depends(get_db)
):
    """Public endpoint to track shipment by tracking number."""
    logger.info(f"Tracking shipment: {tracking_number}")
    shipment = db.exec(select(Shipment).where(Shipment.tracking_number == tracking_number)).first()
    if shipment is None:
        logger.warning(f"Shipment not found: {tracking_number}")
        raise HTTPException(status_code=404, detail="Shipment not found")

    return ShipmentRead.model_validate(shipment)

@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a shipment with status tracking."""
    logger.info(f"Updating shipment {shipment_id} for user: {current_user.username}")
    db_shipment = db.get(Shipment, shipment_id)
    if db_shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Check permissions
    if current_user.role == UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Customers cannot update shipments")

    old_status = db_shipment.status
    shipment_data = shipment.dict(exclude_unset=True)

    for key, value in shipment_data.items():
        setattr(db_shipment, key, value)

    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)

    # Create tracking history if status changed
    if "status" in shipment_data and shipment_data["status"] != old_status:
        tracking_entry = TrackingHistory(
            shipment_id=shipment_id,
            status=shipment_data["status"],
            location="Processing Facility",
            description=f"Status updated to {shipment_data['status']}",
            timestamp=datetime.utcnow()
        )
        db.add(tracking_entry)
        db.commit()

    logger.info(f"Shipment {shipment_id} updated successfully")
    return ShipmentRead.model_validate(db_shipment)

@app.delete("/shipments/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a shipment (admin/manager only)."""
    check_permission(current_user, [UserRole.ADMIN, UserRole.MANAGER])

    logger.info(f"Deleting shipment {shipment_id} for user: {current_user.username}")
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")

    db.delete(shipment)
    db.commit()
    logger.info(f"Shipment {shipment_id} deleted successfully")
    return {"message": "Shipment deleted successfully"}

# Tracking History Endpoints
@app.get("/shipments/{shipment_id}/tracking", response_model=List[TrackingHistoryRead])
def get_shipment_tracking_history(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tracking history for a shipment."""
    # Verify shipment exists and user has access
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if current_user.role == UserRole.CUSTOMER and shipment.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    tracking_history = db.exec(
        select(TrackingHistory)
        .where(TrackingHistory.shipment_id == shipment_id)
        .order_by(TrackingHistory.timestamp.desc())
    ).all()

    return tracking_history

@app.post("/shipments/{shipment_id}/tracking", response_model=TrackingHistoryRead)
def add_tracking_update(
    shipment_id: int,
    tracking: TrackingHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a tracking update to a shipment."""
    check_permission(current_user, [UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE])

    # Verify shipment exists
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Update shipment status if different
    if shipment.status != tracking.status:
        shipment.status = tracking.status
        db.add(shipment)

    # Create tracking entry
    db_tracking = TrackingHistory(
        shipment_id=shipment_id,
        status=tracking.status,
        location=tracking.location,
        description=tracking.description,
        timestamp=tracking.timestamp
    )

    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)

    return TrackingHistoryRead.model_validate(db_tracking)

# Notification Endpoints
@app.get("/notifications/", response_model=List[NotificationRead])
def get_user_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get notifications for the current user."""
    query = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.read_at.is_(None))

    query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    notifications = db.exec(query).all()

    return notifications

@app.post("/notifications/", response_model=NotificationRead)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a notification (admin/manager only)."""
    check_permission(current_user, [UserRole.ADMIN, UserRole.MANAGER])

    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return NotificationRead.model_validate(db_notification)

@app.patch("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    notification.read_at = datetime.utcnow()
    db.add(notification)
    db.commit()

    return {"message": "Notification marked as read"}

# User Management Endpoints (Admin only)
@app.get("/admin/users/", response_model=List[UserRead])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users (admin only)."""
    check_permission(current_user, [UserRole.ADMIN])

    query = select(User)
    if role:
        query = query.where(User.role == role)

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    users = db.exec(query).all()

    return users

@app.patch("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    new_role: UserRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update user role (admin only)."""
    check_permission(current_user, [UserRole.ADMIN])

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.add(user)
    db.commit()

    return {"message": f"User role updated to {new_role}"}

@app.patch("/admin/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Toggle user active status (admin only)."""
    check_permission(current_user, [UserRole.ADMIN])

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.add(user)
    db.commit()

    status = "activated" if user.is_active else "deactivated"
    return {"message": f"User {status} successfully"}
