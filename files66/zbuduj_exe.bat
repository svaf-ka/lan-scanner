@echo off
cd /d "%~dp0"
echo Instaluje PyInstaller...
python -m pip install pyinstaller
echo.
echo Buduje aplikacje...
python -m PyInstaller --onefile --windowed --icon "lan-scanner.ico" --name "Skaner sieci" skaner_gui.py
echo.
echo Gotowe! Plik "Skaner sieci.exe" jest w folderze dist
pause
