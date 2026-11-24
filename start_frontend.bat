@echo off
title DocIntel AI Frontend (Next.js - Port 3002)
echo ========================================================
echo Starting Enterprise AI Doc Intel Frontend on port 3002...
echo (Port 3000: PayGuard, Port 3001: Webhook, Port 3002: DocIntel)
echo ========================================================
cd /d "%~dp0frontend"
npm run dev
pause
