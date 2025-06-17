@echo off
setlocal enableDelayedExpansion

REM ===========================================================================
REM Dota 2 Auto Accept - Installation and Launch Script
REM ===========================================================================
echo ===========================================================================
echo Welcome to Dota 2 Auto Accept
echo ===========================================================================
echo Starting installation and setup process...

REM ===========================================================================
REM Check for Administrator privileges
REM ===========================================================================
openfiles >nul 2>&1
if not !errorlevel!==0 echo ===========================================================================
if not !errorlevel!==0 echo WARNING: This script is not running as Administrator.
if not !errorlevel!==0 echo Some installation steps may fail without elevated privileges.
if not !errorlevel!==0 echo Please right-click and 'Run as administrator' if you encounter issues.
if not !errorlevel!==0 echo ===========================================================================
if not !errorlevel!==0 echo(

echo Starting installation process...

:PYTHON_CHECK
REM ===========================================================================
REM Check and Install Python
REM ===========================================================================
echo(
echo [1/2] Checking for Python...
set "PYTHON_EXE="
where python > nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo   Python is installed.
    set "PYTHON_EXE=python"
    goto :PIP_INSTALL_CHECK
)

where py >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo   Python (via py launcher) is installed.
    set "PYTHON_EXE=py"
    goto :PIP_INSTALL_CHECK
)

echo   Python not found. Installing Python from local installer...
set "PYTHON_INSTALLER=%~dp0dependencies\python-3.13.1-amd64.exe"
if not exist "!PYTHON_INSTALLER!" (
    echo   ERROR: Python installer not found at !PYTHON_INSTALLER!
    echo   Please ensure the Python installer is in the dependencies folder.
    goto :EOF_ERROR
)

echo   Installing Python from !PYTHON_INSTALLER!...
echo   This will install Python with default settings and add it to PATH.
"!PYTHON_INSTALLER!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_dev=0 Include_debug=0 InstallLauncherAllUsers=1 AssociateFiles=1
set INSTALL_RESULT=!ERRORLEVEL!
echo(
if not !INSTALL_RESULT!==0 goto :INSTALL_FAIL

echo ===========================================================================
echo Python installer completed. Validating installation...
echo ===========================================================================
timeout /t 3 /nobreak >nul
echo Checking if Python is accessible...
set PYTHON_FOUND=0
set PYTHON_LAUNCHER_FOUND=0
python --version >nul 2>&1
if !ERRORLEVEL! equ 0 set PYTHON_FOUND=1
py --version >nul 2>&1
if !ERRORLEVEL! equ 0 set PYTHON_LAUNCHER_FOUND=1

if !PYTHON_FOUND! equ 1 (
    echo [OK] Python command is working:
    python --version
    set "PYTHON_EXE=python"
) else (
    echo [FAIL] Python command not found in PATH
)
if !PYTHON_LAUNCHER_FOUND! equ 1 (
    echo [OK] Python Launcher (py) is working
    set "PYTHON_EXE=py"
) else (
    echo [FAIL] Python Launcher (py) not found
)

if !PYTHON_FOUND! equ 1 goto :PIP_INSTALL_CHECK
if !PYTHON_LAUNCHER_FOUND! equ 1 goto :PIP_INSTALL_CHECK

echo   Python still not found in PATH even after local installation.
echo   Please open a new command prompt and re-run this script, or ensure Python was correctly installed and added to PATH.
goto :EOF_ERROR

:INSTALL_FAIL
echo ===========================================================================
echo ERROR: Python installation failed with error code: !INSTALL_RESULT!
echo ===========================================================================
echo Possible reasons:
echo - Insufficient privileges (try running as Administrator)
echo - Python is already installed
echo - System incompatibility
echo - Corrupted installer file
echo(
echo Please try running this script as Administrator or check the installer.
echo ===========================================================================
goto :EOF_ERROR

:PIP_INSTALL_CHECK
if not defined PYTHON_EXE (
    echo   Could not determine Python executable. Please ensure Python is installed and in PATH.
    goto :EOF_ERROR
)
echo   Using !PYTHON_EXE! for Python commands.

REM ===========================================================================
REM Install/Upgrade pip and install project dependencies
REM ===========================================================================
echo(
echo [2/2] Installing/Upgrading pip and installing project dependencies...

echo   Ensuring pip is available and upgrading it...
!PYTHON_EXE! -m ensurepip --upgrade 2>nul
set PIP_ENSURE_RESULT=!ERRORLEVEL!
if !PIP_ENSURE_RESULT! neq 0 (
    echo   Failed to ensure/upgrade pip using '!PYTHON_EXE! -m ensurepip --upgrade'. (Errorlevel: !PIP_ENSURE_RESULT!)
    echo   This might be normal if pip is already installed. Continuing...
)

!PYTHON_EXE! -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo   Failed to upgrade pip.
    echo   Continuing with dependencies installation, but pip might be outdated.
)

echo   Installing project dependencies from requirements.txt...
cd /d "%~dp0src"
if not exist requirements.txt (
    echo   ERROR: requirements.txt not found in src directory
    goto :EOF_ERROR
)

echo   Please wait while dependencies are being installed...
!PYTHON_EXE! -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo   --------------------------------------------------------------------
    echo   ERROR: Failed to install project dependencies.
    echo   This could be due to:
    echo   1. Missing C++ compiler for some packages
    echo   2. Network connectivity issues
    echo   3. Incompatible package versions
    echo(
    echo   You can try installing individual packages manually:
    echo   !PYTHON_EXE! -m pip install requests opencv-python pillow pyautogui
    echo   --------------------------------------------------------------------
    goto :EOF_ERROR
)

echo   Project dependencies installed successfully.

echo(
echo ===========================================================================
echo Installation script completed successfully.
echo All dependencies have been installed.
echo ===========================================================================
echo(
echo Automatically starting Dota 2 Auto Accept Application...
goto :RUN_PROGRAM

:RUN_PROGRAM
echo(
echo ===========================================================================
echo Starting Dota 2 Auto Accept Application...
echo ===========================================================================
echo   Launching the application. Press Ctrl+C to stop when running.
echo(
cd /d "%~dp0src"
!PYTHON_EXE! main.py
set RUN_RESULT=!ERRORLEVEL!
if !RUN_RESULT! neq 0 (
    echo(
    echo   Application exited with error code: !RUN_RESULT!
    echo   Check the logs directory for more information.
) else (
    echo(
    echo   Application finished successfully.
)
echo(
echo Press any key to exit...
pause >nul
goto :EOF_SUCCESS

:EOF_ERROR
echo(
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo   Installation script encountered errors. Please review the messages above.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
pause
exit /b 1

:EOF_SUCCESS

exit /b 0
