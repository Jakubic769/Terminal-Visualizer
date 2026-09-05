@echo off
setlocal EnableExtensions

echo ==============================================
echo  Terminal Visualizer - Windows uninstaller
echo ==============================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\TerminalVisualizer"
set "BIN_DIR=%INSTALL_DIR%\bin"

if not exist "%INSTALL_DIR%" (
    echo [INFO] Installation directory not found:
    echo        %INSTALL_DIR%
    echo.
    echo Nothing to uninstall.
    pause
    exit /b 0
)

echo [INFO] Removing Terminal Visualizer files...

REM Remove bin directory first (launcher)
if exist "%BIN_DIR%" (
    rmdir /s /q "%BIN_DIR%"
)

REM Remove entire installation directory
rmdir /s /q "%INSTALL_DIR%"

if exist "%INSTALL_DIR%" (
    echo [WARN] Could not fully remove installation directory.
    echo        You may delete it manually:
    echo        %INSTALL_DIR%
) else (
    echo [OK] Terminal Visualizer files removed.
)

echo.
echo [INFO] PATH cleanup:
echo If you want to remove the PATH entry manually, go to:
echo   System Properties ^> Environment Variables ^> User variables ^> Path
echo.
pause
