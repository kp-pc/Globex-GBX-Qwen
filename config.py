"""
Globex (GBX) Configuration
Lightweight cryptocurrency optimized for CPU/ARM devices
"""

# Network settings
NETWORK_NAME = "Globex"
SYMBOL = "GBX"
P2P_PORT = 5000
API_PORT = 5001

# Consensus settings
BLOCK_TIME_TARGET = 60  # seconds
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # blocks
INITIAL_DIFFICULTY = 4  # ARM-friendly starting difficulty
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 32

# Mining rewards
INITIAL_BLOCK_REWARD = 50
HALVING_INTERVAL = 500000  # blocks
MAX_SUPPLY = 21000000  # 21M GBX

# Proof of Stake settings
POS_ENABLED = True
MIN_STAKE_AMOUNT = 1000  # Minimum GBX to become validator
STAKE_LOCKUP_PERIOD = 100  # blocks before unstaking
SLASHING_PERCENTAGE = 10  # % of stake slashed for malicious behavior
VALIDATOR_SELECTION_WINDOW = 10  # blocks for validator selection
FINALITY_CHECKPOINT_INTERVAL = 50  # blocks between finality checkpoints

# Development Fund settings
DEV_FUND_ADDRESS = None  # Will be set on first run
DEV_FUND_TOTAL = 2100000  # 10% of max supply (2.1M GBX)
DEV_FUND_VESTING_BLOCKS = 2592000  # ~6 months at 60s block time (~1 year)
DEV_FUND_MULTI_SIG_REQUIRED = 2  # Number of signatures required
DEV_FUND_SIGNERS = []  # List of signer addresses

# Transaction settings
MIN_TRANSACTION_FEE = 0.0001
MAX_TRANSACTION_SIZE = 10000  # bytes
TRANSACTION_VERSION = 1

# Database settings
DB_PATH = "globex.db"

# Mining settings
MINER_THREADS = 2
MINER_NONCE_BATCH_SIZE = 10000
