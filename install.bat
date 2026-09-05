@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Terminal Visualizer Installer

REM ============================================================
REM Logging setup
REM ============================================================
set "INSTALL_DIR=%LOCALAPPDATA%\TerminalVisualizer"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "BIN_DIR=%INSTALL_DIR%\bin"
set "LOG_FILE=%INSTALL_DIR%\install.log"
set "SCRIPT_DIR=%~dp0"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
(
echo ==============================================
echo  Terminal Visualizer - Windows Installer
echo  Started: %date% %time%
echo ==============================================
echo.
) > "%LOG_FILE%"

call :log "[INFO] Searching for Python 3.9+..."

REM ============================================================
REM 1. Find Python 3.9+
REM ============================================================
set "PY="
set "PY_ARGS="

REM Try py launcher first
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
    if not errorlevel 1 (
        set "PY=py"
        set "PY_ARGS=-3"
        call :log "[OK] Found Python via 'py -3'"
    )
)

REM Try python
if not defined PY (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
        if not errorlevel 1 (
            set "PY=python"
            call :log "[OK] Found Python via 'python'"
        )
    )
)

REM Try python3 (Git Bash / MSYS2)
if not defined PY (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)" >nul 2>&1
        if not errorlevel 1 (
            set "PY=python3"
            call :log "[OK] Found Python via 'python3'"
        )
    )
)

REM Search common install locations
if not defined PY (
    for %%V in (314 313 312 311 310 39) do (
        if not defined PY (
            for %%B in ("%LocalAppData%\Programs\Python" "%ProgramFiles%") do (
                if exist "%%~B\Python%%V\python.exe" (
                    set "PY=%%~B\Python%%V\python.exe"
                    call :log "[OK] Found Python at %%~B\Python%%V\python.exe"
                    goto :found_py
                )
            )
        )
    )
)
:found_py

if not defined PY (
    call :log "[ERROR] Python 3.9+ not found."
    call :log "Install from: https://www.python.org/downloads/"
    call :log "Make sure to check 'Add Python to PATH' during installation."
    echo.
    echo [ERROR] Python 3.9+ was not found.
    echo Install from: https://www.python.org/downloads/
    echo Make sure Python is added to PATH.
    pause
    exit /b 1
)

echo [OK] Python found: %PY%
call :log "[OK] Python executable: %PY%"

REM ============================================================
REM 2. Verify Python version
REM ============================================================
call :log "[INFO] Verifying Python version..."
%PY% --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "[ERROR] Could not run Python."
    echo [ERROR] Could not run Python.
    pause
    exit /b 1
)

%PY% -c "import sys; raise SystemExit(0 if sys.version_info >= (3,9) else 1)"
if errorlevel 1 (
    call :log "[ERROR] Python 3.9+ is required."
    echo [ERROR] Python 3.9 or newer is required.
    pause
    exit /b 1
)

call :log "[OK] Python version is sufficient."

REM ============================================================
REM 3. Check project files
REM ============================================================
if not exist "%SCRIPT_DIR%pyproject.toml" (
    if not exist "%SCRIPT_DIR%setup.py" (
        call :log "[ERROR] No pyproject.toml or setup.py found in %SCRIPT_DIR%"
        echo [ERROR] No pyproject.toml or setup.py found.
        echo Make sure this installer is inside the project directory.
        pause
        exit /b 1
    )
)

call :log "[OK] Project files found in %SCRIPT_DIR%"

REM ============================================================
REM 4. Create directories
REM ============================================================
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

REM ============================================================
REM 5. Create virtual environment
REM ============================================================
call :log "[INFO] Creating virtual environment at %VENV_DIR%..."

