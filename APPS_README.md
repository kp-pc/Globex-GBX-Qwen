# Globex Desktop & Mobile Applications

Complete cross-platform wallet and mining applications for the Globex (GBX) cryptocurrency.

## 🖥️ Windows Desktop App

### Features
- One-click executable (.exe)
- Beautiful web-based dashboard
- No command-line required
- Auto-launches in browser

### Build Instructions

#### Prerequisites
```bash
pip install pyinstaller flask ecdsa
```

#### Build the EXE
```bash
python build_windows.py
```

This will create `dist/GlobexWallet.exe` - a standalone executable that includes:
- Python runtime
- Flask web server
- Dashboard interface
- All dependencies

#### Usage
1. Double-click `GlobexWallet.exe`
2. Your default browser opens automatically to the dashboard
3. Start mining, creating wallets, and sending transactions!

### Files
- `windows_app.py` - Windows entry point
- `build_windows.py` - PyInstaller build script
- `dashboard.py` - Web interface (included in build)

---

## 📱 Android Mobile App

### Features
- Native Kotlin application
- Material Design UI
- Real-time blockchain stats
- Touch-optimized mining
- Send/receive GBX on the go

### Project Structure
```
android_app/
├── app/src/main/
│   ├── java/com/globex/wallet/
│   │   └── MainActivity.kt      # App logic
│   ├── res/
│   │   ├── layout/
│   │   │   └── activity_main.xml
│   │   └── values/
│   │       ├── strings.xml
│   │       └── themes.xml
│   └── AndroidManifest.xml
├── build.gradle
└── README.md
```

### Build Instructions

#### 1. Open in Android Studio
```
File → Open → Select android_app folder
```

#### 2. Sync Gradle
Wait for automatic dependency download.

#### 3. Run Backend
Start the Python dashboard:
```bash
python dashboard.py
```

#### 4. Build APK
```bash
cd android_app
./gradlew assembleDebug
```

APK location: `app/build/outputs/apk/debug/app-debug.apk`

### Installation

#### Emulator
- Automatically deploys from Android Studio
- Uses `10.0.2.2` to connect to localhost backend

#### Physical Device
1. Enable USB Debugging on phone
2. Connect via USB
3. Install APK:
   ```bash
   adb install app/build/outputs/apk/debug/app-debug.apk
   ```
4. Update `BASE_URL` in `MainActivity.kt` to your computer's IP

### Requirements
- Android 7.0+ (API 24)
- Internet permission (for backend connection)
- Same WiFi network as backend (for physical devices)

---

## 🔗 Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Windows .exe   │         │  Android App     │
│  or Dashboard   │         │  (Kotlin)        │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │    HTTP REST API          │
         │    (Port 5001)            │
         └───────────┬───────────────┘
                     │
         ┌───────────▼───────────────┐
         │   Python Backend          │
         │   (dashboard.py)          │
         │                           │
         │   - Wallet Management     │
         │   - Mining Engine         │
         │   - Transaction Pool      │
         │   - Blockchain Storage    │
         └───────────────────────────┘
```

---

## 🚀 Quick Start Guide

### For Windows Users
1. **Build**: `python build_windows.py`
2. **Run**: Double-click `dist/GlobexWallet.exe`
3. **Mine**: Click "Mine Block" in the browser
4. **Earn**: Get 50 GBX per block!

### For Android Users
1. **Start Backend**: `python dashboard.py` on your computer
2. **Build APK**: `./gradlew assembleDebug`
3. **Install**: Transfer APK to phone or use ADB
4. **Connect**: Ensure same WiFi network
5. **Mine**: Tap "Mine Block" on your phone!

---

## 📊 Comparison

| Feature | Windows App | Android App | Web Dashboard |
|---------|-------------|-------------|---------------|
| Platform | Windows 10/11 | Android 7.0+ | Any Browser |
| Language | Python/JS | Kotlin | HTML/CSS/JS |
| Build Tool | PyInstaller | Gradle | None |
| Distribution | .exe file | .apk file | URL |
| Mining | ✅ | ✅ | ✅ |
| Wallet | ✅ | ✅ | ✅ |
| Send TX | ✅ | ✅ | ✅ |
| Offline | ❌ | ❌ | ❌ |

---

## 🛠️ Development

### Adding New Features

1. **Backend (Python)**: Add new routes in `dashboard.py`
2. **Windows**: Automatically included in next build
3. **Android**: Update `MainActivity.kt` and layout XML
4. **Web**: Edit `dashboard.py` HTML template

### API Endpoints

All apps communicate via these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/info` | GET | Blockchain statistics |
| `/api/create-wallet` | POST | Generate new wallet |
| `/api/mine` | POST | Mine a new block |
| `/api/send` | POST | Send transaction |
| `/api/validate` | POST | Validate chain |
| `/api/balance` | POST | Check wallet balance |

---

## 📦 Distribution

### Windows
- Distribute `GlobexWallet.exe` directly
- Or create installer with Inno Setup
- Size: ~30MB (includes Python runtime)

### Android
- Upload APK to Google Play Store
- Or distribute via website
- Size: ~15MB

### Security Notes
- Sign Android APK with release keystore
- Code-sign Windows EXE with certificate
- Enable ProGuard for Android release builds
- Never include private keys in source code

---

## 🐛 Troubleshooting

### Windows EXE won't start
- Check Windows Defender (may flag false positive)
- Run as Administrator
- Rebuild with `--clean` flag

### Android can't connect
- Verify backend is running
- Check firewall allows port 5001
- Use correct IP address (10.0.2.2 for emulator)
- Ensure same WiFi network

### Build fails
- Clear cache: `rm -rf build/ dist/`
- Reinstall dependencies
- Update PyInstaller: `pip install --upgrade pyinstaller`

---

## 📄 License

MIT License - See main project LICENSE file.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test on all platforms
5. Submit pull request

---

**Made with ❤️ for the Globex Community**
