@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Terminal Visualizer Installer

REM ============================================================
REM Terminal Visualizer - Windows installer
REM ============================================================
REM This project currently uses the winsdk Python package, whose
REM published Windows wheels go up to CPython 3.12. Prefer Python
REM 3.12, then 3.11/3.10/3.9. Do NOT blindly select the newest
REM installed Python (3.13/3.14 can make pip fail here).
REM ============================================================

set "INSTALL_DIR=%LOCALAPPDATA%\TerminalVisualizer"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "BIN_DIR=%INSTALL_DIR%\bin"
set "LOG_FILE=%INSTALL_DIR%\install.log"
set "SCRIPT_DIR=%~dp0"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1
(
    echo ==============================================
    echo  Terminal Visualizer - Windows Installer
    echo  Started: %date% %time%
    echo ==============================================
    echo.
) > "%LOG_FILE%"

call :log "[INFO] Searching for a compatible Python version (3.9 - 3.12)..."

REM ============================================================
REM 1. Find compatible Python 3.9 - 3.12
REM ============================================================
set "PY="
set "PY_ARGS="

REM Prefer the Python launcher and explicitly request a supported
REM minor version instead of letting `py -3` pick 3.13/3.14.
where py >nul 2>&1
if not errorlevel 1 (
    for %%V in (3.12 3.11 3.10 3.9) do (
        if not defined PY (
            py -%%V -c "import sys; raise SystemExit(0 if (sys.version_info >= (3,9) and sys.version_info < (3,13)) else 1)" >nul 2>&1
            if not errorlevel 1 (
                set "PY=py"
                set "PY_ARGS=-%%V"
                call :log "[OK] Found Python %%V via 'py -%%V'"
            )
        )
    )
)

REM Try python on PATH if the launcher is unavailable.
if not defined PY (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if (sys.version_info >= (3,9) and sys.version_info < (3,13)) else 1)" >nul 2>&1
        if not errorlevel 1 (
            set "PY=python"
            call :log "[OK] Found compatible Python via 'python'"
        )
    )
)

REM Try python3 (Git Bash / MSYS2).
if not defined PY (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        python3 -c "import sys; raise SystemExit(0 if (sys.version_info >= (3,9) and sys.version_info < (3,13)) else 1)" >nul 2>&1
        if not errorlevel 1 (
            set "PY=python3"
            call :log "[OK] Found compatible Python via 'python3'"
        )
    )
)

REM Last resort: check common python.org installation locations.
if not defined PY (
    for %%V in (312 311 310 39) do (
        if not defined PY (
            for %%B in ("%LocalAppData%\Programs\Python" "%ProgramFiles%" "%ProgramFiles(x86)%") do (
                if exist "%%~B\Python%%V\python.exe" (
                    set "PY=%%~B\Python%%V\python.exe"
                    call :log "[OK] Found Python at %%~B\Python%%V\python.exe"
                )
            )
        )
    )
)

if not defined PY (
    call :log "[ERROR] No compatible Python 3.9 - 3.12 installation was found."
    echo.
    echo [ERROR] Compatible Python was not found.
    echo.
    echo This project currently requires Python 3.9, 3.10, 3.11 or 3.12 on Windows.
    echo Python 3.13+ is NOT suitable for this version because the winsdk dependency
    echo does not provide matching Windows wheels.
    echo.
    echo Install Python 3.12 from:
    echo https://www.python.org/downloads/release/python-31210/
    echo.
    echo During installation, enable "Add python.exe to PATH" if available.
    pause
    exit /b 1
)

echo [OK] Using Python: %PY% %PY_ARGS%
call :log "[OK] Python command: %PY% %PY_ARGS%"

REM ============================================================
REM 2. Verify exact Python version
REM ============================================================
echo [INFO] Checking Python version...
call :log "[INFO] Verifying Python version..."

"%PY%" %PY_ARGS% --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "[ERROR] Could not run Python."
    echo [ERROR] Could not run Python.
    echo Check: %LOG_FILE%
    pause
    exit /b 1
)

"%PY%" %PY_ARGS% -c "import sys; print('Python', sys.version.split()[0]); raise SystemExit(0 if (sys.version_info >= (3,9) and sys.version_info < (3,13)) else 1)" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "[ERROR] Python 3.9 - 3.12 is required for this Windows build."
    echo [ERROR] Python 3.9 - 3.12 is required for this Windows build.
    echo See: %LOG_FILE%
    pause
    exit /b 1
)
call :log "[OK] Python version is compatible."

