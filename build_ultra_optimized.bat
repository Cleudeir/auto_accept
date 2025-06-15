@echo off
REM =============================
REM Dota 2 Auto Accept - ULTRA OPTIMIZED Build Script
REM Size Target: Under 50MB (vs previous 300MB)
REM Removes scikit-image and other heavy dependencies
REM =============================

echo Building Dota 2 Auto Accept with ULTRA size optimizations...
echo Target: Reduce from 300MB to under 50MB
echo.

REM Check Python version (require 3.8+)
echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH.
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
    rmdir /s /q "%SCRIPT_DIR%dist"
)
if exist "%SCRIPT_DIR%build" (
    rmdir /s /q "%SCRIPT_DIR%build"
)

REM Change to src directory
cd /d "%SRC_DIR%"

REM Create fresh virtual environment for clean build
if exist "venv\" (
    echo Removing old virtual environment...
    rmdir /s /q "venv"
)

echo Creating fresh virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install ULTRA minimal requirements
echo Installing ULTRA minimal requirements (removing scikit-image)...
pip install -r requirements_ultra_minimal.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install minimal requirements.
    pause
    exit /b 1
)

REM Create directories
if not exist "%SCRIPT_DIR%dist\" mkdir "%SCRIPT_DIR%dist"
if not exist "%SCRIPT_DIR%build\" mkdir "%SCRIPT_DIR%build"

echo.
echo Building with MAXIMUM size optimizations...
echo Excluding: scipy, scikit-image, matplotlib, pandas, torch, flask, and 50+ other packages
echo.

REM ULTRA OPTIMIZED PyInstaller build
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
    --exclude-module scipy.stats ^
    --exclude-module scipy.sparse ^
    --exclude-module pandas ^
    --exclude-module flask ^
    --exclude-module torch ^
    --exclude-module torchvision ^
    --exclude-module plotly ^
    --exclude-module easyocr ^
    --exclude-module tensorflow ^
    --exclude-module sklearn ^
    --exclude-module scikit-image ^
    --exclude-module skimage ^
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
    --exclude-module requests ^
    --exclude-module urllib3 ^
    --exclude-module certifi ^
    --exclude-module charset_normalizer ^
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
    --exclude-module html ^
    --exclude-module test ^
    --exclude-module tests ^
    --exclude-module unittest ^
    --exclude-module pydoc ^
    --exclude-module doctest ^
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
    --exclude-module tkinter.scrolledtext ^
    --exclude-module tkinter.simpledialog ^
    --exclude-module tkinter.tix ^
    --exclude-module turtle ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "pygame.mixer" ^
    --hidden-import "cv2" ^
    --hidden-import "numpy" ^
    --hidden-import "pyautogui" ^
    --hidden-import "mss" ^
    --hidden-import "pygetwindow" ^
    --hidden-import "sounddevice" ^
    --collect-submodules "PIL" ^
    --collect-submodules "tkinter" ^
    --noconfirm ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =============================
    echo ULTRA OPTIMIZED BUILD COMPLETED!
    echo =============================
    echo Executable: %SCRIPT_DIR%dist\Dota2AutoAccept.exe
    
    REM Get file size
    for %%F in ("%SCRIPT_DIR%dist\Dota2AutoAccept.exe") do (
        set size=%%~zF
        set /a sizeMB=!size!/1024/1024
    )
    
    echo File size: %sizeMB% MB (was 300MB)
    echo Size reduction: Approximately %size% bytes
    echo.
    echo Optimization complete! Test the executable to ensure it works.
    pause
) else (
    echo.
    echo =============================
    echo BUILD FAILED!
    echo =============================
    echo Error code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

deactivate
