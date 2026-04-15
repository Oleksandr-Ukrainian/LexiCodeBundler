@echo off
setlocal EnableDelayedExpansion

set SCRIPT=bundle_sourcesMultilingual.py
set APP_NAME=LexiCode_Bundler
set DIST_DIR=dist
set BUILD_DIR=build

echo ============================================
echo LexiCode Bundler - PyInstaller EXE builder
echo ============================================
echo.

:: Find python
set PYTHON_CMD=
where python >nul 2>&1 && set PYTHON_CMD=python
if not defined PYTHON_CMD (
    where py >nul 2>&1 && set PYTHON_CMD=py
)
if not defined PYTHON_CMD (
    echo [ERROR] Python not found in PATH.
    pause
    exit /b 1
)

echo [INFO] Python: %PYTHON_CMD%
%PYTHON_CMD% --version

:: Find pip
set PIP_CMD=
where pip >nul 2>&1 && set PIP_CMD=pip
if not defined PIP_CMD (
    where pip3 >nul 2>&1 && set PIP_CMD=pip3
)
if not defined PIP_CMD (
    set PIP_CMD=%PYTHON_CMD% -m pip
)

echo [INFO] pip: %PIP_CMD%

:: Icon — must be .ico
set ICON_ARG=
set ICON_DATA=
if exist "%~dp0icon.ico" (
    set ICON_ARG=--icon "%~dp0icon.ico"
    set ICON_DATA=--add-data "%~dp0icon.ico;."
    echo [INFO] Icon: %~dp0icon.ico
) else (
    echo [WARN] icon.ico not found - using default icon.
)

:: Kill running EXE and overwrite if it exists
if exist "%~dp0%DIST_DIR%\%APP_NAME%.exe" (
    echo [INFO] Found existing %APP_NAME%.exe - checking if running...
    tasklist /FI "IMAGENAME eq %APP_NAME%.exe" 2>nul | find /I "%APP_NAME%.exe" >nul
    if not errorlevel 1 (
        echo [INFO] Process is running - killing it...
        taskkill /F /IM "%APP_NAME%.exe" >nul 2>&1
        timeout /t 1 /nobreak >nul
    )
    echo [INFO] Removing existing %APP_NAME%.exe...
    del /f /q "%~dp0%DIST_DIR%\%APP_NAME%.exe"
    if exist "%~dp0%DIST_DIR%\%APP_NAME%.exe" (
        echo [ERROR] Could not delete existing EXE even after kill. Close it manually and retry.
        pause
        exit /b 1
    )
    echo [INFO] Old EXE removed.
)

echo.
echo [1/3] Installing PyInstaller...
%PIP_CMD% install --upgrade pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)

echo [2/3] Building EXE...
%PYTHON_CMD% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "%APP_NAME%" ^
    %ICON_ARG% ^
    %ICON_DATA% ^
    --distpath "%~dp0%DIST_DIR%" ^
    --workpath "%~dp0%BUILD_DIR%" ^
    --clean ^
    --noconfirm ^
    "%~dp0%SCRIPT%"

if errorlevel 1 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Done! Output: %~dp0%DIST_DIR%\%APP_NAME%.exe
echo.
start "" "%~dp0%DIST_DIR%"

:: Auto-close countdown (30 seconds)
echo Build successful! This window will close automatically in 30 seconds...
echo Press any key to close immediately.
echo.
for /l %%i in (30,-1,1) do (
    <nul set /p "=Closing in %%i seconds...   "
    echo.
    timeout /t 1 /nobreak >nul
)
exit
