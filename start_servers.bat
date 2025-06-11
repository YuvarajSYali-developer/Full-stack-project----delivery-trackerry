@echo off
echo 🇮🇳 Starting Indian Shipment Management System...
echo.

echo 🚀 Starting Enhanced Backend Server...
start "Indian Backend Server" cmd /k "python working_server.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo 🎨 Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both servers are starting...
echo 🔧 Backend: http://localhost:8001
echo 🎨 Frontend: http://localhost:5173
echo 📚 API Docs: http://localhost:8001/docs
echo.
echo 🔑 Login Credentials:
echo    Admin: admin / admin123 (Rahul Sharma)
echo    Manager: manager / manager123 (Anita Desai)
echo    Customer: testuser / password123 (Demo User)
echo.
echo 🇮🇳 Fully localized for India with 50 shipments and 8 customers!
echo.
pause
