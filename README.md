# 🌐 Globex (GBX) - Lightweight Cryptocurrency for CPU/ARM

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-CPU%2FARM-orange.svg)

**A lightweight, educational cryptocurrency built for efficiency on any device**

*Created with Qwen Coder*

</div>

---

## 🚀 Features

- ⛏️ **Hybrid Consensus** - Proof of Work (PoW) + Proof of Stake (PoS)
- 💰 **Wallet Management** - Create wallets, check balances, send transactions
- 🔗 **Blockchain Validation** - Full chain integrity verification
- 📦 **CPU Optimized** - Runs efficiently on ARM and low-power devices
- 🛠️ **Developer Tools** - Built-in dev fund and checkpoint management
- 🌍 **P2P Ready** - Node networking capabilities

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `create-wallet` | Generate a new GBX wallet address |
| `mine` | Mine new blocks and earn rewards |
| `send` | Transfer GBX to another address |
| `balance` | Check wallet balance |
| `validate` | Verify blockchain integrity |
| `info` | Display blockchain statistics |
| `list-tx` | View pending transactions |
| `stake` | Register as a PoS validator |
| `start-node` | Launch a P2P node |
| `devfund` | Manage development fund |
| `checkpoint` | View finality checkpoints |

---

## 🛠️ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/globex-gbx.git
cd globex-gbx

# Install dependencies
pip install ecdsa
```

### Usage Examples

#### 1. Create a Wallet
```bash
python cli.py create-wallet
```
**Output:**
```
✅ New wallet created!
Address: LXeU9EPLLyNfdVtd5GgN23JFK1MFYpPZsM
```

#### 2. Mine Blocks
```bash
python cli.py mine --count 2
```
**Output:**
```
⛏️ Mined block #5 | Reward: 50 GBX
⛏️ Mined block #6 | Reward: 50 GBX
Total earned: 100 GBX
```

#### 3. Send GBX
```bash
python cli.py send --from <your_address> --to <recipient_address> --amount 10
```

#### 4. Check Balance
```bash
python cli.py balance --address <your_address>
```

#### 5. Validate Blockchain
```bash
python cli.py validate
```
**Output:**
```
✅ Blockchain is valid! Total blocks: 6
```

#### 6. Register as Validator (PoS)
```bash
python cli.py stake --address <your_address> --amount 1000
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Globex CLI                         │
├─────────────────────────────────────────────────────┤
│  Wallet  │  Miner  │  Core  │  Node  │  Utils      │
├─────────────────────────────────────────────────────┤
│                 SQLite Database                     │
│              (globex.db / demo.db)                  │
└─────────────────────────────────────────────────────┘
```

### Core Components

- **`cli.py`** - Command-line interface handler
- **`wallet.py`** - Wallet generation & management
- **`miner.py`** - PoW mining algorithm
- **`core.py`** - Blockchain core logic
- **`node.py`** - P2P networking
- **`utils.py`** - Helper functions
- **`config.py`** - Configuration settings

---

## 🔧 Advanced Usage

### Development Fund
```bash
# Check dev fund status
python cli.py devfund status

# Allocate funds
python cli.py devfund allocate --amount 1000 --purpose "development"
```

### Finality Checkpoints
```bash
python cli.py checkpoint
```

### Start a Node
```bash
python cli.py start-node --port 8545
```

---

## 📈 Blockchain Info

Run `python cli.py info` to see:
- Total blocks in chain
- Latest block hash
- Network difficulty
- Pending transactions
- Active validators

---

## 🎯 Why Globex?

- ✅ **Lightweight** - Minimal dependencies, fast execution
- ✅ **Educational** - Clean, well-documented code
- ✅ **Portable** - Works on Raspberry Pi, smartphones, servers
- ✅ **Extensible** - Easy to add new features
- ✅ **Secure** - ECDSA cryptography, chain validation

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ using **Qwen Coder**
- Inspired by Bitcoin and Ethereum architectures
- Designed for educational purposes

---

<div align="center">

**Happy Mining! ⛏️💎**

*Globex (GBX) - The people's cryptocurrency*

</div>
