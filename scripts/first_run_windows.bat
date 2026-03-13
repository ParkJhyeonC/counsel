@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.." >nul 2>nul || goto :error_root
set "ROOT_DIR=%CD%"
popd >nul 2>nul
set "RUN_BAT=%ROOT_DIR%\scripts\run.bat"

echo [INFO] First-run helper (Windows)
echo [INFO] Project root: %ROOT_DIR%

if not exist "%RUN_BAT%" (
  echo [ERROR] scripts\run.bat not found.
  goto :error
)

call :detect_python
if defined PY_OK goto :run

echo [INFO] Python 3 not found. Trying auto-install with winget...
where winget >nul 2>nul
if not errorlevel 1 (
  winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements
  call :detect_python
  if defined PY_OK goto :run
)

echo [WARN] winget auto-install failed or unavailable.
echo [ACTION] Open Python download page. Install Python 3.10+ and check:
echo          "Add python.exe to PATH"
start "" https://www.python.org/downloads/windows/

echo.
echo [HINT] Python install complete 후, 이 창으로 돌아와 아무 키를 누르세요.
pause >nul
call :detect_python
if defined PY_OK goto :run

echo [ERROR] Python still not detected.
goto :error

:detect_python
set "PY_OK="
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; print(sys.version)" >nul 2>nul
  if not errorlevel 1 set "PY_OK=1"
)
if not defined PY_OK (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; print(sys.version)" >nul 2>nul
    if not errorlevel 1 set "PY_OK=1"
  )
)
exit /b 0

:run
echo [INFO] Python detected. Starting standard runner...
call "%RUN_BAT%"
exit /b %errorlevel%

:error_root
echo [ERROR] Cannot access project root from scripts folder.
goto :error

:error
echo.
echo [HINT] Press any key to close this window...
pause >nul
exit /b 1