REM ============================================================
REM 3. Check project files
REM ============================================================
if not exist "%SCRIPT_DIR%pyproject.toml" if not exist "%SCRIPT_DIR%setup.py" (
    call :log "[ERROR] No pyproject.toml or setup.py found in %SCRIPT_DIR%"
    echo [ERROR] No pyproject.toml or setup.py found.
    echo Make sure install.bat is inside the Terminal-Visualizer project directory.
    pause
    exit /b 1
)
call :log "[OK] Project files found in %SCRIPT_DIR%"

REM ============================================================
REM 4. Prepare directories
REM ============================================================
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" >nul 2>&1
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%" >nul 2>&1

REM ============================================================
REM 5. Create / repair virtual environment
REM ============================================================
echo.
echo [INFO] Creating isolated Python environment...
call :log "[INFO] Preparing virtual environment at %VENV_DIR%..."

if exist "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Existing virtual environment found. Checking it...
    "%VENV_DIR%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if (sys.version_info >= (3,9) and sys.version_info < (3,13)) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Existing virtual environment uses an unsupported Python version.
        call :log "[WARN] Existing venv is incompatible. Recreating it."
        rmdir /s /q "%VENV_DIR%" >nul 2>&1
    ) else (
        call :log "[OK] Existing compatible virtual environment will be reused."
    )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    "%PY%" %PY_ARGS% -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        call :log "[ERROR] Failed to create virtual environment."
        echo [ERROR] Could not create the Python virtual environment.
        echo Check: %LOG_FILE%
        pause
        exit /b 1
    )
    call :log "[OK] Virtual environment created."
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    call :log "[ERROR] venv\Scripts\python.exe is missing after creation."
    echo [ERROR] Virtual environment was not created correctly.
    pause
    exit /b 1
)

echo [OK] Virtual environment ready.

REM ============================================================
REM 6. Upgrade pip tooling
REM ============================================================
echo.
echo [INFO] Updating pip, setuptools and wheel...
call :log "[INFO] Upgrading pip/setuptools/wheel..."

"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log "[ERROR] pip tooling update failed."
    echo [ERROR] Could not update pip/setuptools/wheel.
    echo Check: %LOG_FILE%
    pause
    exit /b 1
)
call :log "[OK] pip tooling updated."

REM ============================================================
REM 7. Install the project
REM ============================================================
echo.
echo [INFO] Installing Terminal Visualizer and dependencies...
call :log "[INFO] Running pip install from %SCRIPT_DIR%"

pushd "%SCRIPT_DIR%"
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade . >> "%LOG_FILE%" 2>&1
set "PIP_RESULT=%ERRORLEVEL%"
popd

if not "%PIP_RESULT%"=="0" (
    call :log "[ERROR] pip install failed with code %PIP_RESULT%."
    echo.
    echo [ERROR] Package installation failed.
    echo.
    echo The full error is in:
    echo   %LOG_FILE%
    echo.
    echo A common cause is using an unsupported Python version.
    pause
    exit /b 1
)

call :log "[OK] Package installed successfully."
echo [OK] Terminal Visualizer installed.

REM ============================================================
REM 8. Create a robust launcher
REM ============================================================
REM Do not depend on visualizer.exe being generated correctly and
REM do not embed an unquoted path with spaces. Run the module directly.
set "LAUNCHER=%BIN_DIR%\visualizer.cmd"

echo.
echo [INFO] Creating visualizer command launcher...
call :log "[INFO] Creating launcher: %LAUNCHER%"

> "%LAUNCHER%" echo @echo off
>>"%LAUNCHER%" echo "%VENV_DIR%\Scripts\python.exe" -m visualizer.cli %%*
>>"%LAUNCHER%" echo exit /b %%ERRORLEVEL%%

if not exist "%LAUNCHER%" (
    call :log "[ERROR] Could not create launcher."
    echo [ERROR] Could not create visualizer.cmd
    pause
    exit /b 1
)
call :log "[OK] Launcher created."
echo [OK] Launcher created.

REM ============================================================
REM 9. Add launcher directory to USER PATH
REM ============================================================
echo.
echo [INFO] Adding Terminal Visualizer to USER PATH...
call :log "[INFO] Updating USER PATH..."

set "PATH_PY=%TEMP%\tv_update_path_%RANDOM%.py"
set "PATH_RESULT_FILE=%TEMP%\tv_path_result_%RANDOM%.txt"

