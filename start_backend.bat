@echo off
title DocIntel AI Backend (FastAPI - Port 8002)
echo ========================================================
echo Starting Enterprise AI Doc Intel Backend on port 8002...
echo (Port 8000: PayGuard, Port 8001: Webhook, Port 8002: DocIntel)
echo ========================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
pause
