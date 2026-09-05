@echo off
setlocal
set "INSTALL_DIR=%LOCALAPPDATA%\TerminalVisualizer"
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"
echo Terminal Visualizer files removed.
echo The PATH entry can be removed from User Environment Variables if desired.
pause
