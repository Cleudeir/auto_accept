
@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo            Dota 2 Auto Accept Installer
echo ====================================================
echo.

:: Check if Python is installed

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Downloading and installing Python...
    
    :: Check if PowerShell is available
    powershell -Command "Get-Command" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo PowerShell is required but not available.
        echo Please install Python 3.9 or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo Downloading Python installer...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile '%TEMP%\python-installer.exe'}"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to download Python installer.
        echo Please install Python 3.9 or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo Installing Python...
    %TEMP%\python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Python.
        echo Please install Python 3.9 or later manually from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo Python has been installed successfully.
    
    :: Refresh environment variables
    echo Refreshing environment variables...
    call refreshenv.cmd >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        :: If refreshenv isn't available, notify user to restart command prompt
        echo Please close this command prompt and open a new one to continue with installation.
        pause
        exit /b 0
    )
) else (
    echo Python is already installed.
)

:: Verify Python is in PATH
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python was installed, but isn't available in the current session.
    echo Please restart this script to continue.
    pause
    exit /b 0
)

:: Install required packages
echo.
echo Installing required Python packages...
python -m pip install --upgrade pip
python -m pip install -r src/requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install some Python packages.
    echo You may need to run this script as administrator.
    pause
    exit /b 1
)

echo.
echo Creating desktop shortcut...

:: Create a batch file to launch the application
echo @echo off > "%~dp0auto_accept.bat"
echo cd "%~dp0src" >> "%~dp0auto_accept.bat"
echo start /min pythonw main.py >> "%~dp0auto_accept.bat"

:: Create desktop shortcut
set "desktopPath=%USERPROFILE%\Desktop"
set "iconPath=%~dp0src\bin\icon.ico"
set "scriptPath=%~dp0auto_accept.bat"
set "shortcutName=Dota 2 Auto Accept.lnk"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%desktopPath%\%shortcutName%'); $Shortcut.TargetPath = '%scriptPath%'; $Shortcut.IconLocation = '%iconPath%'; $Shortcut.Save()"

if %ERRORLEVEL% NEQ 0 (
    echo Failed to create desktop shortcut.
) else (
    echo Desktop shortcut created successfully.
)

echo.
echo ====================================================
echo Installation completed successfully!
echo.
echo To run Dota 2 Auto Accept, double-click on the desktop shortcut
echo or run auto_accept.bat from the installation folder.
echo ====================================================
echo.
pause