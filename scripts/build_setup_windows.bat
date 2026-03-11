@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.." >nul 2>nul || goto :error_root
set "ROOT_DIR=%CD%"

set "VENV_PY=%ROOT_DIR%\.venv\Scripts\python.exe"
set "VENV_PIP=%ROOT_DIR%\.venv\Scripts\pip.exe"
set "ISCC_EXE="
set "SIGNTOOL_EXE="
if exist "%ProgramFiles(x86)%\Windows Kits\10\bin\x64\signtool.exe" set "SIGNTOOL_EXE=%ProgramFiles(x86)%\Windows Kits\10\bin\x64\signtool.exe"
if not defined SIGNTOOL_EXE if exist "%ProgramFiles%\Windows Kits\10\bin\x64\signtool.exe" set "SIGNTOOL_EXE=%ProgramFiles%\Windows Kits\10\bin\x64\signtool.exe"
set "SIGN_PFX=%SIGN_PFX%"
set "SIGN_PFX_PASSWORD=%SIGN_PFX_PASSWORD%"

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC_EXE if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"

echo [INFO] Windows setup build helper
echo [INFO] Root: %ROOT_DIR%

if not exist "%VENV_PY%" (
  echo [INFO] .venv not found. Creating venv for build...
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 -m venv "%ROOT_DIR%\.venv" || goto :error
  ) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
      python -m venv "%ROOT_DIR%\.venv" || goto :error
    ) else (
      echo [ERROR] Python not found. Install Python 3.10+.
      goto :error
    )
  )
)

if not exist "%VENV_PIP%" (
  echo [ERROR] venv pip not found: %VENV_PIP%
  goto :error
)

echo [INFO] Installing build dependency: pyinstaller
"%VENV_PIP%" install pyinstaller
if errorlevel 1 goto :error

echo [INFO] Building standalone app folder with PyInstaller...
if exist "%ROOT_DIR%\build" rmdir /s /q "%ROOT_DIR%\build"
if exist "%ROOT_DIR%\dist" rmdir /s /q "%ROOT_DIR%\dist"
if exist "%ROOT_DIR%\counselog.spec" del /q "%ROOT_DIR%\counselog.spec"

"%VENV_PY%" -m PyInstaller --noconfirm --clean --windowed --name counselog --onedir --hidden-import holidays --add-data "templates;templates" --add-data "static;static" app.py
if errorlevel 1 goto :error


call :maybe_sign "%ROOT_DIR%\dist\counselog\counselog.exe"
if errorlevel 1 goto :error

if defined ISCC_EXE (
  echo [INFO] Inno Setup detected. Building Setup.exe...
  "%ISCC_EXE%" "%ROOT_DIR%\installer\counsel_setup.iss"
  if errorlevel 1 goto :error
  call :maybe_sign "%ROOT_DIR%\dist\counselog_setup.exe"
  if errorlevel 1 goto :error
  echo [DONE] Setup created: %ROOT_DIR%\dist\counselog_setup.exe
) else (
  echo [WARN] Inno Setup 6 not found. Portable build only.
  echo [DONE] Portable app folder: %ROOT_DIR%\dist\counselog
  echo [HINT] Install Inno Setup 6, then rerun this script to generate Setup.exe
)

goto :done

:maybe_sign
set "TARGET_FILE=%~1"
if not exist "%TARGET_FILE%" exit /b 0
if not defined SIGNTOOL_EXE exit /b 0
if not defined SIGN_PFX exit /b 0

echo [INFO] Signing: %TARGET_FILE%
if defined SIGN_PFX_PASSWORD (
  "%SIGNTOOL_EXE%" sign /f "%SIGN_PFX%" /p "%SIGN_PFX_PASSWORD%" /fd sha256 /tr http://timestamp.digicert.com /td sha256 "%TARGET_FILE%"
) else (
  "%SIGNTOOL_EXE%" sign /f "%SIGN_PFX%" /fd sha256 /tr http://timestamp.digicert.com /td sha256 "%TARGET_FILE%"
)
if errorlevel 1 (
  echo [ERROR] Code signing failed: %TARGET_FILE%
  exit /b 1
)
exit /b 0

:error_root
echo [ERROR] Cannot access project root from scripts folder.
goto :error

:error
echo.
echo [ERROR] Build failed.
exit /b 1

:done
popd >nul 2>nul
echo.
echo [HINT] Press any key to close this window...
pause >nul
exit /b 0
