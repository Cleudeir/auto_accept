@echo off
echo =============================================
echo Dota 2 Auto Accept - Build Script
echo =============================================

echo Installing required dependencies...
pip install -r requirements.txt

echo.
echo Creating executable with PyInstaller...
pyinstaller --onefile ^
    --name "Dota2AutoAccept" ^
    --icon=icon.ico ^
    --noconsole ^
    --add-data "dota.png;." ^
    --add-data "print.png;." ^
    --add-data "dota2.mp3;." ^
    --add-data "icon.ico;." ^
    --add-data "config.json;." ^
    --hidden-import PIL ^
    --hidden-import numpy ^
    --hidden-import cv2 ^
    --hidden-import mss ^
    --hidden-import skimage.metrics ^
    --hidden-import sounddevice ^
    --hidden-import pygame ^
    accept.py

echo.
echo Copying additional files to dist folder...
if not exist "dist\Dota2AutoAccept" mkdir "dist\Dota2AutoAccept"
copy "dota.png" "dist\Dota2AutoAccept\" /Y
copy "print.png" "dist\Dota2AutoAccept\" /Y
copy "dota2.mp3" "dist\Dota2AutoAccept\" /Y
copy "icon.ico" "dist\Dota2AutoAccept\" /Y
copy "config.json" "dist\Dota2AutoAccept\" /Y
copy "dist\Dota2AutoAccept.exe" "dist\Dota2AutoAccept\" /Y

echo.
echo Creating ZIP archive...
powershell -Command "Compress-Archive -Path 'dist\Dota2AutoAccept\*' -DestinationPath 'dist\Dota2AutoAccept.zip' -Force"

echo.
echo Build complete! You can find the executable in:
echo dist\Dota2AutoAccept\Dota2AutoAccept.exe
echo Or use the complete ZIP package at:
echo dist\Dota2AutoAccept.zip
echo.
echo Press any key to exit...
pause > nul
