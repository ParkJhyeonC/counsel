@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.." || goto :error_root
set "ROOT_DIR=%CD%"
set "VENV_DIR=%ROOT_DIR%\.venv"
set "TRAY_PS1=%SCRIPT_DIR%run_tray_windows.ps1"
set "TRAY_SERVER=%SCRIPT_DIR%run_tray_server.py"

echo [INFO] Project root: %ROOT_DIR%

if not exist "%ROOT_DIR%\app.py" goto :error_layout
if not exist "%ROOT_DIR%\templates\index.html" goto :error_layout
if not exist "%ROOT_DIR%\static\style.css" goto :error_layout
if not exist "%TRAY_PS1%" goto :error_layout
if not exist "%TRAY_SERVER%" goto :error_layout

where py >nul 2>nul
if %errorlevel%==0 goto :use_py_launcher
where python >nul 2>nul
if %errorlevel%==0 goto :use_python

echo [ERROR] Python not found. Install Python 3.10+.
goto :error

:use_py_launcher
set "PY_CMD=py -3"
goto :prepare

:use_python
set "PY_CMD=python"
goto :prepare

:prepare
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Creating venv...
  %PY_CMD% -m venv "%VENV_DIR%" || goto :error
)

call "%VENV_DIR%\Scripts\activate.bat" || goto :error
python -m pip install --upgrade pip || goto :error
python -m pip install -r requirements.txt || goto :error
python -c "from app import init_db; init_db(); print('[INFO] DB initialization OK')" || goto :error

powershell -NoProfile -ExecutionPolicy Bypass -File "%TRAY_PS1%" -RootDir "%ROOT_DIR%" -PythonExe "%VENV_DIR%\Scripts\python.exe"
exit /b %errorlevel%

:error_root
echo [ERROR] Cannot access project root from scripts folder.
goto :error

:error_layout
echo [ERROR] Project layout is invalid. Required files:
echo        %ROOT_DIR%\app.py
echo        %ROOT_DIR%\templates\index.html
echo        %ROOT_DIR%\static\style.css
echo        %TRAY_PS1%
echo        %TRAY_SERVER%
goto :error

:error
echo.
echo [INFO] 전문상담교사 박재현 제공
echo [HINT] Press any key to close this window...
pause >nul
exit /b 1
