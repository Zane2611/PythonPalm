@echo off
setlocal

cd /d "%~dp0"

py -m pip install -r requirements.txt
py -m PyInstaller --noconfirm --clean --onefile --windowed --name DinoRunner --add-data "assets;assets" mainDinoRunner.py

echo.
echo Build complete. Your exe is in the dist\DinoRunner folder.
pause