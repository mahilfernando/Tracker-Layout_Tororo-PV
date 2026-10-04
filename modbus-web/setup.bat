@echo off
rem One-time setup: creates venv\ (Python for this project only) and installs the libraries.
cd /d "%~dp0"
where python >nul 2>nul || (echo Python not found. Install it from python.org and tick "Add python.exe to PATH". & pause & exit /b 1)
python --version
if not exist venv\Scripts\python.exe (
  echo Creating virtual environment in %CD%\venv ...
  python -m venv venv || (echo venv failed. Move this folder to a short path such as C:\tracker\modbus-web and try again. & pause & exit /b 1)
)
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Library install failed. Check the internet connection. & pause & exit /b 1)
echo.
echo Setup complete. Double-click demo.bat to try it with the simulator.
pause
