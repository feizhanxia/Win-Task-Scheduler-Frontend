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


def open_browser_delayed():
    """Open browser after delay."""
    time.sleep(4)
    for _ in range(15):  # Try for 15 seconds
        if is_port_in_use(8501):
            try:
                webbrowser.open('http://localhost:8501')
                print("Browser opened automatically.")
                return
            except:
                pass
        time.sleep(1)
    print("Please manually open: http://localhost:8501")


def main():
    """Main function to start the Streamlit application."""
    
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        bundle_dir = Path(sys._MEIPASS)
        app_path = bundle_dir / 'app.py'
    else:
        bundle_dir = Path(__file__).parent
        app_path = bundle_dir / 'app.py'
    
    os.chdir(bundle_dir)
    
    # Check if already running
    if is_port_in_use(8501):
        print("Server already running at http://localhost:8501")
        try:
            webbrowser.open('http://localhost:8501')
        except:
            pass
        input("Press Enter to exit...")
        return
    
    print("="*60)
    print("         Windows Task Scheduler Frontend")
    print("="*60)
    print("Starting server... Browser will open automatically.")
    print("If not, visit: http://localhost:8501")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    # Start browser opener in background
    threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    # Start streamlit
    try:
        subprocess.call([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false", 
            "--browser.gatherUsageStats=false",
            "--server.port=8501"
        ])
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
