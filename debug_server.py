#!/usr/bin/env python3
"""
Debug server startup issues
"""

import sys
import os

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    
    try:
        print("  Testing app.main import...")
        from app.main import app
        print("  ✅ app.main imported successfully")
        
        print("  Testing app.schemas import...")
        from app.schemas import User, Shipment
        print("  ✅ app.schemas imported successfully")
        
        print("  Testing uvicorn import...")
        import uvicorn
        print("  ✅ uvicorn imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database connection"""
    print("🗄️  Testing database...")
    
    try:
        from app.database import engine
        from sqlmodel import SQLModel
        
        print("  Creating tables...")
        SQLModel.metadata.create_all(engine)
        print("  ✅ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server_start():
    """Test server startup"""
    print("🚀 Testing server startup...")
    
    try:
        import uvicorn
        from app.main import app
        
        print("  Starting server on port 8001...")
        print("  Note: This will start the actual server. Press Ctrl+C to stop.")
        
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8001,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("  🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"  ❌ Server startup error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🐛 Server Debug Script")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed. Cannot proceed.")
        return
    
    # Test database
    if not test_database():
        print("❌ Database test failed. Cannot proceed.")
        return
    
    print("✅ All tests passed! Starting server...")
    print("=" * 40)
    
    # Start server
    test_server_start()

if __name__ == "__main__":
    main()
