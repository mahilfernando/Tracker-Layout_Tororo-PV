@echo off
rem Runs the simulator, the poller and the web server, then opens the dashboard.
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Run setup.bat first. & pause & exit /b 1)
start "Simulator" cmd /k venv\Scripts\python.exe simulator.py
timeout /t 2 >nul
start "Poller" cmd /k "set MODBUS_IP=127.0.0.1&& set MODBUS_PORT=5020&& venv\Scripts\python.exe poller.py"
start "Web server" cmd /k venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
timeout /t 4 >nul
start http://localhost:8000