if exist "%VENV_DIR%\Scripts\python.exe" (
    call :log "[INFO] Existing venv found, reusing."
    echo [INFO] Existing virtual environment found. Reusing it.
) else (
    %PY% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "[ERROR] Failed to create virtual environment."
        echo [ERROR] Could not create virtual environment.
        pause
        exit /b 1
    )
    call :log "[OK] Virtual environment created."
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    call :log "[ERROR] venv\Scripts\python.exe missing after creation."
    echo [ERROR] Virtual environment was not created correctly.
    pause
    exit /b 1
)

echo [OK] Virtual environment ready.

REM ============================================================
REM 6. Upgrade pip
REM ============================================================
echo.
echo [INFO] Updating pip, setuptools, wheel...
call :log "[INFO] Upgrading pip..."

"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "[WARN] pip upgrade had issues, continuing..."
    echo [WARN] pip upgrade had issues, continuing anyway...
) else (
    call :log "[OK] pip upgraded."
)

REM ============================================================
REM 7. Install Terminal Visualizer
REM ============================================================
echo.
echo [INFO] Installing Terminal Visualizer...
call :log "[INFO] Running pip install %SCRIPT_DIR%"

pushd "%SCRIPT_DIR%"
"%VENV_DIR%\Scripts\python.exe" -m pip install . >> "%LOG_FILE%" 2>&1
set "PIP_RESULT=%ERRORLEVEL%"
popd

if %PIP_RESULT% neq 0 (
    call :log "[ERROR] pip install failed with code %PIP_RESULT%"
    echo.
    echo [ERROR] Package installation failed.
    echo Check install.log for details:
    echo %LOG_FILE%
    pause
    exit /b 1
)

call :log "[OK] Package installed successfully."
echo [OK] Terminal Visualizer installed.

REM ============================================================
REM 8. Detect installed entry point
REM ============================================================
set "ENTRY_POINT="

if exist "%VENV_DIR%\Scripts\visualizer.exe" (
    set "ENTRY_POINT=%VENV_DIR%\Scripts\visualizer.exe"
    call :log "[OK] Found entry point: visualizer.exe"
) else if exist "%VENV_DIR%\Scripts\visualizer-script.py" (
    set "ENTRY_POINT=%VENV_DIR%\Scripts\python.exe %VENV_DIR%\Scripts\visualizer-script.py"
    call :log "[OK] Found entry point: visualizer-script.py"
) else if exist "%VENV_DIR%\Scripts\visualizer" (
    set "ENTRY_POINT=%VENV_DIR%\Scripts\python.exe %VENV_DIR%\Scripts\visualizer"
    call :log "[OK] Found entry point: visualizer (script)"
) else (
    REM Fallback: python -m visualizer.cli
    set "ENTRY_POINT=%VENV_DIR%\Scripts\python.exe -m visualizer.cli"
    call :log "[INFO] No entry point script found, using fallback: python -m visualizer.cli"
)

REM ============================================================
REM 9. Create launcher
REM ============================================================
echo.
echo [INFO] Creating command launcher...
call :log "[INFO] Creating launcher at %BIN_DIR%\visualizer.cmd"

> "%BIN_DIR%\visualizer.cmd" echo @echo off
>>"%BIN_DIR%\visualizer.cmd" echo %ENTRY_POINT% %%*

if not exist "%BIN_DIR%\visualizer.cmd" (
    call :log "[ERROR] Could not create launcher."
    echo [ERROR] Could not create visualizer.cmd
    pause
    exit /b 1
)

call :log "[OK] Launcher created."
echo [OK] Launcher created.

REM ============================================================
REM 10. Update USER PATH via temporary Python script
REM ============================================================
echo.
echo [INFO] Adding to USER PATH...
call :log "[INFO] Updating USER PATH..."

set "PATH_PY=%TEMP%\tv_update_path_%RANDOM%.py"

