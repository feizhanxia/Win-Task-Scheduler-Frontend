@echo off
REM Build script for creating executable on Windows

REM Install required packages first
pip install pyinstaller streamlit jinja2 croniter

REM Create the executable using PyInstaller
pyinstaller TaskScheduler.spec --clean --noconfirm

echo Build complete! The executable is in the dist folder.
pause
