# Globex Installation Files

## Available Installers

### 1. Linux (x86_64)
**File:** `globex-linux-x86_64`
- **Type:** Standalone executable
- **Size:** ~16MB
- **Usage:** 
  ```bash
  chmod +x globex-linux-x86_64
  ./globex-linux-x86_64
  ```
- Opens dashboard in your default browser at http://127.0.0.1:5001

### 2. Windows (.exe)
**Note:** The Windows .exe file must be built on a Windows machine.

**Option A - Build on Windows:**
1. Copy the `windows_app.py` and all source files to a Windows machine
2. Install Python 3.8+ on Windows
3. Run:
   ```cmd
   pip install pyinstaller flask flask-cors
   pyinstaller --onefile --windowed --name Globex windows_app.py
   ```
4. Find `Globex.exe` in the `dist` folder

**Option B - Use Portable Version:**
- The `dist/windows/globex-portable/` folder contains all necessary files
- Run `run.bat` to start the application on Windows

### 3. Android (.apk)
**Note:** The APK must be built using Android Studio or the command line build tools.

**Build Instructions:**
1. Open the project in Android Studio (folder: `android_app/` or root project)
2. Ensure you have:
   - Android SDK installed
   - JDK 17+
   - Gradle 8.0+
3. Build the APK:
   ```bash
   ./gradlew assembleDebug
   ```
4. Find the APK at: `app/build/outputs/apk/debug/app-debug.apk`

**Or use Android Studio:**
- File → Build Bundle(s) / APK(s) → Build APK(s)

## Source Files Location
- **Windows entry point:** `windows_app.py`
- **Linux entry point:** Same as Windows (cross-platform)
- **Android project:** `android_app/` directory and root project with Gradle files

## Requirements

### Linux/Windows Desktop
- Python 3.8+ (if building from source)
- Flask, Flask-CORS
- Modern web browser

### Android
- Android 8.0 (API 26) or higher
- ARM64 or x86_64 device

## Verification
Checksums for available files are in `checksums.txt`