REM Use the newly created venv Python for PATH editing so this step
REM does not depend on the user's system Python command resolution.
> "%PATH_PY%" echo import os, sys, winreg, ctypes
>>"%PATH_PY%" echo p = os.path.normpath(r'%BIN_DIR%')
>>"%PATH_PY%" echo try:
>>"%PATH_PY%" echo     k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_READ ^| winreg.KEY_SET_VALUE)
>>"%PATH_PY%" echo     try:
>>"%PATH_PY%" echo         old, kind = winreg.QueryValueEx(k, 'Path')
>>"%PATH_PY%" echo     except FileNotFoundError:
>>"%PATH_PY%" echo         old, kind = '', winreg.REG_EXPAND_SZ
>>"%PATH_PY%" echo     parts = [x.strip() for x in str(old).split(';') if x.strip()]
>>"%PATH_PY%" echo     norm = [os.path.normcase(os.path.normpath(x)) for x in parts]
>>"%PATH_PY%" echo     target = os.path.normcase(os.path.normpath(p))
>>"%PATH_PY%" echo     if target not in norm:
>>"%PATH_PY%" echo         parts.insert(0, p)
>>"%PATH_PY%" echo         winreg.SetValueEx(k, 'Path', 0, winreg.REG_EXPAND_SZ, ';'.join(parts))
>>"%PATH_PY%" echo         result = 'PATH_UPDATED'
>>"%PATH_PY%" echo     else:
>>"%PATH_PY%" echo         result = 'PATH_ALREADY_OK'
>>"%PATH_PY%" echo     winreg.CloseKey(k)
>>"%PATH_PY%" echo     try:
>>"%PATH_PY%" echo         ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, 'Environment', 0x0002, 5000, None)
>>"%PATH_PY%" echo     except Exception:
>>"%PATH_PY%" echo         pass
>>"%PATH_PY%" echo     print(result)
>>"%PATH_PY%" echo except Exception as e:
>>"%PATH_PY%" echo     print('PATH_ERROR:' + str(e))
>>"%PATH_PY%" echo     sys.exit(1)

"%VENV_DIR%\Scripts\python.exe" "%PATH_PY%" > "%PATH_RESULT_FILE%" 2>&1
set "PATH_EXIT=%ERRORLEVEL%"
set "PATH_RESULT="
if exist "%PATH_RESULT_FILE%" set /p PATH_RESULT=<"%PATH_RESULT_FILE%"

del /f /q "%PATH_PY%" >nul 2>&1
del /f /q "%PATH_RESULT_FILE%" >nul 2>&1

if "%PATH_EXIT%"=="0" if "%PATH_RESULT%"=="PATH_UPDATED" (
    call :log "[OK] USER PATH updated."
    echo [OK] USER PATH updated.
) else if "%PATH_EXIT%"=="0" if "%PATH_RESULT%"=="PATH_ALREADY_OK" (
    call :log "[OK] Launcher directory was already in USER PATH."
    echo [OK] Launcher directory already in USER PATH.
) else (
    call :log "[WARN] Could not update USER PATH automatically: %PATH_RESULT%"
    echo [WARN] Could not update USER PATH automatically.
    echo Add this directory manually to your User PATH:
    echo   %BIN_DIR%
)

REM ============================================================
REM 10. Verify installation and launcher
REM ============================================================
echo.
echo [INFO] Verifying installation...
call :log "[INFO] Verifying visualizer --help..."

call "%LAUNCHER%" --help >nul 2>&1
if errorlevel 1 (
    call :log "[ERROR] visualizer --help failed."
    echo [ERROR] Installation verification failed.
    echo The launcher exists, but the application did not start correctly.
    echo Check:
    echo   %LOG_FILE%
    echo.
    echo You can also test manually with:
    echo   "%LAUNCHER%" --demo
    pause
    exit /b 1
)

call :log "[OK] visualizer --help works."
echo [OK] Installation verified.

REM ============================================================
REM 11. Done
REM ============================================================
echo.
echo ==============================================
echo  Installation complete!
echo ==============================================
echo.
echo Install directory:
echo   %INSTALL_DIR%
echo.
echo Log file:
echo   %LOG_FILE%
echo.
echo IMPORTANT: open a NEW terminal window before using:
echo   visualizer
echo.
echo Test without audio:
echo   visualizer --demo
echo.
echo Direct test from this window:
echo   "%LAUNCHER%" --demo
echo.
pause
exit /b 0

REM ============================================================
REM Subroutine: log
REM ============================================================
:log
>>"%LOG_FILE%" echo %~1
>>"%LOG_FILE%" echo [%date% %time%] %~1
goto :eof
