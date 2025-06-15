@echo off
REM =============================
REM Dota 2 Auto Accept Build Script
REM Updated: 2025-06-14
REM =============================

echo Building Dota 2 Auto Accept executable...
echo.

REM Check Python version (require 3.8+)
echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher and add it to PATH.
    pause
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set SRC_DIR=%SCRIPT_DIR%src

echo Script directory: %SCRIPT_DIR%
echo Source directory: %SRC_DIR%

REM Clean up old build and dist folders
echo Cleaning up old build artifacts...
if exist "%SCRIPT_DIR%dist" (
    echo Removing old dist folder...
    rmdir /s /q "%SCRIPT_DIR%dist"
)
if exist "%SCRIPT_DIR%build" (
    echo Removing old build folder...
    rmdir /s /q "%SCRIPT_DIR%build"
)

REM Change to src directory
cd /d "%SRC_DIR%"

REM Check if virtual environment exists, if not create it
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyInstaller first
echo Installing PyInstaller...
pip install pyinstaller

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

REM Create dist and build directories if they don't exist
if not exist "%SCRIPT_DIR%dist\" mkdir "%SCRIPT_DIR%dist"
if not exist "%SCRIPT_DIR%build\" mkdir "%SCRIPT_DIR%build"

echo.
echo Building executable with PyInstaller...
echo Current directory: %CD%
echo.

REM Build with PyInstaller (using absolute paths)
echo Running PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Dota2AutoAccept" ^
    --icon "%SRC_DIR%\bin\icon.ico" ^
    --add-data "%SRC_DIR%\bin;bin" ^
    --add-data "%SRC_DIR%\config.json;." ^
    --add-data "%SRC_DIR%\controllers;controllers" ^
    --add-data "%SRC_DIR%\models;models" ^
    --add-data "%SRC_DIR%\views;views" ^
    --distpath "%SCRIPT_DIR%dist" ^
    --workpath "%SCRIPT_DIR%build" ^
    --specpath "%SCRIPT_DIR%build" ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "pygame" ^
    --hidden-import "pygame.mixer" ^
    --hidden-import "sounddevice" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --hidden-import "screeninfo" ^
    --hidden-import "pyautogui" ^
    --hidden-import "mss" ^
    --hidden-import "pygetwindow" ^
    --hidden-import "skimage" ^
    --hidden-import "skimage.feature" ^
    --hidden-import "skimage.measure" ^
    --hidden-import "matplotlib" ^
    --hidden-import "matplotlib.pyplot" ^
    --collect-all "cv2" ^
    --collect-all "pygame" ^
    --collect-all "skimage" ^
    --collect-submodules "PIL" ^
    --collect-submodules "tkinter" ^
    --noconfirm ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =============================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo =============================
    echo Executable created at: %SCRIPT_DIR%dist\Dota2AutoAccept.exe
    echo File size: 
    dir "%SCRIPT_DIR%dist\Dota2AutoAccept.exe"
    echo.
    echo You can now run the executable from the dist folder.
    pause
) else (
    echo.
    echo =============================
    echo BUILD FAILED!
    echo =============================
    echo Build failed with error code %ERRORLEVEL%
    echo Check the output above for error details.
    echo.
    echo Common solutions:
    echo 1. Make sure all dependencies are installed
    echo 2. Check if antivirus is blocking PyInstaller
    echo 3. Try running as administrator
    echo 4. Check if Python and pip are properly installed
    pause
    exit /b %ERRORLEVEL%
)

REM Deactivate virtual environment
deactivate


