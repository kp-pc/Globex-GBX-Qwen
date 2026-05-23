#!/bin/bash

# Globex Multi-Platform Build Script
set -e

echo "=========================================="
echo "GLOBEX MULTI-PLATFORM BUILD SYSTEM"
echo "=========================================="

mkdir -p dist

# Build Linux
build_linux() {
    echo ""
    echo "BUILDING LINUX INSTALLER"
    echo "=========================================="
    
    mkdir -p dist/linux/AppDir/usr/bin/globex
    
    cp -r *.py dist/linux/AppDir/usr/bin/globex/ 2>/dev/null || true
    cp requirements.txt dist/linux/AppDir/usr/bin/globex/ 2>/dev/null || true
    
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
    
    cat > dist/linux/AppDir/globex-wrapper << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/usr/bin/globex"
python3 dashboard.py
EOF
    
    chmod +x dist/linux/AppDir/globex-wrapper
    
    tar -czf dist/globex-linux-x86_64.tar.gz -C dist/linux/AppDir .
    echo "[✓] Linux tarball created: dist/globex-linux-x86_64.tar.gz"
}

# Build Windows
build_windows() {
    echo ""
    echo "BUILDING WINDOWS INSTALLER"
    echo "=========================================="
    
    mkdir -p dist/windows/globex-portable
    
    cp -r *.py dist/windows/globex-portable/ 2>/dev/null || true
    cp requirements.txt dist/windows/globex-portable/ 2>/dev/null || true
    
    cat > dist/windows/globex-portable/run.bat << 'EOF'
@echo off
echo Starting Globex...
python dashboard.py
pause
EOF
    
    cd dist/windows
    zip -r globex-windows-portable.zip globex-portable/ 2>/dev/null || true
    cd ../..
    
    echo "[✓] Windows portable created: dist/globex-windows-portable.zip"
}

# Build Android
build_android() {
    echo ""
    echo "BUILDING ANDROID APK"
    echo "=========================================="
    
    if [ -d "android_app" ]; then
        if command -v gradle &> /dev/null; then
            cd android_app
            gradle assembleDebug 2>&1 | tail -5
            APK=$(find . -name "*.apk" -type f | head -1)
            if [ -n "$APK" ]; then
                cp "$APK" ../dist/globex-android-debug.apk
                echo "[✓] Android APK created: dist/globex-android-debug.apk"
            else
                echo "[!] APK not found, creating info file"
                echo "Android build requires Gradle setup" > ../dist/globex-android-info.txt
            fi
            cd ..
        else
            echo "[!] Gradle not found - Android build skipped"
            echo "To build Android APK manually:" > dist/android-build-instructions.txt
            echo "1. Install Android Studio or Gradle" >> dist/android-build-instructions.txt
            echo "2. Run: cd android_app && gradle assembleDebug" >> dist/android-build-instructions.txt
        fi
    elif [ -d "app" ]; then
        echo "[!] Android project structure needs Gradle wrapper"
        echo "Manual build required for Android" > dist/android-build-info.txt
    else
        echo "[!] No Android project found"
    fi
}

# Generate checksums
generate_checksums() {
    echo ""
    echo "GENERATING CHECKSUMS"
    echo "=========================================="
    
    cd dist
    rm -f checksums.txt
    for file in *; do
        if [ -f "$file" ] && [ "$file" != "checksums.txt" ]; then
            sha256sum "$file" >> checksums.txt
        fi
    done
    
    if [ -f "checksums.txt" ]; then
        echo "[✓] Checksums generated: dist/checksums.txt"
        cat checksums.txt
    fi
    
    cd ..
}

# Main
main() {
    echo ""
    echo "Starting build process..."
    echo ""
    
    build_linux
    build_windows
    build_android
    generate_checksums
    
    echo ""
    echo "=========================================="
    echo "BUILD COMPLETE"
    echo "=========================================="
    echo ""
    echo "Distribution files:"
    ls -lh dist/*.tar.gz dist/*.zip 2>/dev/null || true
    echo ""
}

main "$@"
