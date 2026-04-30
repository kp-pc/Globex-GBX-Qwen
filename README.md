# 🌐 Globex (GBX) Cryptocurrency

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Android-lightgrey.svg)

**A production-ready cryptocurrency with hybrid PoW/PoS consensus, mobile apps, and enterprise features!**

[Quick Start](#-quick-start) • [Latest Features](#-latest-features) • [Features](#-features) • [Dashboard](#-web-dashboard) • [CLI Commands](#-cli-commands)

</div>

---

## 🎯 What is Globex?

Globex (GBX) is a **production-grade cryptocurrency** built in Python that demonstrates advanced blockchain technology including hybrid Proof-of-Work/Proof-of-Stake consensus, finality checkpoints, development fund management, and cross-platform applications. Whether you're learning about cryptocurrencies, building educational projects, or prototyping blockchain solutions, Globex provides **enterprise-level features with beginner-friendly accessibility**!

### ✨ Why Choose Globex?

- 🚀 **Zero Configuration** - Get started in seconds
- 🎨 **Multi-Platform Apps** - Web dashboard, Windows .exe, Android APK
- 📚 **Educational** - Clean, well-documented code (3,362 lines)
- 🔧 **Enterprise Features** - Hybrid PoW/PoS, multi-sig dev fund, finality checkpoints
- 💻 **Cross-Platform** - Works on Linux, macOS, Windows, and Android
- ⚡ **ARM-Optimized** - CPU-friendly mining for Raspberry Pi and mobile devices

---

## 🆕 Latest Features

### New in Globex v2.0

| Feature | Description | Status |
|---------|-------------|--------|
| 🔗 **Finality Checkpoints** | Prevent chain reorganizations with validator-signed checkpoints every 50 blocks | ✅ Implemented |
| 💼 **Multi-Sig Dev Fund** | 2.1M GBX development fund with vesting schedule and 2-of-N multi-signature security | ✅ Implemented |
| ⚡ **Hybrid PoW/PoS** | Energy-efficient Proof-of-Stake option alongside traditional CPU mining | ✅ Implemented |
| 📱 **Android App** | Native mobile wallet with mining, transactions, and real-time stats | ✅ Implemented |
| 🖥️ **Windows .exe** | Standalone desktop application (~30MB) - no Python required | ✅ Implemented |
| 🎨 **Web Dashboard** | Beautiful Flask-based interface with one-click operations | ✅ Implemented |
| 🔄 **Difficulty Adjustment** | ARM-friendly adaptive difficulty targeting 60-second block times | ✅ Implemented |
| 🛡️ **Validator Slashing** | 10% stake slashing for malicious validator behavior | ✅ Implemented |

---

## 🚀 Quick Start

### Option 1: Web Dashboard (Recommended for Beginners!)

The easiest way to use Globex is through our beautiful web interface:

```bash
# 1. Install dependencies
pip install flask ecdsa

# 2. Launch the dashboard
python dashboard.py

# 3. Open your browser
# Go to: http://localhost:5001
```

That's it! You'll see a colorful dashboard where you can:
- ✨ Create a wallet with one click
- ⛏️ Mine blocks and earn GBX
- 💸 Send transactions
- 📊 View blockchain stats

### Option 2: Windows Desktop App (.exe)

Want a native Windows application?

```bash
# 1. Install build tools
pip install pyinstaller flask ecdsa

# 2. Build the executable
python build_windows.py

# 3. Run the app
# Double-click: dist/GlobexWallet.exe
```

A standalone Windows app will be created that launches the dashboard automatically!

### Option 3: Android Mobile App

Take Globex on the go with our Android app:

```bash
# 1. Open android_app/ folder in Android Studio
# 2. Sync Gradle dependencies
# 3. Build APK: ./gradlew assembleDebug
# 4. Install on your device
```

See [APPS_README.md](APPS_README.md) for detailed instructions.

### Option 4: Command Line Interface

For advanced users who prefer the terminal:

```bash
# Install dependencies
pip install ecdsa flask

# Run CLI commands
python cli.py --help
python cli.py info
python cli.py mine
python cli.py stake --address YOUR_ADDRESS --amount 1000
python cli.py devfund status
```


## 🖥️ Desktop & Mobile Apps

### Windows Desktop App (.exe)
Get a native Windows application that runs the dashboard automatically!

```bash
# Build the executable
pip install pyinstaller flask ecdsa
python build_windows.py

# Run: Double-click dist/GlobexWallet.exe
```

**Features:**
- ✅ One-click installation
- ✅ No Python required for end users
- ✅ Auto-launches in browser
- ✅ Standalone ~30MB executable

### Android Mobile App
Take Globex on the go with our native Android app!

```bash
# Open android_app/ in Android Studio
# Build: ./gradlew assembleDebug
# Install APK on your device
```

**Features:**
- 📱 Touch-optimized interface
- ⛏️ Mobile mining
- 💸 Send/receive on the go
- 📊 Real-time stats

📖 **Full documentation:** See [APPS_README.md](APPS_README.md)

## 🎨 Web Dashboard

Our stunning web dashboard makes cryptocurrency management a breeze!

### Dashboard Features:

| Feature | Description |
|---------|-------------|
| 👛 **Wallet Management** | Create and manage wallets with one click |
| ⛏️ **One-Click Mining** | Mine blocks without complex commands |
| 💸 **Easy Transfers** | Send GBX with a simple form |
| 📊 **Live Stats** | Real-time blockchain statistics |
| ✅ **Chain Validation** | Verify blockchain integrity instantly |
| 🔄 **Reset Demo** | Start fresh anytime |

### Dashboard Preview:

```
╔═══════════════════════════════════════════════════╗
║           🌐 GLOBEX DASHBOARD                     ║
║     Your friendly crypto interface                ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  ┌──────────────┐  ┌──────────────┐              ║
║  │ 📊 Network   │  │ 👛 Wallet    │              ║
║  │              │  │              │              ║
║  │   6 Blocks   │  │  100.0 GBX   │              ║
║  │   0 Pending  │  │ LXeU9EPL...  │              ║
║  │              │  │              │              ║
║  └──────────────┘  └──────────────┘              ║
║                                                   ║
║  ⚡ Quick Actions                                 ║
║  [⛏️ Mine]  [✓ Validate]  [🗑️ Reset]            ║
║                                                   ║
║  💸 Send GBX                                     ║
║  To: [_____________________________]             ║
║  Amount: [________] GBX                          ║
║  Fee: [0.001] GBX                                ║
║  [Send Transaction]                              ║
║                                                   ║
║  🔗 Recent Blocks                                ║
║  Block #6 | 1 tx | Reward: 50 GBX               ║
║  Block #5 | 0 tx | Reward: 50 GBX               ║
║  Block #4 | 1 tx | Reward: 50 GBX               ║
╚═══════════════════════════════════════════════════╝
```

---

## 🎁 Features

### Core Features

| Feature | Description |
|---------|-------------|
| ⛏️ **Proof of Work** | ARM-optimized CPU mining with adaptive difficulty (targets 60s blocks) |
| 💰 **UTXO System** | Secure transaction model like Bitcoin with full validation |
| 👛 **ECDSA Wallets** | Industry-standard secp256k1 cryptographic security |
| 📦 **Mempool** | Smart pending transaction management with fee prioritization |
| ✅ **Validation** | Full blockchain integrity verification with Merkle proofs |
| 🔄 **Difficulty Adjustment** | Automatic adjustment every 10 blocks based on network hashrate |

### Advanced Features

| Feature | Description |
|---------|-------------|
| ⚡ **Hybrid PoS** | Energy-efficient Proof-of-Stake with weighted validator selection |
| 🔗 **Finality Checkpoints** | Validator-signed checkpoints every 50 blocks prevent reorgs |
| 💼 **Multi-Sig Dev Fund** | 2.1M GBX fund with vesting (1 year) and 2-of-N signature requirement |
| 🛡️ **Validator Slashing** | 10% stake penalty for malicious validator behavior |
| 🌐 **REST API** | Full HTTP endpoints for wallet, mining, transactions, and staking |
| 🔐 **Encrypted Wallets** | Optional password protection for wallet private keys |
| 📊 **Real-time Stats** | Hashrate monitoring, block rewards, and network statistics |

---

## 📋 CLI Commands

### Wallet Commands

```bash
# Create a new wallet
python cli.py create-wallet -o my_wallet.json

# Create encrypted wallet
python cli.py create-wallet -o secure.json -p mypassword
```

### Mining Commands

```bash
# Mine 5 blocks
python cli.py mine --count 5

# Mine continuously
python cli.py mine --continuous

# Mine to specific address
python cli.py mine --address LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
```

### Transaction Commands

```bash
# Send GBX
python cli.py send --from wallet.json --to ADDRESS --amount 10 --fee 0.001

# Check balance
python cli.py balance --address LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM

# View pending transactions
python cli.py list-tx
```

### Network Commands

```bash
# Start a node
python cli.py start-node --port 5000

# Validate blockchain
python cli.py validate

# Show blockchain info
python cli.py info
```

### Staking & Validator Commands

```bash
# Register as validator (minimum 1000 GBX)
python cli.py stake --address ADDRESS --amount 1000

# Mine a Proof-of-Stake block
python cli.py mine --pos --address VALIDATOR_ADDRESS

# View all active validators
python cli.py stake --list

# View finality checkpoints
python cli.py checkpoint
```

### Development Fund Commands

```bash
# Check dev fund status and vesting progress
python cli.py devfund status

# Propose a dev fund transaction (requires multi-sig)
python cli.py devfund propose --amount 100 --recipients ADDR1 ADDR2

# Sign a dev fund proposal (signers only)
python cli.py devfund sign --tx-id TX_ID

# Execute a fully-signed proposal
python cli.py devfund execute --tx-id TX_ID
```

---

## 🏗️ How It Works

### Blockchain Architecture

```
┌─────────────────────────────────────────────────┐
│                 GLOBEX BLOCKCHAIN               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│  │ Block 0 │───▶│ Block 1 │───▶│ Block 2 │───▶│
│  │ Genesis │    │  PoW    │    │  PoW    │    │
│  └─────────┘    └─────────┘    └─────────┘    │
│       │              │              │          │
│       ▼              ▼              ▼          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│  │  Hash   │    │  Hash   │    │  Hash   │    │
│  │ Tx Root │    │ Tx Root │    │ Tx Root │    │
│  │  Nonce  │    │  Nonce  │    │  Nonce  │    │
│  └─────────┘    └─────────┘    └─────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Transaction Flow

```
User Creates Wallet
        │
        ▼
   Mine Blocks (Earn GBX)
        │
        ▼
   Send Transaction
        │
        ▼
   Add to Mempool
        │
        ▼
   Miner Includes in Block
        │
        ▼
   Transaction Confirmed! ✅
```

---

## 💡 Example Session

### Complete Workflow

```bash
# Step 1: Create your wallet
$ python cli.py create-wallet -o my_wallet.json

==================================================
NEW WALLET CREATED
==================================================
Address: LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
Public Key: 04a1b2c3d4e5f6...
Private Key: 7f8e9d0c1b2a3...
==================================================
⚠️  IMPORTANT: Save your private key securely!

# Step 2: Mine some coins
$ python cli.py mine --count 3

Mining to: LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
Threads: 2

Mining block 1/3...
Block found!
  Index: 4
  Hash: 0000abc123...
  Reward: 50.0000 GBX

Mining block 2/3...
Block found!
  Index: 5
  Hash: 0000def456...
  Reward: 50.0000 GBX

Mining block 3/3...
Block found!
  Index: 6
  Hash: 0000ghi789...
  Reward: 50.0000 GBX

Chain length: 7

# Step 3: Check your balance
$ python cli.py balance --address LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM

========================================
BALANCE
========================================
Address: LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
Balance: 150.00000000 GBX
========================================

# Step 4: Send to a friend
$ python cli.py send --from my_wallet.json --to LYz8KpQr3StUvWx... --amount 25

Sending 25.0 GBX
From: LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
To: LYz8KpQr3StUvWx...
Fee: 0.001 GBX

✓ Transaction created successfully!
  TX ID: a1b2c3d4e5f6...
  Status: Pending

# Step 5: Mine to confirm transaction
$ python cli.py mine --count 1

Block found! Transaction confirmed! ✅

# Step 6: View blockchain info
$ python cli.py info

==================================================
GLOBEX BLOCKCHAIN INFO
==================================================
Network: Globex (GBX)
Chain Length: 8
Mempool Size: 0

Latest Block:
  Index: 8
  Hash: 0000jkl012...
  Timestamp: 2024-01-15 10:30:45
  Transactions: 1
  Block Reward: 50.0000 GBX
==================================================
```

---

## 🛠️ Installation & Setup

### Requirements

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
# For CLI only
pip install ecdsa

# For web dashboard
pip install ecdsa flask
```

### Verify Installation

```bash
python cli.py --help
```

You should see all available commands listed!

---

## 📁 Project Structure

```
globex/
├── cli.py              # Command-line interface (526 lines)
├── dashboard.py        # Flask web dashboard with REST API (458 lines)
├── core.py             # Blockchain core: PoW/PoS, checkpoints, dev fund (1059 lines)
├── wallet.py           # ECDSA wallet generation and management (144 lines)
├── miner.py            # Multi-threaded CPU miner with hashrate stats (321 lines)
├── node.py             # P2P networking and REST API server (528 lines)
├── utils.py            # Cryptographic utilities: SHA-256, Merkle trees (212 lines)
├── config.py           # Network and consensus configuration (49 lines)
├── build_windows.py    # PyInstaller script for Windows .exe (42 lines)
├── windows_app.py      # Windows desktop app wrapper (23 lines)
├── android_app/        # Native Android Kotlin app (see android_app/README.md)
└── README.md           # This documentation file
```

**Total Codebase:** 3,362 lines of well-documented Python + Kotlin

---

## 🎓 Learning Resources

### Understanding the Code

1. **`core.py`** - Start here! Contains the main Blockchain class
2. **`wallet.py`** - Learn about ECDSA cryptography
3. **`miner.py`** - Understand Proof of Work
4. **`cli.py`** - See how all components connect

### Key Concepts

- **Blocks**: Contain transactions, timestamp, previous hash, nonce
- **Hash**: SHA-256 fingerprint of block data
- **Nonce**: Number miners change to find valid hash
- **Difficulty**: Target hash must be below this value
- **UTXO**: Unspent Transaction Outputs track ownership

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Inspired by Bitcoin, Ethereum, and other cryptocurrencies
- Built with ❤️ using Python and Kotlin
- Made for educational purposes and blockchain prototyping
- Special thanks to the open-source cryptography community

---

<div align="center">

**Ready to start?** Run `python dashboard.py` and open http://localhost:5001!

### Quick Links

[Web Dashboard](#-quick-start) • [Android App](android_app/README.md) • [CLI Reference](#-cli-commands) • [API Docs](#-rest-api)

Made with 🌟 by the Globex Team

</div>

---

## 🚀 Future Roadmap & Strategic Architecture

Our vision is to combine the **uncompromising security of Bitcoin** with the **high-throughput performance of Polygon**.

### 🏗 Strategic Architecture Goals

| Goal | Implementation Strategy | Target Metric |
| :--- | :--- | :--- |
| **Bitcoin-Level Security** | Pure PoW base layer with Nakamoto Consensus + ASIC-resistant algo | >51% Decentralization |
| **Instant Finality** | Hybrid PoS checkpointing every 10s on top of PoW blocks | <2s Finality Time |
| **Polygon-Level Speed** | Parallel transaction execution engine & State pruning | 2,000+ TPS |
| **Infinite Scaling** | Native ZK-Rollup support for L2 execution | 100,000+ TPS (L2) |
| **Lightweight Nodes** | SPV support & Merkle proof verification for mobile | <50MB Sync Size |

Based on this architecture and industry trends, here are suggested future updates:

### Phase 1: Near-Term Enhancements (Q1-Q2 2025)

| Feature | Description | Priority | Estimated Effort |
|---------|-------------|----------|------------------|
| 🔐 **Hardware Wallet Support** | Integration with Ledger/Trezor for enhanced security | High | 2-3 weeks |
| 🌐 **P2P Network Layer** | Full decentralized node discovery using Kademlia DHT | Critical | 3-4 weeks |
| 📊 **Advanced Analytics Dashboard** | Real-time charts, network hashrate graphs, validator performance metrics | Medium | 1-2 weeks |
| 🤖 **Smart Contract Lite** | Basic scripting language for simple automated transactions | Medium | 4-6 weeks |
| 📱 **iOS Mobile App** | Native iOS wallet with mining and staking capabilities | High | 3-4 weeks |
| ⚡ **Dynamic Difficulty Adjustment** | Advanced DAA to stabilize block times against hash rate volatility | Critical | 2 weeks |

### Phase 2: Mid-Term Development (Q3-Q4 2025)

| Feature | Description | Priority | Estimated Effort |
|---------|-------------|----------|------------------|
| ⚡ **Layer 2 Scaling** | Payment channels and ZK-Rollups for instant, low-fee microtransactions | Critical | 6-8 weeks |
| 🌉 **Cross-Chain Bridge** | Atomic swaps with Bitcoin, Ethereum, and other major chains | High | 8-10 weeks |
| 🏛️ **DAO Governance** | Community-driven protocol upgrades and treasury management | Medium | 4-6 weeks |
| 🎯 **Mining Pool Protocol** | Collaborative mining with fair reward distribution | High | 3-4 weeks |
| 🔒 **Privacy Features** | Optional zk-SNARKs for confidential transactions | Medium | 6-8 weeks |
| ⚙️ **Parallel Execution Engine** | Multi-threaded transaction processing for higher throughput | Critical | 6-8 weeks |

### Phase 3: Long-Term Vision (2026+)

| Feature | Description | Priority | Estimated Effort |
|---------|-------------|----------|------------------|
| 🌍 **Global CDN Nodes** | Geographically distributed nodes for ultra-low latency | Medium | Ongoing |
| 🏢 **Enterprise SDK** | Business integration tools for payments and supply chain | High | 6-8 weeks |
| 🎮 **Gaming Integration** | In-game currency APIs and play-to-earn mechanics | Medium | 4-6 weeks |
| 📈 **DeFi Ecosystem** | Decentralized exchange, lending, and yield farming protocols | High | 12-16 weeks |
| 🌐 **EVM Compatibility** | Run Ethereum smart contracts natively on GBX | High | 8-10 weeks |
| 🔮 **Quantum Resistance** | Post-quantum cryptographic signature schemes | Low | 12+ weeks |

### Suggested Implementation Order

1. **P2P Network Layer** - Essential for true decentralization (Bitcoin-level security foundation)
2. **Dynamic Difficulty Adjustment** - Stabilize network against attacks
3. **Hardware Wallet Support** - Critical for enterprise adoption and security
4. **Parallel Execution Engine** - Key to achieving Polygon-level speed
5. **Layer 2 Scaling (ZK-Rollups)** - Enables mass adoption through lower fees and higher TPS
6. **Cross-Chain Bridge** - Expands ecosystem interoperability
7. **DAO Governance** - Empowers community ownership

### Technical Debt & Optimization Targets

| Area | Current State | Target State | Priority |
|------|---------------|--------------|----------|
| **Consensus** | Basic PoW | Hybrid PoW/PoS with Finality Gadget | 🔴 Critical |
| **Networking** | Simple TCP | Libp2p + DHT + Encryption | 🔴 Critical |
| **Database** | File-based JSON | LevelDB/RocksDB with State Pruning | 🟡 High |
| **VM** | Single-threaded Interpreter | Parallelized Wasm/EVM | 🟡 High |
| **API Security** | Basic authentication | OAuth2 + JWT tokens + Rate Limiting | 🟡 High |
| **Testing** | Manual testing | 90%+ unit test coverage + CI/CD | 🟢 Medium |
| **Monitoring** | Basic stats | Prometheus + Grafana dashboards | 🟢 Medium |
| **Documentation** | Good README | Complete API docs + tutorials + Video guides | 🟢 Medium |

### Key Metrics to Track Progress

| Metric | Current | Target (Bitcoin Standard) | Target (Polygon Speed) |
|--------|---------|---------------------------|------------------------|
| **Decentralization (Nakamoto Coefficient)** | ~5 | >20 | N/A |
| **Transaction Finality** | ~60s | ~600s (10 blocks) | <2s |
| **Throughput (TPS)** | ~15 | ~7 TPS | 2,000+ TPS |
| **Block Time** | 60s | 600s | 2s |
| **Node Storage Requirement** | Growing | ~500GB (full) | <50GB (pruned) |
| **Energy Efficiency** | Moderate | High (PoW) | Very High (PoS/L2) |

### Community Contributions Welcome!

We're looking for contributors in these areas:
- 🐛 Bug fixes and performance optimizations
- 📚 Documentation improvements and translations
- 🧪 Test suite expansion
- 🎨 UI/UX enhancements for dashboard and mobile apps
- 🔬 Research on consensus mechanisms and cryptography

Join us in building the future of Globex! 🚀
