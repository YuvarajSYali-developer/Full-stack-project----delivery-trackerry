#!/usr/bin/env python3
"""
Simple server runner that shows output
"""

import subprocess
import sys
import time

def run_server():
    """Run the server with visible output"""
    print("🚀 Starting Backend Server...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--port", "8001",
        "--host", "127.0.0.1",
        "--log-level", "info"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        # Run the server and show output
        process = subprocess.run(cmd, check=False)
        return process.returncode
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running server: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_server()
    sys.exit(exit_code)
