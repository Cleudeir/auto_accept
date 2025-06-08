@echo off
setlocal enabledelayedexpansion

:: Title and Welcome
echo ===========================================
echo Dota Auto Accept - Compilation Script
echo ===========================================
echo.

:: remove all files in dist and build folders
echo Cleaning previous builds...
rmdir /s /q dist
rmdir /s /q build

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)

:: Check pip
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: pip not found for Python. Please ensure pip is installed.
    pause
    exit /b 1
)

:: Check PyInstaller
echo Checking for PyInstaller...
python -m pip list | findstr /I "pyinstaller" >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Error: Failed to install PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo PyInstaller found.
)

:: Set variables
set SCRIPT_NAME=dota_auto_accept.py
set ICON_NAME=icon.ico
set REFERENCE_IMAGE=dota.png
set PLUS_IMAGE=dota2-plus.jpeg
set ENV_FILE=.env
set APP_NAME=DotaAutoAccept

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

:: Validate plus image exists
if not exist "%PLUS_IMAGE%" (
    echo Error: Plus image %PLUS_IMAGE% not found in current directory.
    pause
    exit /b 1
)

:: Validate .env exists
if not exist "%ENV_FILE%" (
    echo Error: %ENV_FILE% not found in current directory.
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
python -m PyInstaller --onefile --windowed %ICON_PARAM% --name "%APP_NAME%" --add-data "%REFERENCE_IMAGE%;." --add-data "%PLUS_IMAGE%;." --add-data "%ENV_FILE%;." --clean --distpath "dist" --workpath "build" "%SCRIPT_NAME%"

:: Check compilation result
if %errorlevel% equ 0 (
    echo Compilation successful!
    echo Executable located in: dist\%APP_NAME%.exe
    
    :: Move the executable to Google Drive folder
    move /Y "dist\%APP_NAME%.exe" "C:\Users\CleudeirSilva\My Drive\Dota compile\%APP_NAME%.exe"
    if %errorlevel% equ 0 (
        echo Executable moved to: C:\Users\CleudeirSilva\My Drive\Dota compile\%APP_NAME%.exe
        start "" "C:\Users\CleudeirSilva\My Drive\Dota compile"
    ) else (
        echo Warning: Could not move executable. Please check the destination path.
    )
    
) else (
    echo Compilation failed.
)

echo Script finished.
pause