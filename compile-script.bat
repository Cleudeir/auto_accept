@echo off
setlocal enabledelayedexpansion

:: Title and Welcome
echo ===========================================
echo Dota Auto Accept - Compilation Script
echo ===========================================


:: remove all files in dist and build folders
rmdir /s /q dist
rmdir /s /q build

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)

:: Check PyInstaller
python -m pip list | findstr "pyinstaller" >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

:: Set variables
set SCRIPT_NAME=dota_auto_accept.py
set ICON_NAME=icon.ico
set REFERENCE_IMAGE=dota.png

:: Validate script exists
if not exist "%SCRIPT_NAME%" (
    echo Error: %SCRIPT_NAME% not found in current directory.
    pause
    exit /b 1
)

:: Validate reference image exists
if not exist "%REFERENCE_IMAGE%" (
    echo Error: Reference image %REFERENCE_IMAGE% not found in current directory.
    pause
    exit /b 1
)

:: Validate icon exists
if not exist "%ICON_NAME%" (
    echo Warning: No icon file found. Compiling without custom icon.
    set ICON_PARAM=
) else (
    set ICON_PARAM=--icon="%ICON_NAME%"
)

:: Create dist and build directories if they don't exist
if not exist "dist" mkdir dist
if not exist "build" mkdir build



:: Compile the script with additional data files
echo Compiling %SCRIPT_NAME%...
python -m PyInstaller --onefile --windowed %ICON_PARAM% --name "DotaAutoAccept" --add-data "%REFERENCE_IMAGE%;." --clean --distpath "dist" --workpath "build" "%SCRIPT_NAME%"

:: Check compilation result
if %errorlevel% equ 0 (
    echo Compilation successful!
    echo Executable located in: dist\DotaAutoAccept.exe
    start "" dist
) else (
    echo Compilation failed.
)

pause