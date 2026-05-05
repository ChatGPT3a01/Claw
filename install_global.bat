@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

set "CLAW_HOME=%~dp0"
REM Strip trailing backslash
if "%CLAW_HOME:~-1%"=="\" set "CLAW_HOME=%CLAW_HOME:~0,-1%"

echo.
echo ================================================
echo   Claw Global Install
echo   Adding to user PATH:
echo   %CLAW_HOME%
echo ================================================
echo.

REM Check if already in PATH
echo %PATH% | find /I "%CLAW_HOME%" > nul
if %errorlevel% equ 0 (
    echo [SKIP] Already in current session PATH.
    echo.
    echo If "claw" still does not work, open a NEW PowerShell or CMD window.
    pause
    exit /b 0
)

REM Get current user PATH (registry, not session)
for /f "usebackq tokens=2,*" %%A in (`reg query HKCU\Environment /v Path 2^>nul`) do set "USER_PATH=%%B"

if "%USER_PATH%"=="" (
    set "NEW_PATH=%CLAW_HOME%"
) else (
    REM Check user-level registry PATH
    echo !USER_PATH! | find /I "%CLAW_HOME%" > nul
    if !errorlevel! equ 0 (
        echo [SKIP] Already in user PATH ^(registry^).
        echo Open a NEW terminal window for it to take effect.
        pause
        exit /b 0
    )
    set "NEW_PATH=!USER_PATH!;%CLAW_HOME%"
)

echo Adding to user PATH ^(persistent^)...
setx PATH "!NEW_PATH!" > nul
if %errorlevel% neq 0 (
    echo [ERROR] setx failed. Try running as Administrator.
    pause
    exit /b 1
)

echo.
echo [OK] Done! Claw is now globally available.
echo.
echo IMPORTANT:
echo   - Close this window.
echo   - Open a NEW PowerShell / CMD window.
echo   - Type:  claw
echo.
pause
