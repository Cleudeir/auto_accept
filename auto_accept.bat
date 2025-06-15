@echo off
setlocal enableDelayedExpansion

echo Starting installation process...

REM ==========================================================================
REM Check and Install curl
REM ==========================================================================
echo(
echo [1/3] Checking for curl...
where curl >nul 2>&1
if !ERRORLEVEL! equ 0 (
    echo   curl is already installed.
    goto :PYTHON_CHECK
)

echo   curl not found. Attempting to install using winget...
where winget >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   winget is not available.
    echo   Please install curl manually (e.g., from https://curl.se/windows/) ^& ensure it's in your PATH.
    goto :EOF_ERROR
)

winget search Microsoft.Curl >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   Microsoft.Curl package not found via winget.
    echo   Please install curl manually (e.g., from https://curl.se/windows/) ^& ensure it's in your PATH.
    goto :EOF_ERROR
)

echo   Attempting to install Microsoft.Curl via winget...
winget install -e --id Microsoft.Curl --source winget --accept-package-agreements --accept-source-agreements
if !ERRORLEVEL! neq 0 (
    echo   Failed to install curl using winget (Errorlevel: !ERRORLEVEL!).
    echo   Please try installing curl manually (e.g., from https://curl.se/windows/) ^& ensure it's in your PATH.
    goto :EOF_ERROR
)

echo   curl installed successfully via winget.
echo   You might need to open a new command prompt for changes to take effect.
REM Re-check if curl is now available in the current session
where curl >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   curl still not found in PATH after winget install. Please open a new command prompt ^& re-run this script.
    goto :EOF_ERROR
)

:PYTHON_CHECK
REM ==========================================================================
REM Check and Install Python
REM ==========================================================================
echo(
echo [2/3] Checking for Python...
set "PYTHON_EXE="
where python >nul 2>&1
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

echo   Python not found. Attempting to install Python 3 using winget...
where winget >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   winget is not available.
    echo   Please install Python 3 manually (from https://www.python.org/downloads/) ^& ensure it's added to your PATH.
    goto :EOF_ERROR
)

winget search Python.Python.3 >nul 2>&1
if !ERRORLEVEL! neq 0 (
    echo   Python.Python.3 package not found via winget.
    echo   Please install Python 3 manually (from https://www.python.org/downloads/) ^& ensure it's added to your PATH.
    goto :EOF_ERROR
)

echo   Attempting to install Python.Python.3 via winget...
winget install -e --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements
if !ERRORLEVEL! neq 0 (
    echo   Failed to install Python using winget (Errorlevel: !ERRORLEVEL!).
    echo   Please install Python 3 manually (from https://www.python.org/downloads/) ^& ensure it's added to your PATH.
    goto :EOF_ERROR
)

echo   Python 3 installed successfully via winget.
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

echo   Python still not found in PATH even after winget install.
echo   Please open a new command prompt ^& re-run this script, or ensure Python is correctly installed ^& in PATH.
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
echo [3/3] Installing/Upgrading pip ^& installing project dependencies...

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
