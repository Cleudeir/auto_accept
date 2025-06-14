@echo off
echo Advanced Build Script for Dota 2 Auto Accept
echo =============================================
echo.

set /p choice="Build type: (1) GUI version (no console) (2) Console version (3) Both [1]: "
if "%choice%"=="" set choice=1

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

if "%choice%"=="1" goto build_gui
if "%choice%"=="2" goto build_console
if "%choice%"=="3" goto build_both

:build_gui
echo Building GUI version (no console window)...
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
goto finish

:build_console
echo Building console version (with console window for debugging)...
pyinstaller ^
    --onefile ^
    --console ^
    --name "Dota2AutoAccept_Console" ^
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
goto finish

:build_both
echo Building both GUI and console versions...
echo.
echo Building GUI version...
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

echo.
echo Building console version...
pyinstaller ^
    --onefile ^
    --console ^
    --name "Dota2AutoAccept_Console" ^
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

:finish
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Build completed successfully!
    echo ==========================================
    echo.
    if "%choice%"=="1" (
        echo GUI executable created at: ..\dist\Dota2AutoAccept.exe
    )
    if "%choice%"=="2" (
        echo Console executable created at: ..\dist\Dota2AutoAccept_Console.exe
    )
    if "%choice%"=="3" (
        echo GUI executable created at: ..\dist\Dota2AutoAccept.exe
        echo Console executable created at: ..\dist\Dota2AutoAccept_Console.exe
    )
    echo.
    echo You can now distribute the executable(s) without needing Python installed.
    echo.
) else (
    echo.
    echo ==========================================
    echo Build failed with error code %ERRORLEVEL%
    echo ==========================================
    echo Check the output above for error details.
    echo.
)

pause
