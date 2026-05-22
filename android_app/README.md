# Globex Android Wallet App

A native Android wallet application for the Globex (GBX) cryptocurrency, built with Kotlin and modern Android architecture components.

## 📱 Features

- **Wallet Management**: Create and manage ECDSA wallets with secure storage
- **Mining Dashboard**: Mine GBX directly from your mobile device
- **Transactions**: Send and receive GBX with fee customization
- **Blockchain Explorer**: View chain height, blocks, and pending transactions
- **Validation**: Verify blockchain integrity on-device
- **Staking**: Register as a PoS validator and earn rewards
- **Development Fund**: View and participate in governance proposals

## 🏗️ Architecture

The app follows the **Repository Pattern** with clean separation of concerns:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   UI Layer      │────▶│  Repository      │────▶│   API Layer     │
│  (Activity)     │     │  (GlobexRepo)    │     │  (Retrofit)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                        ┌──────▼──────┐
                        │ Local Cache │
                        │(Encrypted)  │
                        └─────────────┘
```

### Package Structure

```
com.globex.wallet/
├── api/
│   ├── GlobexApi.kt          # Retrofit API interface
│   └── RetrofitClient.kt     # Singleton Retrofit builder
├── model/
│   └── Models.kt             # Data classes for API responses
├── repository/
│   └── GlobexRepository.kt   # Data operations & caching
├── GlobexApplication.kt      # Application class (DI)
└── MainActivity.kt           # Main UI activity
```

## 🔧 Dependencies

- **Retrofit 2.9.0** - REST API client
- **OkHttp 4.12.0** - HTTP client with logging
- **Gson Converter** - JSON serialization
- **Kotlin Coroutines** - Async operations
- **AndroidX Security Crypto** - Encrypted storage
- **Material Components** - Modern UI components

## 🚀 Setup Instructions

### Prerequisites

1. Android Studio Hedgehog or later
2. JDK 17+
3. Android SDK 34 (API level)
4. Running Globex node (local or remote)

### Installation Steps

1. **Clone the repository**
   ```bash
   cd android_app
   ```

2. **Sync Gradle dependencies**
   - Open in Android Studio
   - Let Gradle sync automatically

3. **Configure API endpoint**
   
   Edit `api/RetrofitClient.kt`:
   ```kotlin
   // For Android Emulator (localhost)
   private var baseUrl: String = "http://10.0.2.2:5001/"
   
   // For physical device (replace with your PC IP)
   private var baseUrl: String = "http://192.168.1.100:5001/"
   ```

4. **Start the Globex node**
   ```bash
   python dashboard.py --port 5001
   ```

5. **Run the app**
   - Connect device/emulator
   - Click Run in Android Studio

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/create-wallet` | POST | Generate new ECDSA wallet |
| `/api/balance/{address}` | GET | Get balance for address |
| `/api/mine` | POST | Mine a new block |
| `/api/send` | POST | Submit transaction |
| `/api/info` | GET | Get blockchain info |
| `/api/chain` | GET | Get full blockchain |
| `/api/validate` | POST | Validate blockchain |
| `/api/nodes` | GET | List connected nodes |
| `/api/stake` | POST | Register as validator |
| `/api/devfund/status` | GET | Development fund status |

## 🔒 Security Features

1. **Encrypted Storage**: Wallet addresses stored using AndroidX Security Crypto (AES-256-GCM)
2. **Master Key**: Hardware-backed keystore for key generation
3. **No Private Key Export**: Private keys never leave the wallet file
4. **HTTPS Support**: Production mode enforces encrypted connections
5. **Certificate Pinning**: Optional certificate pinning for production

## 🎨 UI Components

- **Material Design 3** components
- **Responsive layouts** for phones and tablets
- **Dark mode** support (auto-switching)
- **Loading states** with progress indicators
- **Toast notifications** for user feedback
- **Card-based** information display

## 🧪 Testing

### Unit Tests
```bash
./gradlew test
```

### Instrumented Tests
```bash
./gradlew connectedAndroidTest
```

### Manual Testing Checklist

- [ ] Create wallet successfully
- [ ] View wallet address and balance
- [ ] Mine a block and see reward
- [ ] Send transaction to another address
- [ ] Validate blockchain integrity
- [ ] Refresh blockchain info
- [ ] Handle network errors gracefully

## 🌐 Network Configuration

### Development (Emulator)
```kotlin
baseUrl = "http://10.0.2.2:5001/"
```

### Development (Physical Device)
```kotlin
baseUrl = "http://192.168.1.XXX:5001/"
```

### Production
```kotlin
baseUrl = "https://api.globex.network/"
```

### Testnet
```kotlin
baseUrl = "https://testnet.globex.network/"
```

## 📦 Building Release APK

```bash
./gradlew assembleRelease
```

The APK will be generated at:
`app/build/outputs/apk/release/app-release.apk`

## 🐛 Troubleshooting

### Connection Refused
- Ensure Globex node is running
- Check firewall settings
- Verify correct IP address for your setup

### Cleartext Traffic Error
- Add `android:usesCleartextTraffic="true"` to manifest (dev only)
- Use HTTPS for production

### Wallet Not Saving
- Check storage permissions
- Verify Android Keystore is available

## 📄 License

MIT License - See main project LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

**Built with ❤️ for the Globex Community**
