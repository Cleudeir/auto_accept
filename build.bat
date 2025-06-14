@echo off
echo Building Dota 2 Auto Accept executable...
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set SRC_DIR=%SCRIPT_DIR%src

echo Script directory: %SCRIPT_DIR%
echo Source directory: %SRC_DIR%

REM Change to src directory
cd /d "%SRC_DIR%"

REM Check if virtual environment exists, if not create it
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create dist and build directories if they don't exist
if not exist "%SCRIPT_DIR%dist\" mkdir "%SCRIPT_DIR%dist"
if not exist "%SCRIPT_DIR%build\" mkdir "%SCRIPT_DIR%build"

echo.
echo Building executable with PyInstaller...
echo Current directory: %CD%
echo.

REM Build with PyInstaller (using absolute paths)
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
    --hidden-import "pygame" ^
    --hidden-import "sounddevice" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --hidden-import "screeninfo" ^
    --hidden-import "pyautogui" ^
    --hidden-import "mss" ^
    --hidden-import "pygetwindow" ^
    --hidden-import "skimage" ^
    --collect-all "cv2" ^
    --collect-all "pygame" ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo Executable created at: %SCRIPT_DIR%dist\Dota2AutoAccept.exe
    echo.
    pause
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
    pause
)
