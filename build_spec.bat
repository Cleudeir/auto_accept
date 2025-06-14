@echo off
echo Building Dota 2 Auto Accept using spec file...
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

REM Go back to root directory for spec file
cd /d "%~dp0"

REM Create dist and build directories if they don't exist
if not exist "dist\" mkdir "dist"
if not exist "build\" mkdir "build"

echo.
echo Building executable using spec file...
echo.

REM Build with PyInstaller using the spec file
pyinstaller Dota2AutoAccept.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Build completed successfully!
    echo ==========================================
    echo.
    echo Executable created at: dist\Dota2AutoAccept.exe
    echo.
    echo You can now run the application without Python installed.
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
