@echo off
echo Starting Backend Server...
echo ========================

cd /d "%~dp0"
echo Current directory: %CD%

echo.
echo Activating virtual environment...
call myvenv\Scripts\activate.bat

echo.
echo Starting uvicorn server...
echo Command: python -m uvicorn app.main:app --reload --port 8001 --host 127.0.0.1
echo.

python -m uvicorn app.main:app --reload --port 8001 --host 127.0.0.1

echo.
echo Server stopped.
pause
