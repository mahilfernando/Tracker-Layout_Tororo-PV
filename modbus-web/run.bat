@echo off
rem Runs the poller and web server against the REAL device set in config.py.
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Run setup.bat first. & pause & exit /b 1)
start "Poller" cmd /k venv\Scripts\python.exe poller.py
start "Web server" cmd /k venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
timeout /t 4 >nul
start http://localhost:8000
