"""
Build script to convert the Globex Python Dashboard into a Windows .exe application.
Uses PyInstaller to bundle Python, Flask, and dependencies into a single executable.

Prerequisites:
    pip install pyinstaller flask ecdsa

Usage:
    python build_windows.py
"""
import os
import sys
import PyInstaller.__main__

def build():
    print("🏗️  Building Globex Windows Application...")
    
    # Arguments for PyInstaller
    args = [
        'windows_app.py',              # Main entry point
        '--name=GlobexWallet',         # Name of the exe
        '--onefile',                   # Bundle everything into one file
        '--windowed',                  # No console window (GUI mode)
        '--icon=NONE',                 # You can add a .ico file here later
        '--add-data=dashboard.py;.',   # Include dashboard file
        '--hidden-import=flask',       # Ensure Flask is included
        '--hidden-import=ecdsa',       # Ensure ecdsa is included
        '--clean',                     # Clean cache before building
        '--noconfirm'                  # Overwrite existing build without asking
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build successful!")
        print("📦 Your application is located in the 'dist' folder as 'GlobexWallet.exe'")
        print("💡 Tip: You can double-click GlobexWallet.exe to run the wallet.")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
