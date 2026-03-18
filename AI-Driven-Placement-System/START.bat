@echo off
REM AI Driven Placement & Career Intelligence System - Start All Services
REM This script starts the main portal and all Streamlit modules

cd /d "%~dp0"

echo.
echo ========================================
echo   AI Driven Placement & Career Intelligence System - Starting All Services
echo ========================================
echo.

echo [1/4] Starting Node.js Server (Port 3000)...
start "AI Driven Placement & Career Intelligence System Portal" node server.js

timeout /t 2 /nobreak

echo [2/4] Starting Aptitude Module (Port 8501)...
start "Aptitude Questions" cmd /k "cd Aptitude && C:/Users/ASUS/AppData/Local/Programs/Python/Python312/python.exe -m streamlit run AptiApp_Simple.py --server.port=8501"

timeout /t 2 /nobreak

echo [3/4] Starting DSA Module (Port 8502)...
start "DSA Practice" cmd /k "cd CodingPract && C:/Users/ASUS/AppData/Local/Programs/Python/Python312/python.exe -m streamlit run DSA_dash_Simple.py --server.port=8502"

timeout /t 2 /nobreak

echo [4/4] Starting Mock Interview Module (Port 8503)...
start "Mock Interview" cmd /k "cd MockInter && C:/Users/ASUS/AppData/Local/Programs/Python/Python312/python.exe -m streamlit run app.py --server.port=8503"

timeout /t 2 /nobreak

echo.
echo ========================================
echo     All Services Started Successfully!
echo ========================================
echo.
echo Access your services:
echo.
echo   Main Portal:       http://localhost:3000
echo   Aptitude:         http://localhost:8501
echo   DSA Practice:     http://localhost:8502
echo   Mock Interview:   http://localhost:8503
echo.
echo Press any key to close this window...
pause
