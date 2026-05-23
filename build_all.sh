#!/bin/bash

# Globex Multi-Platform Build Script
# Builds installers for Windows, Linux, and Android

set -e

echo "=========================================="
echo "GLOBEX MULTI-PLATFORM BUILD SYSTEM"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create dist directory
mkdir -p dist

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_status "Python 3 found: $(python3 --version)"
    else
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check Java for Android
    if command -v java &> /dev/null; then
        print_status "Java found: $(java -version 2>&1 | head -1)"
    else
        print_warning "Java not found - Android build may fail"
    fi
    
    # Check Gradle
    if command -v gradle &> /dev/null || [ -f "./gradlew" ]; then
        print_status "Gradle found"
    else
        print_warning "Gradle not found - will use gradlew wrapper"
    fi
}

# Build Linux AppImage
build_linux() {
    echo ""
    echo "=========================================="
    echo "BUILDING LINUX INSTALLER (AppImage)"
    echo "=========================================="
    
    mkdir -p dist/linux/AppDir/usr/bin/globex
    mkdir -p dist/linux/AppDir/usr/share/applications
    mkdir -p dist/linux/AppDir/usr/share/icons/hicolor/256x256/apps
    
    # Copy application files
    cp -r *.py dist/linux/AppDir/usr/bin/globex/ 2>/dev/null || true
    cp requirements.txt dist/linux/AppDir/usr/bin/globex/ 2>/dev/null || true
    
    # Create desktop file
    cat > dist/linux/AppDir/globex.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Globex
Comment=Globex Blockchain Platform
Exec=globex-wrapper
Icon=globex
Categories=Network;P2P;
Terminal=true
EOF
    
    # Create wrapper script
    cat > dist/linux/AppDir/globex-wrapper << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/usr/bin/globex"
python3 dashboard.py
EOF
    
    chmod +x dist/linux/AppDir/globex-wrapper
    
    # Create simple icon (placeholder)
    echo "Creating placeholder icon..."
    convert -size 256x256 xc:#4CAF50 -fill white -gravity center \
        -pointsize 48 -annotate 0 "GLOBEX" \
        dist/linux/AppDir/usr/share/icons/hicolor/256x256/apps/globex.png 2>/dev/null || \
    cp /usr/share/icons/hicolor/256x256/apps/help.png \
        dist/linux/AppDir/usr/share/icons/hicolor/256x256/apps/globex.png 2>/dev/null || \
    echo "Icon creation skipped"
    
    # Download appimagetool
    if [ ! -f "dist/linux/appimagetool" ]; then
        echo "Downloading appimagetool..."
        wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage \
            -O dist/linux/appimagetool || print_warning "Could not download appimagetool"
        chmod +x dist/linux/appimagetool 2>/dev/null || true
    fi
    
    # Build AppImage
    cd dist/linux
    if [ -x "./appimagetool" ]; then
        ARCH=x86_64 ./appimagetool AppDir globex-linux-x86_64.AppImage 2>/dev/null && \
            print_status "Linux AppImage created: globex-linux-x86_64.AppImage" || \
            print_warning "AppImage creation failed, creating tarball instead"
    fi
    
    # Create tarball as fallback
    cd ../../
    tar -czf dist/globex-linux-x86_64.tar.gz -C dist/linux/AppDir .
    print_status "Linux tarball created: dist/globex-linux-x86_64.tar.gz"
    
    cd ..
}

