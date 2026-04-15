@echo off
setlocal EnableDelayedExpansion
title App Installer - Dependency Check

echo ============================================
echo   App Installer - Dependency Checker
echo ============================================
echo.

:: ── 1. Check if Python is installed ──────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH.
    echo.
    echo Please install Python 3.8+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check the box:
    echo   [x] Add Python to PATH
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

:: ── 2. Get and display Python version ────────────────────────────────────────
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo [OK] Python %PY_VER% found.

:: ── 3. Enforce minimum Python 3.8 ────────────────────────────────────────────
for /f "tokens=1,2 delims=." %%a in ("%PY_VER%") do (
    set PY_MAJOR=%%a
    set PY_MINOR=%%b
)

if %PY_MAJOR% LSS 3 (
    echo [ERROR] Python 3.8 or higher is required. You have %PY_VER%.
    pause
    exit /b 1
)
if %PY_MAJOR% EQU 3 if %PY_MINOR% LSS 8 (
    echo [ERROR] Python 3.8 or higher is required. You have %PY_VER%.
    pause
    exit /b 1
)

:: ── 4. Verify all required stdlib modules ────────────────────────────────────
echo.
echo Checking required modules...
echo.

set ALL_OK=1

call :check_module os
call :check_module re
call :check_module json
call :check_module random
call :check_module datetime
call :check_module pathlib
call :check_module typing
call :check_module tkinter

:: ── 5. Special check: tkinter (not always bundled on Linux, warn on Windows) ──
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    set ALL_OK=0
    echo.
    echo [WARNING] tkinter is not available in this Python installation.
    echo   On Windows, re-install Python and ensure "tcl/tk and IDLE" is checked.
    echo   Download: https://www.python.org/downloads/
)

:: ── 6. Final result ───────────────────────────────────────────────────────────
echo.
if "%ALL_OK%"=="1" (
    echo ============================================
    echo  [SUCCESS] All dependencies are satisfied!
    echo  This app uses only Python standard library.
    echo  No pip install required.
    echo ============================================
) else (
    echo ============================================
    echo  [WARNING] Some checks failed. See above.
    echo ============================================
)

echo.
pause
exit /b 0

:: ── Helper: check a single stdlib module ─────────────────────────────────────
:check_module
python -c "import %~1" >nul 2>&1
if errorlevel 1 (
    echo   [FAIL]  %~1
    set ALL_OK=0
) else (
    echo   [OK]    %~1
)
exit /b 0
