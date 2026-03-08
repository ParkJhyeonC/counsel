@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0..
set VENV_DIR=%ROOT_DIR%\.venv

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python Launcher(py)를 찾을 수 없습니다. Python 3.10+ 설치 후 다시 시도하세요.
  exit /b 1
)

if not exist "%VENV_DIR%" (
  echo [INFO] 가상환경 생성: %VENV_DIR%
  py -3 -m venv "%VENV_DIR%"
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

python -m pip install -r "%ROOT_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

cd /d "%ROOT_DIR%"
python -c "from app import init_db; init_db(); print('[INFO] DB 초기화 확인 완료')"
if errorlevel 1 exit /b 1

python app.py
