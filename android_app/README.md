# Globex Android App

Native Android wallet application for the Globex (GBX) cryptocurrency.

## Features

- 👛 **Wallet Management**: Create and manage GBX wallets
- ⛏️ **Mobile Mining**: Mine blocks directly from your phone
- 💸 **Send Transactions**: Transfer GBX to other users
- ✅ **Chain Validation**: Verify blockchain integrity
- 📊 **Real-time Stats**: View blockchain height, blocks, and pending transactions

## Prerequisites

- Android Studio Arctic Fox (2020.3.1) or newer
- JDK 11 or higher
- Android SDK 34
- Minimum Android version: 7.0 (API 24)

## Setup Instructions

### 1. Open in Android Studio
```bash
# Open Android Studio
# File → Open → Select the android_app folder
```

### 2. Sync Gradle
Android Studio will automatically sync the project. Wait for the sync to complete.

### 3. Configure Backend Connection

The app connects to the Globex Python backend. You have two options:

#### Option A: Run on Emulator with Local Backend
1. Start the Python dashboard on your computer:
   ```bash
   python dashboard.py
   ```
2. The emulator can access your computer's localhost via `10.0.2.2`
3. The app is already configured to use this address

#### Option B: Run on Physical Device
1. Make sure your phone and computer are on the same WiFi network
2. Find your computer's IP address:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig`
3. Update `BASE_URL` in `MainActivity.kt`:
   ```kotlin
   private val BASE_URL = "http://YOUR_IP_ADDRESS:5001"
   ```
4. Allow port 5001 through your firewall

### 4. Build and Run

#### Debug Build
```bash
./gradlew assembleDebug
```

#### Release Build (APK)
```bash
./gradlew assembleRelease
```

The APK will be generated at:
`app/build/outputs/apk/release/app-release.apk`

## Project Structure

```
android_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/globex/wallet/
│   │   │   └── MainActivity.kt          # Main app logic
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml    # UI layout
│   │   │   └── values/
│   │   │       ├── strings.xml          # String resources
│   │   │       └── themes.xml           # App theme
│   │   └── AndroidManifest.xml          # App configuration
│   ├── build.gradle                     # App dependencies
│   └── proguard-rules.pro               # ProGuard config
├── build.gradle                         # Project config
└── settings.gradle                      # Gradle settings
```

## Dependencies

- **Retrofit 2**: HTTP client for API calls
- **OkHttp 3**: Network layer
- **Gson**: JSON parsing
- **Material Design**: Modern UI components
- **Kotlin Coroutines**: Async operations
- **ViewBinding**: Type-safe view access

## Key Features Explained

### Wallet Creation
Tap "Create New Wallet" to generate a new GBX address and private key. The address is displayed on screen.

### Mining
Tap "Mine Block" to solve a proof-of-work puzzle and earn 50 GBX reward. Mining difficulty adjusts based on the blockchain.

### Sending Transactions
1. Enter recipient's GBX address
2. Enter amount to send
3. Tap "Send Transaction"
4. Transaction is broadcast to the network

### Chain Validation
Tap "Validate" to verify the entire blockchain's integrity. Checks all block hashes and proof-of-work.

## Troubleshooting

### Cannot Connect to Backend
- Ensure `dashboard.py` is running
- Check that port 5001 is not blocked by firewall
- Verify IP address is correct (use `10.0.2.2` for emulator)
- Try restarting both the app and backend

### Build Errors
- Clean project: `Build → Clean Project`
- Rebuild: `Build → Rebuild Project`
- Invalidate caches: `File → Invalidate Caches / Restart`

### App Crashes on Launch
- Check LogCat for error messages
- Ensure minimum SDK is 24 or higher
- Verify all dependencies are synced

## Building APK for Distribution

1. Generate a keystore (first time only):
   ```bash
   keytool -genkey -v -keystore globex-wallet.keystore -alias globex -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Create `keystore.properties` in project root:
   ```properties
   storePassword=your_password
   keyPassword=your_password
   keyAlias=globex
   storeFile=/path/to/globex-wallet.keystore
   ```

3. Build signed APK:
   ```bash
   ./gradlew assembleRelease
   ```

## Future Enhancements

- [ ] Biometric authentication
- [ ] QR code scanner for addresses
- [ ] Transaction history list
- [ ] Push notifications for received payments
- [ ] Dark mode support
- [ ] Multiple wallet support
- [ ] Staking interface
- [ ] Price chart integration

## License

MIT License - See main project LICENSE file.
