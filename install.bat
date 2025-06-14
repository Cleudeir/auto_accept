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
REM Install/Upgrade pip and install pycurl
REM ==========================================================================
echo(
echo [3/3] Installing/Upgrading pip ^& installing pycurl...

echo   Ensuring pip is available ^& upgrading it...
!PYTHON_EXE! -m ensurepip --upgrade
if !ERRORLEVEL! neq 0 (
    echo   Failed to ensure/upgrade pip using '!PYTHON_EXE! -m ensurepip --upgrade'. (Errorlevel: !ERRORLEVEL!)
    goto :EOF_ERROR
)

!PYTHON_EXE! -m pip install --upgrade pip
if !ERRORLEVEL! neq 0 (
    echo   Failed to upgrade pip using '!PYTHON_EXE! -m pip install --upgrade pip'. (Errorlevel: !ERRORLEVEL!)
    echo   Continuing with pycurl installation, but pip might be outdated.
)

echo   Attempting to install pycurl...
!PYTHON_EXE! -m pip install pycurl
if !ERRORLEVEL! neq 0 (
    echo   --------------------------------------------------------------------
    echo   ERROR: Failed to install pycurl (Errorlevel: !ERRORLEVEL!).
    echo   pycurl can be difficult to install on Windows due to dependencies
    echo   on libcurl ^& C compilers.
    echo(
    echo   Possible solutions:
    echo   1. Install Microsoft C++ Build Tools:
    echo      Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo      Download the Build Tools, ^& during installation, select the
    echo      "C++ build tools" workload.
    echo(
    echo   2. Try installing from an unofficial binary wheel if available:
    echo      Search for "pycurl windows whl" on sites like Christoph Gohlke's
    echo      Python Extension Packages for Windows (https://www.lfd.uci.edu/~gohlke/pythonlibs/).
    echo      If you download a .whl file, install it with:
    echo      !PYTHON_EXE! -m pip install path\to\yourfile.whl
    echo(
    echo   3. Consider using the 'requests' library as an alternative for HTTP tasks:
    echo      !PYTHON_EXE! -m pip install requests
    echo   --------------------------------------------------------------------
    goto :EOF_ERROR
)

echo   pycurl installed successfully.

echo(
echo ==========================================================================
echo Installation script completed successfully.
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
pause
exit /b 0
