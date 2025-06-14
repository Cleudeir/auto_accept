@echo off
echo Building Dota 2 Auto Accept executable...
echo.

REM Change to src directory
cd /d "%~dp0src"

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
if not exist "..\dist\" mkdir "..\dist"
if not exist "..\build\" mkdir "..\build"

echo.
echo Building executable with PyInstaller...
echo.

REM Build with PyInstaller (we're already in src directory)
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Dota2AutoAccept" ^
    --icon "bin\icon.ico" ^
    --add-data "bin;bin" ^
    --add-data "config.json;." ^
    --distpath "..\dist" ^
    --workpath "..\build" ^
    --specpath "..\build" ^
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
    --collect-all "sounddevice" ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo Executable created at: ..\dist\Dota2AutoAccept.exe
    echo.
    pause
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    echo.
    pause
)
