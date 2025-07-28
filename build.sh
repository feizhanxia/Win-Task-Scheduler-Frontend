# Build script for creating executable

# Install required packages first
pip install pyinstaller streamlit jinja2 croniter

# Create the executable using PyInstaller
pyinstaller TaskScheduler.spec --clean --noconfirm

echo "Build complete! The executable is in the dist folder."
