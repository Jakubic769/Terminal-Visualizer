@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Terminal Visualizer Installer

echo ==============================================
echo  Terminal Visualizer - Windows installer
echo ==============================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    set "PY=py"
    set "PY_ARGS=-3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python 3.9+ was not found.
        echo Install Python from https://www.python.org/downloads/
        echo Make sure Python is added to PATH.
        pause
        exit /b 1
    )
    set "PY=python"
    set "PY_ARGS="
)

echo [INFO] Checking Python version...
%PY% %PY_ARGS% -c "import sys; raise SystemExit(0 if sys.version_info^>=(3,9) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.9 or newer is required.
    pause
    exit /b 1
)

set "INSTALL_DIR=%LOCALAPPDATA%\TerminalVisualizer"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "BIN_DIR=%INSTALL_DIR%\bin"
set "SCRIPT_DIR=%~dp0"

echo [INFO] Installing to:
echo        %INSTALL_DIR%
echo.

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

echo [INFO] Creating isolated Python environment...
%PY% %PY_ARGS% -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo [ERROR] Could not create Python virtual environment.
    pause
    exit /b 1
)

echo [INFO] Updating pip/setuptools/wheel...
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] pip bootstrap failed.
    pause
    exit /b 1
)

echo [INFO] Installing Terminal Visualizer and dependencies...
"%VENV_DIR%\Scripts\python.exe" -m pip install "%SCRIPT_DIR%"
if errorlevel 1 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)

echo [INFO] Creating command launcher...
> "%BIN_DIR%\visualizer.cmd" echo @echo off
>>"%BIN_DIR%\visualizer.cmd" echo "%VENV_DIR%\Scripts\visualizer.exe" %%*

echo [INFO] Adding Terminal Visualizer to your USER PATH...
rem Use Python to edit the user PATH safely instead of setx, which can truncate long PATHs.
"%PY%" %PY_ARGS% -c "import os,winreg; p=os.path.expandvars(r'%BIN_DIR%'); k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Environment',0,winreg.KEY_READ^|winreg.KEY_SET_VALUE); old=winreg.QueryValueEx(k,'Path')[0] if True else ''; parts=[x for x in old.split(';') if x]; parts2=[x for x in parts if os.path.normcase(x)!=os.path.normcase(p)]; parts2.insert(0,p); winreg.SetValueEx(k,'Path',0,winreg.REG_EXPAND_SZ,';'.join(parts2)); winreg.CloseKey(k)"
if errorlevel 1 (
    echo [WARN] Could not update USER PATH automatically.
    echo Add this directory manually:
    echo %BIN_DIR%
) else (
    echo [OK] USER PATH updated.
)

echo.
echo ==============================================
echo  Installation complete!
echo ==============================================
echo.
echo Close this terminal and open a NEW terminal.
echo Then run:
echo.
echo     visualizer
echo.
echo Test without real audio:
echo     visualizer --demo
echo.
echo NOTE: Windows 10/11 is required.
echo.
pause
