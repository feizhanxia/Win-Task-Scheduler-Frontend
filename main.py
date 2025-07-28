#!/usr/bin/env python3
"""
Main entry point for the packaged Streamlit application.
This script handles the proper initialization and execution of the Streamlit app.
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading
from pathlib import Path
import socket


def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def open_browser_once():
    """Open browser only once after server starts."""
    # Wait for server to fully start
    time.sleep(3)
    
    # Check if server is responding
    max_attempts = 10
    for _ in range(max_attempts):
        if is_port_in_use(8501):
            try:
                webbrowser.open('http://localhost:8501')
                print("Browser opened automatically.")
                break
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                break
        time.sleep(1)
    else:
        print("Server did not start in time, please open browser manually.")


def main():
    """Main function to start the Streamlit application."""
    
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        app_path = bundle_dir / 'app.py'
    else:
        # Running in a normal Python environment
        bundle_dir = Path(__file__).parent
        app_path = bundle_dir / 'app.py'
    
    # Change to the application directory
    os.chdir(bundle_dir)
    
    try:
        # Check if server is already running
        if is_port_in_use(8501):
            print("="*50)
            print("Streamlit server is already running on port 8501!")
            print("Please open your browser and go to: http://localhost:8501")
            print("Or stop the existing server and try again.")
            print("="*50)
            input("Press Enter to exit...")
            return
        
        # Start browser in a separate thread (only once)
        browser_thread = threading.Thread(target=open_browser_once)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Use subprocess to run streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.headless=true",
            "--server.enableCORS=false", 
            "--server.enableXsrfProtection=false",
            "--browser.gatherUsageStats=false",
            "--server.port=8501",
            "--global.developmentMode=false"
        ]
        
        print("="*50)
        print("Windows Task Scheduler Frontend")
        print("="*50)
        print("Starting Streamlit server...")
        print("Browser will open automatically in a few seconds...")
        print()
        print("If browser doesn't open, go to: http://localhost:8501")
        print()
        print("Press Ctrl+C to stop the application")
        print("="*50)
        
        # Run the command
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n" + "="*50)
        print("Application stopped by user.")
        print("="*50)
    except Exception as e:
        print(f"\nError starting Streamlit application: {e}")
        print("\nPossible solutions:")
        print("1. Make sure Python is properly installed")
        print("2. Try running as administrator")
        print("3. Check if port 8501 is available")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
