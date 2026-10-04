@echo off
rem Test mode: reads 20 registers and shows them at http://localhost:8000/raw.html
rem Change these to match your device:
set IP=192.168.1.21
set UNIT=1
set START=45000
set COUNT=20
rem ONE_BASED=--one-based makes 45000 mean the same register as in Modbus Poll
rem (wire address 4999). Leave it empty for PVH-manual style (45000 = wire 5000).
set ONE_BASED=--one-based
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Run setup.bat first. & pause & exit /b 1)
start "Raw poller" cmd /k venv\Scripts\python.exe raw_poller.py --ip %IP% --unit %UNIT% --start %START% --count %COUNT% %ONE_BASED%
start "Web server" cmd /k venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000
timeout /t 4 >nul
start http://localhost:8000/raw.html