# Build Windows Installer
build_windows() {
    echo ""
    echo "=========================================="
    echo "BUILDING WINDOWS INSTALLER (NSIS/Setup)"
    echo "=========================================="
    
    mkdir -p dist/windows
    
    # Create Python executable using PyInstaller
    print_status "Creating Windows executable with PyInstaller..."
    
    # Install PyInstaller if needed
    pip3 install pyinstaller --quiet 2>/dev/null || true
    
    # Create spec file for PyInstaller
    cat > dist/windows/globex.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dashboard.py'],
    pathex=[],
    binaries=[],
    datas=[('requirements.txt', '.')],
    hiddenimports=[
        'Crypto',
        'Crypto.Hash.SHA256',
        'Crypto.PublicKey.ECC',
        'ecdsa',
        'flask',
        'flask_cors',
        'websocket',
        'numpy',
        'matplotlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Globex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
EOF
    
    # Try to build with PyInstaller (if on Windows or cross-compiling)
    if command -v pyinstaller &> /dev/null; then
        cd dist/windows
        pyinstaller globex.spec 2>/dev/null && \
            print_status "Windows executable created" || \
            print_warning "PyInstaller build failed"
        cd ../..
    fi
    
    # Create NSIS installer script
    cat > dist/windows/installer.nsi << 'EOF'
!include "MUI2.nsh"

Name "Globex Blockchain Platform"
OutFile "globex-windows-installer.exe"
InstallDir "$PROGRAMFILES\\Globex"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "Globex" SecDefault
    SetOutPath "$INSTDIR"
    File /r "dist\windows\dist\Globex\*.*"
    WriteRegStr HKLM SOFTWARE\Globex "Install_Dir" "$INSTDIR"
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\Globex"
    CreateShortCut "$SMPROGRAMS\Globex\Globex.lnk" "$INSTDIR\Globex.exe"
    CreateShortCut "$DESKTOP\Globex.lnk" "$INSTDIR\Globex.exe"
SectionEnd

Section "Uninstall"
    DeleteRegKey HKLM SOFTWARE\Globex
    Delete "$INSTDIR\uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\Globex\Globex.lnk"
    Delete "$DESKTOP\Globex.lnk"
    RMDir "$SMPROGRAMS\Globex"
SectionEnd
EOF
    
    # Create a simple zip distribution
    if [ -d "dist/windows/dist/Globex" ]; then
        cd dist/windows/dist
        zip -r ../../globex-windows-x86_64.zip Globex/
        cd ../../..
        print_status "Windows ZIP created: dist/globex-windows-x86_64.zip"
    else
        # Fallback: create a portable package
        mkdir -p dist/windows/globex-portable
        cp -r ../*.py dist/windows/globex-portable/ 2>/dev/null || true
        cp ../requirements.txt dist/windows/globex-portable/ 2>/dev/null || true
        cat > dist/windows/globex-portable/run.bat << 'EOF'
@echo off
echo Starting Globex...
python dashboard.py
pause
EOF
        cd dist/windows
        zip -r ../globex-windows-portable.zip globex-portable/ 2>/dev/null || true
        cd ../..
        print_status "Windows portable created: dist/globex-windows-portable.zip"
    fi
}

# Build Android APK
build_android() {
    echo ""
    echo "=========================================="
    echo "BUILDING ANDROID APK"
    echo "=========================================="
    
    mkdir -p dist/android
    
    # Check if Gradle wrapper exists
    if [ -f "./gradlew" ]; then
        GRADLE_CMD="./gradlew"
    elif command -v gradle &> /dev/null; then
        GRADLE_CMD="gradle"
    else
        print_warning "Gradle not found, attempting to use gradlew wrapper"
        GRADLE_CMD="./gradlew"
    fi
    
    # Make gradlew executable
    if [ -f "./gradlew" ]; then
        chmod +x ./gradlew
    fi
    
    # Build debug APK
    print_status "Building Android debug APK..."
    if [ -d "android_app" ]; then
        cd android_app
        if $GRADLE_CMD assembleDebug 2>&1 | tee ../dist/android/build.log; then
            # Find the APK
            APK_PATH=$(find . -name "*.apk" -type f | head -1)
            if [ -n "$APK_PATH" ]; then
                cp "$APK_PATH" ../dist/globex-android-debug.apk
                print_status "Android APK created: dist/globex-android-debug.apk"
            fi
        else
            print_warning "Gradle build failed, check dist/android/build.log"
        fi
        cd ..
    elif [ -d "app" ]; then
        if $GRADLE_CMD assembleDebug 2>&1 | tee dist/android/build.log; then
            APK_PATH=$(find . -path "*/build/outputs/apk/debug/*.apk" -type f | head -1)
            if [ -n "$APK_PATH" ]; then
                cp "$APK_PATH" dist/globex-android-debug.apk
                print_status "Android APK created: dist/globex-android-debug.apk"
            fi
        else
            print_warning "Gradle build failed, check dist/android/build.log"
        fi
    else
        print_warning "No Android project found"
    fi
}

# Generate checksums
generate_checksums() {
    echo ""
    echo "=========================================="
    echo "GENERATING CHECKSUMS"
    echo "=========================================="
    
    cd dist
    for file in *; do
        if [ -f "$file" ] && [ "$file" != "checksums.txt" ]; then
            sha256sum "$file" >> checksums.txt
        fi
    done
    
    if [ -f "checksums.txt" ]; then
        print_status "Checksums generated: dist/checksums.txt"
        cat checksums.txt
    fi
    
    cd ..
}

# Main execution
main() {
    check_prerequisites
    
    echo ""
    echo "Starting build process..."
    echo ""
    
    # Build for each platform
    build_linux
    build_windows
    build_android
    
    # Generate checksums
    generate_checksums
    
    echo ""
    echo "=========================================="
    echo "BUILD COMPLETE"
    echo "=========================================="
    echo ""
    echo "Distribution files:"
    ls -lh dist/
    echo ""
    echo "Download links will be available after pushing to GitHub."
    echo ""
}

# Run main function
main "$@"
