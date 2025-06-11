#!/usr/bin/env python3
"""
Test script to verify all the fixes are working correctly
"""

import sys
import os
import json
from pathlib import Path

def test_backend_imports():
    """Test that backend imports work correctly"""
    try:
        sys.path.insert(0, str(Path.cwd()))
        from app.main import app
        from app.schemas import ShipmentCreate, ShipmentRead, User
        from app.auth import get_password_hash, verify_password
        print("✅ Backend imports successful")
        return True
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        return False

def test_schema_compatibility():
    """Test that frontend and backend schemas are compatible"""
    try:
        from app.schemas import ShipmentCreate, ShipmentRead
        
        # Test ShipmentCreate fields
        required_fields = {'tracking_number', 'status', 'origin', 'destination', 'weight'}
        create_fields = set(ShipmentCreate.__fields__.keys())
        
        if required_fields.issubset(create_fields):
            print("✅ ShipmentCreate schema compatibility verified")
        else:
            missing = required_fields - create_fields
            print(f"❌ Missing fields in ShipmentCreate: {missing}")
            return False
            
        # Test ShipmentRead fields
        read_fields = set(ShipmentRead.__fields__.keys())
        expected_read_fields = required_fields | {'id', 'created_at', 'updated_at'}
        
        if expected_read_fields.issubset(read_fields):
            print("✅ ShipmentRead schema compatibility verified")
        else:
            missing = expected_read_fields - read_fields
            print(f"❌ Missing fields in ShipmentRead: {missing}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Schema compatibility error: {e}")
        return False

def test_frontend_files():
    """Test that frontend files have correct structure"""
    frontend_path = Path("frontend")
    
    # Check main.ts
    main_ts = frontend_path / "src" / "main.ts"
    if main_ts.exists():
        content = main_ts.read_text()
        if "import router from './router'" in content and "createRouter" not in content:
            print("✅ main.ts router configuration fixed")
        else:
            print("❌ main.ts still has duplicate router configuration")
            return False
    else:
        print("❌ main.ts not found")
        return False
    
    # Check router/index.ts
    router_ts = frontend_path / "src" / "router" / "index.ts"
    if router_ts.exists():
        content = router_ts.read_text()
        if "localStorage.getItem('token')" in content and "authService" not in content:
            print("✅ router/index.ts authentication fixed")
        else:
            print("❌ router/index.ts still has authService import issues")
            return False
    else:
        print("❌ router/index.ts not found")
        return False
    
    # Check ShipmentsView.vue
    shipments_vue = frontend_path / "src" / "views" / "ShipmentsView.vue"
    if shipments_vue.exists():
        content = shipments_vue.read_text()
        if "tracking_number" in content and "shipment.content" not in content:
            print("✅ ShipmentsView.vue data model fixed")
        else:
            print("❌ ShipmentsView.vue still has data model issues")
            return False
    else:
        print("❌ ShipmentsView.vue not found")
        return False
    
    return True

def test_api_service():
    """Test that API service has correct methods"""
    api_ts = Path("frontend/src/services/api.ts")
    if api_ts.exists():
        content = api_ts.read_text()
        if "getAllShipments" in content and "getShipments" in content:
            print("✅ API service method compatibility fixed")
            return True
        else:
            print("❌ API service missing getAllShipments method")
            return False
    else:
        print("❌ api.ts not found")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing fixes...")
    print("=" * 50)
    
    tests = [
        test_backend_imports,
        test_schema_compatibility,
        test_frontend_files,
        test_api_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All fixes verified successfully!")
        print("\nNext steps:")
        print("1. Start backend: myvenv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open browser to http://localhost:5173")
        print("4. Login with: testuser / password123")
    else:
        print("❌ Some issues remain. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
