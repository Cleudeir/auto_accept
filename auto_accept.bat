@echo off
setlocal enableDelayedExpansion

echo Starting installation process...

:PYTHON_CHECK
REM ==========================================================================
REM Check and Install Python
REM ==========================================================================
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
"!PYTHON_INSTALLER!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
if !ERRORLEVEL! neq 0 (
    echo   Failed to install Python using local installer (Errorlevel: !ERRORLEVEL!).
    echo   Please try running the installer manually from dependencies\python-3.13.1-amd64.exe
    goto :EOF_ERROR
)

echo   Python 3.13.1 installed successfully from local installer.
echo   You MIGHT need to open a new command prompt for Python to be available in PATH.
REM Try to find python or py again
where python >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYTHON_EXE=python"
    goto :PIP_INSTALL_CHECK
)
where py >nul 2>&1
if !ERRORLEVEL! equ 0 (
    set "PYTHON_EXE=py"
    goto :PIP_INSTALL_CHECK
)

echo   Python still not found in PATH even after local installation.
echo   Please open a new command prompt ^& re-run this script, or ensure Python was correctly installed ^& added to PATH.
goto :EOF_ERROR

:PIP_INSTALL_CHECK
if not defined PYTHON_EXE (
    echo   Could not determine Python executable. Please ensure Python is installed ^& in PATH.
    goto :EOF_ERROR
)
echo   Using !PYTHON_EXE! for Python commands.

REM ==========================================================================
REM Install/Upgrade pip and install project dependencies
REM ==========================================================================
echo(
echo [2/2] Installing/Upgrading pip ^& installing project dependencies...

echo   Ensuring pip is available ^& upgrading it...
!PYTHON_EXE! -m ensurepip --upgrade 2>nul
set PIP_ENSURE_RESULT=!ERRORLEVEL!
if !PIP_ENSURE_RESULT! neq 0 (
    echo   Failed to ensure/upgrade pip using '!PYTHON_EXE! -m ensurepip --upgrade'. (Errorlevel: !PIP_ENSURE_RESULT!)
    echo   This might be normal if pip is already installed. Continuing...
)

!PYTHON_EXE! -m pip install --upgrade pip
set PIP_UPGRADE_RESULT=!ERRORLEVEL!
if !PIP_UPGRADE_RESULT! neq 0 (
    echo   Failed to upgrade pip using '!PYTHON_EXE! -m pip install --upgrade pip'. (Errorlevel: !PIP_UPGRADE_RESULT!)
    echo   Continuing with dependencies installation, but pip might be outdated.
)

echo   Installing project dependencies from requirements.txt...
cd /d "%~dp0src"
if not exist requirements.txt (
    echo   ERROR: requirements.txt not found in src directory
    goto :EOF_ERROR
)

!PYTHON_EXE! -m pip install -r requirements.txt
set INSTALL_RESULT=!ERRORLEVEL!
if !INSTALL_RESULT! neq 0 (
    echo   --------------------------------------------------------------------
    echo   ERROR: Failed to install project dependencies (Errorlevel: !INSTALL_RESULT!).
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
echo ==========================================================================
echo Installation script completed successfully.
echo All dependencies have been installed.
echo You can now run the Dota 2 Auto Accept application using auto_accept.bat
echo ==========================================================================


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
