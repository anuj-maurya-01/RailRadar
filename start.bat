@echo off
echo ===================================================
echo Starting YatriRail -- Live Indian Railway Intelligence
echo ===================================================

echo [1/2] Launching FastAPI Backend on http://localhost:8000 ...
start "FastAPI Backend" cmd /k "cd /d %~dp0\backend && ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Launching React Frontend on http://localhost:5173 ...
start "React Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo ===================================================
echo Services are running:
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo ===================================================
