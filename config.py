"""
Globex (GBX) Configuration
Lightweight cryptocurrency optimized for CPU/ARM devices
Enhanced for Bitcoin-level security and Polygon-level speed
"""

# Network settings
NETWORK_NAME = "Globex"
SYMBOL = "GBX"
P2P_PORT = 5000
API_PORT = 5001
P2P_BOOTSTRAP_NODES = [
    "node1.globex.network:5000",
    "node2.globex.network:5000",
    "node3.globex.network:5000"
]

# Consensus settings - Hybrid PoW/PoS
BLOCK_TIME_TARGET = 60  # seconds (can be reduced to 2s with optimizations)
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # blocks
INITIAL_DIFFICULTY = 4  # ARM-friendly starting difficulty
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 32
DYNAMIC_DIFFICULTY_ENABLED = True  # Bitcoin-style dynamic adjustment

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
INSTANT_FINALITY_THRESHOLD = 2  # seconds for instant finality with PoS

# Parallel Execution Settings
PARALLEL_EXECUTION_ENABLED = True
MAX_PARALLEL_TX_BATCH = 100  # Max transactions per parallel batch
EXECUTION_SHARDS = 4  # Number of parallel execution shards

# ZK-Rollup Settings
ZK_ROLLUP_ENABLED = True
ROLLUP_BATCH_SIZE = 1000  # Transactions per rollup batch
ROLLUP_SUBMISSION_INTERVAL = 300  # seconds between rollup submissions

# SPV (Simplified Payment Verification) Settings
SPV_ENABLED = True
SPV_MERKLE_PROOF_CACHE = 1000  # Cache size for merkle proofs
LIGHT_NODE_SUPPORT = True

# Quantum Resistance Settings
QUANTUM_RESISTANCE_ENABLED = True
POST_QUANTUM_ALGORITHM = "CRYSTALS-Kyber"  # NIST-approved PQC algorithm
HYBRID_SIGNATURES = True  # Use both ECDSA and PQC during transition

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
MAX_TRANSACTIONS_PER_BLOCK = 500  # Increase for higher TPS

# Database settings
DB_PATH = "globex.db"

# Mining settings
MINER_THREADS = 2
MINER_NONCE_BATCH_SIZE = 10000

# Performance targets
TARGET_TPS = 2000  # Target transactions per second (Polygon-level)
LAYER2_TPS_TARGET = 100000  # ZK-Rollup target TPS
