@echo off
REM =============================
REM Dota 2 Auto Accept - OPTIMIZED Build Script for Minimal Size
REM Updated: 2025-06-14
REM Size Optimization: Aggressive exclusions and minimal dependencies
REM =============================

echo Building Dota 2 Auto Accept executable with size optimizations...
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

REM Install minimal requirements ONLY for smaller build
echo Installing MINIMAL requirements for size optimization...
pip install -r requirements_minimal.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install requirements.
    pause
    exit /b 1
)

REM Create dist and build directories if they don't exist
if not exist "%SCRIPT_DIR%dist\" mkdir "%SCRIPT_DIR%dist"
if not exist "%SCRIPT_DIR%build\" mkdir "%SCRIPT_DIR%build"

echo.
echo Building executable with MAXIMUM size optimizations...
echo Current directory: %CD%
echo.

REM Build with PyInstaller - ULTRA OPTIMIZED for minimal size
echo Running PyInstaller with aggressive size optimizations...
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
    --optimize=2 ^
    --strip ^
    --noupx ^
    --exclude-module matplotlib ^
    --exclude-module matplotlib.pyplot ^
    --exclude-module scipy ^
    --exclude-module pandas ^
    --exclude-module flask ^
    --exclude-module torch ^
    --exclude-module torchvision ^
    --exclude-module plotly ^
    --exclude-module easyocr ^
    --exclude-module tensorflow ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module IPython ^
    --exclude-module seaborn ^
    --exclude-module docx ^
    --exclude-module python_docx ^
    --exclude-module openpyxl ^
    --exclude-module xlrd ^
    --exclude-module xlsxwriter ^
    --exclude-module pdf ^
    --exclude-module pypdf ^
    --exclude-module pymupdf ^
    --exclude-module pdfminer ^
    --exclude-module cryptography ^
    --exclude-module bcrypt ^
    --exclude-module camelot ^
    --exclude-module lxml ^
    --exclude-module xmltodict ^
    --exclude-module requests ^
    --exclude-module urllib3 ^
    --exclude-module certifi ^
    --exclude-module charset_normalizer ^
    --exclude-module idna ^
    --exclude-module click ^
    --exclude-module jinja2 ^
    --exclude-module werkzeug ^
    --exclude-module blinker ^
    --exclude-module itsdangerous ^
    --exclude-module markupsafe ^
    --exclude-module pytest ^
    --exclude-module setuptools ^
    --exclude-module wheel ^
    --exclude-module pip ^
    --exclude-module distutils ^
    --exclude-module email ^
    --exclude-module http ^
    --exclude-module xml ^
    --exclude-module urllib ^
    --exclude-module html ^
    --exclude-module test ^
    --exclude-module tests ^
    --exclude-module unittest ^
    --exclude-module pydoc ^
    --exclude-module doctest ^
    --exclude-module argparse ^
    --exclude-module multiprocessing ^
    --exclude-module concurrent ^
    --exclude-module asyncio ^
    --exclude-module sqlite3 ^
    --exclude-module dbm ^
    --exclude-module tkinter.dnd ^
    --exclude-module tkinter.colorchooser ^
    --exclude-module tkinter.commondialog ^
    --exclude-module tkinter.filedialog ^
    --exclude-module tkinter.font ^
    --exclude-module tkinter.messagebox ^
    --exclude-module tkinter.scrolledtext ^
    --exclude-module tkinter.simpledialog ^
    --exclude-module tkinter.tix ^
    --exclude-module turtle ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "pygame" ^
    --hidden-import "pygame.mixer" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --hidden-import "pyautogui" ^
    --hidden-import "mss" ^
    --hidden-import "pygetwindow" ^
    --hidden-import "skimage.metrics" ^
    --hidden-import "sounddevice" ^
    --collect-submodules "PIL" ^
    --collect-submodules "tkinter" ^
    --noconfirm ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =============================
    echo OPTIMIZED BUILD COMPLETED SUCCESSFULLY!
    echo =============================
    echo Executable created at: %SCRIPT_DIR%dist\Dota2AutoAccept.exe
    echo File size: 
    dir "%SCRIPT_DIR%dist\Dota2AutoAccept.exe" | findstr "Dota2AutoAccept.exe"
    echo.
    echo Size optimization complete!
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
