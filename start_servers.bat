@echo off
echo Starting Shipment Management System...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "myvenv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:5173
echo.
echo Login with: testuser / password123
echo.
pause
