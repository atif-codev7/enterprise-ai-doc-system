@echo off
title Launch Enterprise AI Doc System (Ports 8002 & 3002)
echo ========================================================
echo Launching Project 3: Enterprise AI Doc System
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3002
echo ========================================================

start "DocIntel Backend (FastAPI :8002)" cmd /c "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "DocIntel Frontend (Next.js :3002)" cmd /c "%~dp0start_frontend.bat"
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:3002...
start http://localhost:3002
