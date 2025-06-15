@echo off

:: Check for Administrator privileges
openfiles >nul 2>&1
if not %errorlevel%==0 echo ===========================================================================
if not %errorlevel%==0 echo WARNING: This script is not running as Administrator.
if not %errorlevel%==0 echo Some installation steps may fail without elevated privileges.
if not %errorlevel%==0 echo Please right-click and 'Run as administrator' if you encounter issues.
if not %errorlevel%==0 echo ===========================================================================
if not %errorlevel%==0 echo(

echo ===========================================================================
echo Python Silent Installation Script
echo ===========================================================================
echo This script will install Python 3.13.1 in silent mode without any checks.
echo(

REM Set the path to the Python installer
set "PYTHON_INSTALLER=%~dp0dependencies\python-3.13.1-amd64.exe"

echo Installing Python from: %PYTHON_INSTALLER%
echo(

REM Check if installer exists
if not exist "%PYTHON_INSTALLER%" echo ERROR: Python installer not found at %PYTHON_INSTALLER%
if not exist "%PYTHON_INSTALLER%" echo Please ensure the Python installer is in the dependencies folder.
if not exist "%PYTHON_INSTALLER%" pause
if not exist "%PYTHON_INSTALLER%" exit /b 1

echo Starting Python installation in silent mode...
echo This may take a few minutes. Please wait...
echo(

REM Install Python silently
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0 Include_dev=0 Include_debug=0 InstallLauncherAllUsers=1 AssociateFiles=1

set INSTALL_RESULT=%ERRORLEVEL%
echo(
if not %INSTALL_RESULT%==0 goto install_fail

echo ===========================================================================
echo Python installer completed. Validating installation...
echo ===========================================================================
timeout /t 3 /nobreak >nul
echo Checking if Python is accessible...
set PYTHON_FOUND=0
set PYTHON_LAUNCHER_FOUND=0
python --version >nul 2>&1
if %ERRORLEVEL%==0 set PYTHON_FOUND=1
py --version >nul 2>&1
if %ERRORLEVEL%==0 set PYTHON_LAUNCHER_FOUND=1

if %PYTHON_FOUND%==1 echo [OK] Python command is working:
if %PYTHON_FOUND%==1 python --version
if not %PYTHON_FOUND%==1 echo [FAIL] Python command not found in PATH
if %PYTHON_LAUNCHER_FOUND%==1 echo [OK] Python Launcher (py) is working
if not %PYTHON_LAUNCHER_FOUND%==1 echo [FAIL] Python Launcher (py) not found

echo Checking if pip is accessible...
set PIP_FOUND=0
python -m pip --version >nul 2>&1
if %ERRORLEVEL%==0 set PIP_FOUND=1
if %ERRORLEVEL%==0 echo [OK] pip is working with python command
if not %ERRORLEVEL%==0 py -m pip --version >nul 2>&1
if not %ERRORLEVEL%==0 if %ERRORLEVEL%==0 set PIP_FOUND=1
if not %ERRORLEVEL%==0 if %ERRORLEVEL%==0 echo [OK] pip is working with py launcher
if not %PIP_FOUND%==1 echo [FAIL] pip is not accessible

echo(
if %PYTHON_FOUND%==1 goto success
goto warn_incomplete

:success
echo ===========================================================================
echo SUCCESS: Python is installed and working!
echo ===========================================================================
echo Installation completed with the following features:
echo - Installed for all users
echo - Added to system PATH
echo - Python Launcher installed
echo - .py files associated with Python
echo - Test files, documentation, and debug files excluded for space saving
echo(
echo Python is ready to use!
echo ===========================================================================
echo(
echo NOTE: If 'python' or 'py' is not recognized in new terminals, restart your command prompt or computer to refresh PATH.
echo ===========================================================================
goto end

:warn_incomplete
echo ===========================================================================
echo WARNING: Installation may not be complete
echo ===========================================================================
echo The installer completed, but Python is not accessible from command line.
echo This might be because:
echo - PATH changes require a system restart
echo - Installation needs Administrator privileges
echo - A reboot is required for changes to take effect
echo(
echo Try restarting your command prompt or computer and test again with:
echo   python --version
echo   py --version
echo ===========================================================================
goto end

:install_fail
echo ===========================================================================
echo ERROR: Python installation failed with error code: %INSTALL_RESULT%
echo ===========================================================================
echo Possible reasons:
echo - Insufficient privileges (try running as Administrator)
echo - Python is already installed
echo - System incompatibility
echo - Corrupted installer file
echo(
echo Please try running this script as Administrator or check the installer.
echo ===========================================================================
goto end

:end
echo(
echo Press any key to exit...
pause >nul
exit /b %INSTALL_RESULT%
