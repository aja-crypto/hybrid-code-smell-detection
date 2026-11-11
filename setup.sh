#!/bin/bash
# Quick Start Script for Code Smell Detection System
# macOS and Linux Bash Script

echo "========================================"
echo "Code Smell Detection - Quick Start"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    echo "Please install Python 3.9+ from https://www.python.org"
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

echo "[OK] Python3 and Node.js detected"
echo ""

echo "========================================"
echo "Step 1: Creating Python Virtual Environment"
echo "========================================"
python3 -m venv venv
source venv/bin/activate
echo "[OK] Virtual environment created and activated"
echo ""

echo "========================================"
echo "Step 2: Installing Python Dependencies"
echo "========================================"
pip install --upgrade pip
pip install -r requirements.txt
echo "[OK] Python dependencies installed"
echo ""

echo "========================================"
echo "Step 3: Setting Up Frontend"
echo "========================================"
cd frontend
npm install
cp .env.example .env
cd ..
echo "[OK] Frontend dependencies installed"
echo ""

echo "========================================"
echo "Step 4: Starting Services"
echo "========================================"
echo ""
echo "To start the application, use two separate terminal windows:"
echo ""
echo "Terminal 1 - Backend Server:"
echo "  1. source venv/bin/activate"
echo "  2. cd backend"
echo "  3. python app.py"
echo ""
echo "Terminal 2 - Frontend Application:"
echo "  1. cd frontend"
echo "  2. npm start"
echo ""
echo "The frontend will open at: http://localhost:3000"
echo "The backend API will be at: http://localhost:5000"
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
