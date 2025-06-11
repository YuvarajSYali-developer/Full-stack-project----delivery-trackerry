#!/usr/bin/env python3
"""
Simple script to start the backend server with proper error handling
"""

import sys
import os
import subprocess
import time

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Shipment Management Backend Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("❌ Error: app/main.py not found. Make sure you're in the project root directory.")
        return False
    
    # Check if virtual environment exists
    venv_python = "myvenv\\Scripts\\python.exe"
    if not os.path.exists(venv_python):
        print("❌ Error: Virtual environment not found. Using system Python.")
        venv_python = "python"
    else:
        print("✅ Using virtual environment Python")
    
    # Try to import the app first
    print("🔍 Testing app import...")
    try:
        result = subprocess.run([
            venv_python, "-c", 
            "from app.main import app; print('✅ App imported successfully')"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ App import failed: {result.stderr}")
            return False
        else:
            print(result.stdout.strip())
    except subprocess.TimeoutExpired:
        print("❌ App import timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing app import: {e}")
        return False
    
    # Start the server
    print("🌐 Starting uvicorn server...")
    try:
        cmd = [
            venv_python, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--port", "8001",
            "--host", "127.0.0.1"
        ]
        
        print(f"Command: {' '.join(cmd)}")
        print("=" * 50)
        
        # Start the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        print("Server output:")
        print("-" * 30)
        
        for line in process.stdout:
            print(line.rstrip())
            if "Uvicorn running on" in line:
                print("✅ Server started successfully!")
                break
        
        # Keep the process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            process.terminate()
            process.wait()
            
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Installing uvicorn...")
        try:
            subprocess.run([venv_python, "-m", "pip", "install", "uvicorn"], check=True)
            print("✅ uvicorn installed. Please run the script again.")
        except Exception as e:
            print(f"❌ Failed to install uvicorn: {e}")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
