@echo off
REM Quick Start Script for Code Smell Detection System
REM Windows Batch Script

echo ========================================
echo Code Smell Detection - Quick Start
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Python and Node.js detected
echo.

echo ========================================
echo Step 1: Creating Python Virtual Environment
echo ========================================
python -m venv venv
call venv\Scripts\activate.bat
echo [OK] Virtual environment created and activated
echo.

echo ========================================
echo Step 2: Installing Python Dependencies
echo ========================================
pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Python dependencies installed
echo.

echo ========================================
echo Step 3: Setting Up Frontend
echo ========================================
cd frontend
npm install
copy .env.example .env
echo [OK] Frontend dependencies installed
cd ..
echo.

echo ========================================
echo Step 4: Starting Services
echo ========================================
echo.
echo To start the application, use two separate terminal windows:
echo.
echo Terminal 1 - Backend Server:
echo   1. Make sure virtual environment is activated: venv\Scripts\activate.bat
echo   2. Navigate to backend: cd backend
echo   3. Run: python app.py
echo.
echo Terminal 2 - Frontend Application:
echo   1. Navigate to frontend: cd frontend
echo   2. Run: npm start
echo.
echo The frontend will open at: http://localhost:3000
echo The backend API will be at: http://localhost:5000
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.

pause
