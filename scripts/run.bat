@echo off
setlocal

chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
set "KEEP_OPEN_ON_ERROR=1"

pushd "%ROOT_DIR%" >nul 2>nul
if errorlevel 1 goto :root_error
set "ROOT_DIR=%CD%"
set "VENV_DIR=%ROOT_DIR%\.venv"

echo [INFO] Using project root: "%ROOT_DIR%"

if not exist "%ROOT_DIR%\app.py" goto :layout_error
if not exist "%ROOT_DIR%\templates\index.html" goto :layout_error
if not exist "%ROOT_DIR%\static\style.css" goto :layout_error

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_CMD=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_CMD=python"
  ) else (
    echo [ERROR] Python executable not found. Install Python 3.10+ and try again.
    goto :error
  )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [INFO] Creating virtual environment: "%VENV_DIR%"
  %PY_CMD% -m venv "%VENV_DIR%"
  if errorlevel 1 goto :error
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 goto :error

python -m pip install --upgrade pip
if errorlevel 1 goto :error

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

python -c "from app import init_db; init_db(); print('[INFO] DB initialization OK')"
if errorlevel 1 goto :error

echo [INFO] Starting app at http://localhost:5000
start "" http://localhost:5000
python app.py

popd
exit /b 0

:root_error
echo [ERROR] Failed to access project root: "%ROOT_DIR%"
goto :error

:layout_error
echo [ERROR] Project structure invalid. Check files below:
echo         - "%ROOT_DIR%\app.py"
echo         - "%ROOT_DIR%\templates\index.html"
echo         - "%ROOT_DIR%\static\style.css"
goto :error

:error
if defined ROOT_DIR popd >nul 2>nul
if "%KEEP_OPEN_ON_ERROR%"=="1" (
  echo.
  echo [HINT] 오류 확인 후 아무 키나 누르면 창이 닫힙니다.
  pause >nul
)
exit /b 1
