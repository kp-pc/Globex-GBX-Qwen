# 🌐 Globex (GBX) Cryptocurrency

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)

**A beginner-friendly cryptocurrency with a beautiful web dashboard!**

[Quick Start](#-quick-start) • [Features](#-features) • [Dashboard](#-web-dashboard) • [CLI Commands](#-cli-commands)

</div>

---

## 🎯 What is Globex?

Globex (GBX) is a **fully functional cryptocurrency** built in Python that demonstrates blockchain technology in action. Whether you're learning about cryptocurrencies or want to experiment with your own digital currency, Globex makes it **easy and fun**!

### ✨ Why Choose Globex?

- 🚀 **Zero Configuration** - Get started in seconds
- 🎨 **Beautiful Dashboard** - No command line needed!
- 📚 **Educational** - Clean, well-documented code
- 🔧 **Feature-Rich** - Mining, wallets, transactions, staking
- 💻 **Cross-Platform** - Works on Linux, macOS, and Windows

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
# Go to: http://localhost:5000
```

That's it! You'll see a colorful dashboard where you can:
- ✨ Create a wallet with one click
- ⛏️ Mine blocks and earn GBX
- 💸 Send transactions to friends
- 📊 View the blockchain in real-time

### Option 2: Command Line Interface

Prefer the terminal? Use our powerful CLI:

```bash
# Install dependencies
pip install ecdsa

# Create a wallet
python cli.py create-wallet

# Mine some coins
python cli.py mine --count 5

# Check your balance
python cli.py balance --address YOUR_ADDRESS

# Send GBX to a friend
python cli.py send --from wallet.json --to FRIEND_ADDRESS --amount 10
```

---

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
| ⛏️ **Proof of Work** | CPU-friendly mining with adjustable difficulty |
| 💰 **UTXO System** | Secure transaction model like Bitcoin |
| 👛 **ECDSA Wallets** | Industry-standard cryptographic security |
| 📦 **Mempool** | Pending transaction management |
| ✅ **Validation** | Full blockchain integrity verification |
| 🎯 **Dev Fund** | Built-in development funding mechanism |

### Advanced Features

| Feature | Description |
|---------|-------------|
| ⚡ **Proof of Stake** | Energy-efficient consensus option |
| 🔒 **Finality Checkpoints** | Prevent chain reorganizations |
| 🌐 **P2P Network** | Decentralized node communication |
| 📊 **REST API** | HTTP endpoints for integration |
| 🔐 **Encrypted Wallets** | Password-protected wallet files |

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

### Staking Commands

```bash
# Register as validator
python cli.py stake --address ADDRESS --amount 1000

# View checkpoints
python cli.py checkpoint
```

### Development Fund

```bash
# Check dev fund status
python cli.py devfund status

# Propose transaction
python cli.py devfund propose --amount 100 --recipients ADDR1 ADDR2
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
├── cli.py           # Command-line interface
├── dashboard.py     # Web dashboard (NEW!)
├── core.py          # Blockchain core logic
├── wallet.py        # Wallet management
├── miner.py         # Mining implementation
├── node.py          # P2P networking
├── utils.py         # Utility functions
├── config.py        # Configuration settings
└── README.md        # This file
```

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

- Inspired by Bitcoin and other cryptocurrencies
- Built with ❤️ using Python
- Made for educational purposes

---

<div align="center">

**Ready to start?** Run `python dashboard.py` and open http://localhost:5000!

Made with 🌟 by the Globex Team

</div>
