# main.py
from typing import Any, Optional, Dict, List, DefaultDict  # noqa: F401
from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager  # noqa: F401
from sqlmodel import Session, select
from datetime import timedelta
from app.database import get_db
from app.schemas import ShipmentCreate, ShipmentUpdate, User, UserCreate, UserRead, Token, Shipment, ShipmentRead
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

settings = get_settings()
app = FastAPI(
    title="Shipment Management API",
    description="A FastAPI backend for managing shipments with authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*", "Authorization", "Content-Type"],
    expose_headers=["*"],
    max_age=3600,
)

# Add rate limiting middleware
request_counts: DefaultDict[str, List[float]] = defaultdict(list)
RATE_LIMIT = 100  # requests
RATE_LIMIT_WINDOW = 60  # seconds

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

# Setup middleware
setup_middleware(app)

# Initialize database on startup
@app.on_event("startup")
async def on_startup():
    logger.info("Starting up the application...")
    try:
        from app.seed import seed_database
        seed_database()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down the application...")

# Authentication endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Validate input
        if not form_data.username or not form_data.password:
            logger.warning("Login attempt with empty username or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
        
        # Execute query and get the first result
        stmt = select(User).where(User.username == form_data.username)
        logger.debug(f"Executing query: {stmt}")
        
        try:
            # Use SQLModel's exec method
            user = db.exec(stmt).first()

            if not user:
                logger.warning(f"Login failed: User '{form_data.username}' not found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            logger.debug(f"Found user: {user.username}")
            
            # Verify password
            if not verify_password(form_data.password, user.hashed_password):
                logger.warning(f"Login failed: Incorrect password for user '{form_data.username}'")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            
            logger.info(f"Login successful for user: {user.username}")
            return {"access_token": access_token, "token_type": "bearer"}
            
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"Database error during login: {str(db_error)}")
            import traceback
            logger.error(f"Database error traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error during login"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        import traceback
        logger.error(f"Error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login"
        )

@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    try:
        logger.info(f"User registration attempt for: {user.username}")
        
        # Validate input
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

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User registered successfully: {user.username}")
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
    """
    Get current user information.
    """
    logger.info(f"Fetching current user info for: {current_user.username}")
    return current_user

# Protected shipment endpoints
@app.post("/shipments/", response_model=ShipmentRead)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new shipment.
    """
    try:
        logger.info(f"Creating new shipment for user: {current_user.username}")
        shipment_data = shipment.dict()
        db_shipment = Shipment(**shipment_data)
        
        try:
            db.add(db_shipment)
            db.commit()
            db.refresh(db_shipment)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Fetching shipments for user: {current_user.username}")
    shipments = db.exec(select(Shipment).offset(skip).limit(limit)).all()
    return shipments

@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def read_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Fetching shipment {shipment_id} for user: {current_user.username}")
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")
    return ShipmentRead.model_validate(shipment)

@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment: ShipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Updating shipment {shipment_id} for user: {current_user.username}")
    db_shipment = db.get(Shipment, shipment_id)
    if db_shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment_data = shipment.dict(exclude_unset=True)
    for key, value in shipment_data.items():
        setattr(db_shipment, key, value)
    
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    logger.info(f"Shipment {shipment_id} updated successfully")
    return ShipmentRead.model_validate(db_shipment)

@app.delete("/shipments/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"Deleting shipment {shipment_id} for user: {current_user.username}")
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        logger.warning(f"Shipment not found: {shipment_id}")
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    db.delete(shipment)
    db.commit()
    logger.info(f"Shipment {shipment_id} deleted successfully")
    return {"message": "Shipment deleted successfully"}