> "%PATH_PY%" echo import os, winreg, sys, ctypes
>>"%PATH_PY%" echo try:
>>"%PATH_PY%" echo     p = os.path.normpath(r'%BIN_DIR%')
>>"%PATH_PY%" echo     k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ ^| winreg.KEY_SET_VALUE)
>>"%PATH_PY%" echo     try:
>>"%PATH_PY%" echo         old, _ = winreg.QueryValueEx(k, 'Path')
>>"%PATH_PY%" echo     except FileNotFoundError:
>>"%PATH_PY%" echo         old = ''
>>"%PATH_PY%" echo     parts = [x.strip() for x in old.split(';') if x.strip()]
>>"%PATH_PY%" echo     parts_lower = [os.path.normcase(os.path.normpath(x)) for x in parts]
>>"%PATH_PY%" echo     target_lower = os.path.normcase(os.path.normpath(p))
>>"%PATH_PY%" echo     if target_lower not in parts_lower:
>>"%PATH_PY%" echo         parts.insert(0, p)
>>"%PATH_PY%" echo         new_path = ';'.join(parts)
>>"%PATH_PY%" echo         winreg.SetValueEx(k, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
>>"%PATH_PY%" echo         print('PATH_UPDATED')
>>"%PATH_PY%" echo     else:
>>"%PATH_PY%" echo         print('PATH_ALREADY_OK')
>>"%PATH_PY%" echo     winreg.CloseKey(k)
>>"%PATH_PY%" echo     HWND_BROADCAST = 0xFFFF
>>"%PATH_PY%" echo     WM_SETTINGCHANGE = 0x1A
>>"%PATH_PY%" echo     SMTO_ABORTIFHUNG = 0x0002
>>"%PATH_PY%" echo     result = ctypes.c_long()
>>"%PATH_PY%" echo     ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
>>"%PATH_PY%" echo except Exception as e:
>>"%PATH_PY%" echo     print('PATH_ERROR:', e)
>>"%PATH_PY%" echo     sys.exit(0)

%PY% "%PATH_PY%" > "%TEMP%\tv_path_result.txt" 2>&1
set "PATH_RESULT="
if exist "%TEMP%\tv_path_result.txt" (
    set /p PATH_RESULT=<"%TEMP%\tv_path_result.txt"
)
del /f /q "%PATH_PY%" >nul 2>&1
del /f /q "%TEMP%\tv_path_result.txt" >nul 2>&1

if "%PATH_RESULT%"=="PATH_UPDATED" (
    call :log "[OK] USER PATH updated."
    echo [OK] USER PATH updated.
) else if "%PATH_RESULT%"=="PATH_ALREADY_OK" (
    call :log "[OK] Already in USER PATH."
    echo [OK] Already in USER PATH.
) else (
    call :log "[WARN] Could not update PATH automatically: %PATH_RESULT%"
    echo [WARN] Could not update PATH automatically.
    echo Add this directory manually to PATH:
    echo %BIN_DIR%
)

REM ============================================================
REM 11. Verify launcher works
REM ============================================================
echo.
echo [INFO] Verifying installation...
call :log "[INFO] Verifying installation..."

"%BIN_DIR%\visualizer.cmd" --help >nul 2>&1
if errorlevel 1 (
    call :log "[WARN] visualizer --help returned non-zero, but installation may still work."
) else (
    call :log "[OK] visualizer --help works."
)

REM ============================================================
REM 12. Done
REM ============================================================
echo.
echo ==============================================
echo  Installation complete!
echo ==============================================
echo.
echo Installation directory:
echo %INSTALL_DIR%
echo.
echo Log file:
echo %LOG_FILE%
echo.
echo ^>^>^> IMPORTANT: Close ALL terminal windows ^<^<^<
echo ^>^>^> and open a NEW one before running:    ^<^<^<
echo.
echo     visualizer
echo.
echo Test without audio:
echo     visualizer --demo
echo.
echo If it still doesn't work, run this command:
echo     "%BIN_DIR%\visualizer.cmd" --demo
echo.
pause
exit /b 0

REM ============================================================
REM Subroutine: log
REM ============================================================
:log
(
echo %~1
echo [%date% %time%] %~1
) >> "%LOG_FILE%" 2>&1
goto :eof