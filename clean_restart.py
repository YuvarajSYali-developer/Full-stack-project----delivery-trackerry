#!/usr/bin/env python3
"""
Clean restart script
"""

import os
import subprocess
import time
import sys

def kill_processes():
    """Kill any running uvicorn processes"""
    print("🔄 Killing any running processes...")
    
    try:
        # Kill uvicorn processes on Windows
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        print("  ✅ Processes killed")
        time.sleep(2)
    except Exception as e:
        print(f"  ⚠️  Could not kill processes: {e}")

def remove_database():
    """Remove database file"""
    print("🗑️  Removing database...")
    
    db_files = ["sqlite.db", "test.db"]
    for db_file in db_files:
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"  ✅ Removed {db_file}")
        except Exception as e:
            print(f"  ⚠️  Could not remove {db_file}: {e}")

def create_simple_server():
    """Create a very simple server"""
    print("📝 Creating simple server...")
    
    server_code = '''
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine, select, Field
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
import os

# Simple database setup
DATABASE_URL = "sqlite:///./simple.db"
engine = create_engine(DATABASE_URL, echo=False)

# Simple User model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create app
app = FastAPI(title="Simple Shipment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    SQLModel.metadata.create_all(engine)
    
    # Create test user
    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.username == "testuser")).first()
        if not existing_user:
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

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple token (not secure for production)
    token = f"simple_token_{user.username}"
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"message": "Simple Shipment API is running!"}

@app.get("/users/me")
def get_current_user():
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
'''
    
    with open("simple_app.py", "w") as f:
        f.write(server_code)
    
    print("  ✅ Simple server created")

def start_simple_server():
    """Start the simple server"""
    print("🚀 Starting simple server...")
    
    try:
        subprocess.run([sys.executable, "simple_app.py"], check=True)
    except KeyboardInterrupt:
        print("  🛑 Server stopped")
    except Exception as e:
        print(f"  ❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🧹 Clean Restart Script")
    print("=" * 30)
    
    kill_processes()
    remove_database()
    create_simple_server()
    
    print("✅ Ready to start simple server!")
    print("Run: python simple_app.py")

if __name__ == "__main__":
    main()
