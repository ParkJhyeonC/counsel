@echo off
setlocal

REM Ensure predictable output encoding in Korean Windows terminals.
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"
set "VENV_DIR=%ROOT_DIR%\.venv"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=python"
  ) else (
    echo [ERROR] Python executable not found. Install Python 3.10+ and try again.
    exit /b 1
  )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Creating virtual environment: "%VENV_DIR%"
  %PY_CMD% -m venv "%VENV_DIR%"
  if errorlevel 1 exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 exit /b 1

cd /d "%ROOT_DIR%"
if errorlevel 1 (
  echo [ERROR] Failed to change directory to "%ROOT_DIR%".
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

python -c "from app import init_db; init_db(); print('[INFO] DB initialization OK')"
if errorlevel 1 exit /b 1

echo [INFO] Starting app at http://localhost:5000
python app.py
