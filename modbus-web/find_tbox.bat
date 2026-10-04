@echo off
rem Scans 192.168.1.x for Modbus devices and shows which one answers like a PVH TBox.
cd /d "%~dp0"
if not exist venv\Scripts\python.exe (echo Run setup.bat first. & pause & exit /b 1)
venv\Scripts\python.exe find_tbox.py --subnet 192.168.1
pause
