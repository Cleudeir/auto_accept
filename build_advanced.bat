@echo off
setlocal enabledelayedexpansion

:: Set title and colors
title Dota 2 Auto Accept - Advanced Build Script
color 0A

:: Parse command line arguments
set BUILD_TYPE=onefile
set DEBUG=0
set CLEAN=0

:parse_args
if "%~1"=="" goto :end_parse_args
if /i "%~1"=="--onedir" set BUILD_TYPE=onedir
if /i "%~1"=="--debug" set DEBUG=1
if /i "%~1"=="--clean" set CLEAN=1
shift
goto :parse_args
:end_parse_args

:: Header
echo ========================================================
echo             Dota 2 Auto Accept - Build Script
echo ========================================================
echo.

:: Clean build directories if requested
if %CLEAN%==1 (
    echo Cleaning previous build files...
    if exist "build" rmdir /s /q "build"
    if exist "dist" rmdir /s /q "dist"
    echo Build directories cleaned.
    echo.
)

:: Install dependencies
echo Installing required dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    goto :error
)
echo Dependencies installed successfully.
echo.

:: Set PyInstaller options based on build type and debug mode
set "PYINSTALLER_OPTS=--name "Dota2AutoAccept" --icon=icon.ico"

if %DEBUG%==1 (
    set "PYINSTALLER_OPTS=!PYINSTALLER_OPTS! --debug all"
    echo Building in DEBUG mode...
) else (
    set "PYINSTALLER_OPTS=!PYINSTALLER_OPTS! --noconsole"
    echo Building in RELEASE mode...
)

if "%BUILD_TYPE%"=="onefile" (
    set "PYINSTALLER_OPTS=!PYINSTALLER_OPTS! --onefile"
    echo Building as SINGLE FILE executable...
) else (
    echo Building as DIRECTORY with separate files...
)

:: Add data files
set "PYINSTALLER_OPTS=!PYINSTALLER_OPTS! --add-data "dota.png;." --add-data "print.png;." --add-data "dota2.mp3;." --add-data "icon.ico;." --add-data "config.json;.""

:: Add hidden imports
set "PYINSTALLER_OPTS=!PYINSTALLER_OPTS! --hidden-import PIL --hidden-import numpy --hidden-import cv2 --hidden-import mss --hidden-import skimage.metrics --hidden-import sounddevice --hidden-import pygame"

echo.
echo Creating executable with PyInstaller...
echo Command: pyinstaller %PYINSTALLER_OPTS% accept.py
pyinstaller %PYINSTALLER_OPTS% accept.py

if %errorlevel% neq 0 (
    echo Error building executable!
    goto :error
)

echo.
echo Build completed successfully!

:: Create distribution package
if "%BUILD_TYPE%"=="onefile" (
    echo Creating distribution package...
    
    :: Create folder for distribution
    if not exist "dist\package" mkdir "dist\package"
    
    :: Copy executable and required files
    copy "dist\Dota2AutoAccept.exe" "dist\package\" /Y
    copy "dota.png" "dist\package\" /Y
    copy "print.png" "dist\package\" /Y
    copy "dota2.mp3" "dist\package\" /Y
    copy "icon.ico" "dist\package\" /Y
    copy "config.json" "dist\package\" /Y
    
    :: Create ZIP archive
    echo Creating ZIP archive...
    powershell -Command "Compress-Archive -Path 'dist\package\*' -DestinationPath 'dist\Dota2AutoAccept_Package.zip' -Force"
    
    echo.
    echo Distribution package created at:
    echo dist\Dota2AutoAccept_Package.zip
) else (
    :: For onedir builds, just zip the directory
    echo Creating ZIP archive of directory build...
    powershell -Command "Compress-Archive -Path 'dist\Dota2AutoAccept\*' -DestinationPath 'dist\Dota2AutoAccept_Package.zip' -Force"
    
    echo.
    echo Distribution package created at:
    echo dist\Dota2AutoAccept_Package.zip
)

echo.
echo ========================================================
echo                       BUILD SUMMARY
echo ========================================================
echo Build Type: %BUILD_TYPE%
echo Debug Mode: %DEBUG%
if "%BUILD_TYPE%"=="onefile" (
    echo Executable: dist\Dota2AutoAccept.exe
) else (
    echo Executable: dist\Dota2AutoAccept\Dota2AutoAccept.exe
)
echo Package: dist\Dota2AutoAccept_Package.zip
echo.

goto :end

:error
echo.
echo ========================================================
echo                       BUILD FAILED
echo ========================================================
echo.
exit /b 1

:end
echo Press any key to exit...
pause > nul
