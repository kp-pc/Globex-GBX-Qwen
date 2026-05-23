"""
Globex (GBX) Core Blockchain Implementation
Block structure, Proof-of-Work, difficulty adjustment, mempool, and chain validation
"""

import json
import sqlite3
import threading
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import time

from utils import (
    sha256, double_sha256, MerkleTree, get_timestamp, 
    calculate_difficulty_adjustment, bytes_to_hex, hex_to_bytes, verify_address
)
from wallet import Wallet, address_from_public_key
from config import (
    INITIAL_DIFFICULTY, BLOCK_TIME_TARGET, DIFFICULTY_ADJUSTMENT_INTERVAL,
    INITIAL_BLOCK_REWARD, HALVING_INTERVAL, MAX_SUPPLY,
    MIN_TRANSACTION_FEE, DB_PATH, POS_ENABLED, MIN_STAKE_AMOUNT,
    STAKE_LOCKUP_PERIOD, SLASHING_PERCENTAGE, FINALITY_CHECKPOINT_INTERVAL,
    DEV_FUND_TOTAL, DEV_FUND_VESTING_BLOCKS, DEV_FUND_MULTI_SIG_REQUIRED
)


@dataclass
class Transaction:
    """Transaction structure for Globex."""
    tx_id: str = ""
    version: int = 1
    inputs: List[Dict] = field(default_factory=list)
    outputs: List[Dict] = field(default_factory=list)
    timestamp: float = 0.0
    signature: str = ""
    public_key: str = ""
    fee: float = 0.0
    tx_type: str = "transfer"  # transfer, coinbase, stake, unstake, dev_fund
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Transaction':
        return cls(**data)
    
    def serialize(self) -> bytes:
        """Serialize transaction for signing."""
        data = {
            'version': self.version,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'timestamp': self.timestamp,
            'tx_type': self.tx_type,
            'fee': self.fee
        }
        return json.dumps(data, sort_keys=True).encode()
    
    def compute_tx_id(self) -> str:
        """Compute transaction ID from serialized data."""
        return bytes_to_hex(double_sha256(self.serialize()))
    
    def validate(self) -> Tuple[bool, str]:
        """Validate transaction structure and signature."""
        if not self.inputs and self.tx_type != "coinbase":
            return False, "Transaction must have inputs"
        
        if not self.outputs:
            return False, "Transaction must have outputs"
        
        # Validate signature for non-coinbase transactions
        if self.tx_type != "coinbase" and self.signature:
            try:
                pub_key = hex_to_bytes(self.public_key)
                sig = hex_to_bytes(self.signature)
                from wallet import Wallet
                if not Wallet.verify_transaction_signature(pub_key, self.serialize(), sig):
                    return False, "Invalid signature"
            except Exception as e:
                return False, f"Signature verification failed: {str(e)}"
        
        # Validate fee
        if self.fee < 0:
            return False, "Fee cannot be negative"
        
        return True, "Valid"


@dataclass
class Block:
    """Block structure for Globex blockchain."""
    index: int = 0
    timestamp: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    prev_hash: str = ""
    nonce: int = 0
    difficulty: int = INITIAL_DIFFICULTY
    merkle_root: str = ""
    block_hash: str = ""
    validator: str = ""  # For PoS blocks
    stake_amount: float = 0.0  # For PoS validation
    checkpoint: bool = False  # Finality checkpoint flag
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['transactions'] = [tx.to_dict() for tx in self.transactions]
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Block':
        data['transactions'] = [Transaction.from_dict(tx) for tx in data.get('transactions', [])]
        return cls(**data)
    
    def compute_merkle_root(self) -> str:
        """Compute Merkle root from transactions."""
        if not self.transactions:
            return bytes_to_hex(double_sha256(b''))
        
        tx_hashes = [bytes_to_hex(double_sha256(tx.serialize())) for tx in self.transactions]
        tree = MerkleTree([h.encode() for h in tx_hashes])
        return bytes_to_hex(tree.get_root())
    
    def compute_hash(self) -> str:
        """Compute block hash from header data."""
        header = {
            'index': self.index,
            'timestamp': self.timestamp,
            'prev_hash': self.prev_hash,
            'merkle_root': self.merkle_root,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'validator': self.validator
        }
        header_data = json.dumps(header, sort_keys=True).encode()
        return bytes_to_hex(double_sha256(header_data))
    
    def hash_meets_difficulty(self, block_hash: str, difficulty: int) -> bool:
        """Check if hash meets the required difficulty (leading zeros)."""
        target = '0' * difficulty
        return block_hash.startswith(target)
    
    def serialize_header(self) -> bytes:
        """Serialize block header for hashing."""
        header = {
            'index': self.index,
            'timestamp': self.timestamp,
            'prev_hash': self.prev_hash,
            'merkle_root': self.merkle_root,
            'difficulty': self.difficulty,
            'nonce': self.nonce
        }
        return json.dumps(header, sort_keys=True).encode()


class StakeManager:
    """Manages proof-of-stake validators and staking operations."""
    
    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn
        self._init_tables()
    
    def _init_tables(self):
        """Initialize stake-related database tables."""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validators (
                address TEXT PRIMARY KEY,
                stake_amount REAL,
                locked_until_block INTEGER,
                is_active INTEGER DEFAULT 1,
                slashed_amount REAL DEFAULT 0,
                created_at REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                validator_address TEXT,
                amount REAL,
                block_height INTEGER,
                locked_until_block INTEGER,
                status TEXT DEFAULT 'active',
                created_at REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                block_height INTEGER PRIMARY KEY,
                block_hash TEXT,
                validator_signatures TEXT,
                finalized INTEGER DEFAULT 0,
                created_at REAL
            )
        ''')
        self.db.commit()
    
    def register_validator(self, address: str, stake_amount: float, lockup_blocks: int, current_block: int) -> bool:
        """Register a new validator with staked amount."""
        if stake_amount < MIN_STAKE_AMOUNT:
            return False
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO validators 
            (address, stake_amount, locked_until_block, is_active, created_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (address, stake_amount, current_block + lockup_blocks, time.time()))
        
        cursor.execute('''
            INSERT INTO stakes (validator_address, amount, block_height, locked_until_block, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (address, stake_amount, current_block, current_block + lockup_blocks, time.time()))
        
        self.db.commit()
        return True
    
    def get_validators(self) -> List[Dict]:
        """Get all active validators."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM validators WHERE is_active = 1')
        columns = ['address', 'stake_amount', 'locked_until_block', 'is_active', 'slashed_amount', 'created_at']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def select_validator(self, block_height: int) -> Optional[str]:
        """Select a validator for the next block based on stake weight."""
        validators = self.get_validators()
        if not validators:
            return None
        
        # Weighted random selection based on stake
        total_stake = sum(v['stake_amount'] for v in validators)
        if total_stake == 0:
            return None
        
        import random
        rand_val = random.uniform(0, total_stake)
        cumulative = 0
        
        for v in validators:
            cumulative += v['stake_amount']
            if rand_val <= cumulative:
                return v['address']
        
        return validators[-1]['address'] if validators else None
    
    def slash_validator(self, address: str, amount: float) -> bool:
        """Slash a validator's stake for malicious behavior."""
        cursor = self.db.cursor()
        cursor.execute('SELECT stake_amount FROM validators WHERE address = ?', (address,))
        result = cursor.fetchone()
        
        if not result:
            return False
        
        current_stake = result[0]
        slash_amount = min(amount, current_stake * (SLASHING_PERCENTAGE / 100))
        
        cursor.execute('''
            UPDATE validators 
            SET stake_amount = stake_amount - ?, slashed_amount = slashed_amount + ?
            WHERE address = ?
        ''', (slash_amount, slash_amount, address))
        
        self.db.commit()
        return True
    
    def add_checkpoint(self, block_height: int, block_hash: str, signatures: List[str]) -> bool:
        """Add a finality checkpoint."""
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO checkpoints 
            (block_height, block_hash, validator_signatures, finalized, created_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (block_height, block_hash, json.dumps(signatures), time.time()))
        self.db.commit()
        return True
    
    def is_finalized(self, block_height: int) -> bool:
        """Check if a block is finalized via checkpoint."""
        cursor = self.db.cursor()
        cursor.execute('SELECT finalized FROM checkpoints WHERE block_height = ?', (block_height,))
        result = cursor.fetchone()
        return result is not None and result[0] == 1


class DevFundManager:
    """Manages the development fund with vesting and multi-signature simulation."""
    
    def __init__(self, db_conn: sqlite3.Connection, fund_address: str):
        self.db = db_conn
        self.fund_address = fund_address
        self.signers: List[str] = []
        self._init_tables()
    
    def _init_tables(self):
        """Initialize dev fund database tables."""
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_fund (
                id INTEGER PRIMARY KEY,
                address TEXT UNIQUE,
                total_amount REAL,
                released_amount REAL DEFAULT 0,
                genesis_block INTEGER,
                vesting_blocks INTEGER,
                created_at REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_fund_signers (
                address TEXT PRIMARY KEY,
                added_at REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dev_fund_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT,
                amount REAL,
                recipients TEXT,
                signatures TEXT,
                block_height INTEGER,
                executed INTEGER DEFAULT 0,
                created_at REAL
            )
        ''')
        self.db.commit()
    
    def initialize_fund(self, total_amount: float, genesis_block: int, vesting_blocks: int) -> bool:
        """Initialize the development fund."""
        cursor = self.db.cursor()
        try:
            cursor.execute('''
                INSERT INTO dev_fund (address, total_amount, genesis_block, vesting_blocks, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.fund_address, total_amount, genesis_block, vesting_blocks, time.time()))
            self.db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def add_signer(self, address: str) -> bool:
        """Add a multi-signature signer."""
        cursor = self.db.cursor()
        cursor.execute('INSERT OR IGNORE INTO dev_fund_signers (address, added_at) VALUES (?, ?)',
                      (address, time.time()))
        self.db.commit()
        self.signers.append(address)
        return True
    
    def get_vested_amount(self, current_block: int) -> float:
        """Calculate the vested amount available at current block."""
        cursor = self.db.cursor()
        cursor.execute('SELECT total_amount, genesis_block, vesting_blocks, released_amount FROM dev_fund LIMIT 1')
        result = cursor.fetchone()
        
        if not result:
            return 0.0
        
        total, genesis, vesting, released = result
        blocks_elapsed = current_block - genesis
        
        if blocks_elapsed >= vesting:
            return total - released
        
        vested_ratio = blocks_elapsed / vesting
        total_vested = total * vested_ratio
        return max(0, total_vested - released)
    
    def propose_transaction(self, tx_id: str, amount: float, recipients: List[Dict], 
                           block_height: int) -> Dict:
        """Propose a dev fund transaction (requires multi-sig)."""
        proposal = {
            'tx_id': tx_id,
            'amount': amount,
            'recipients': recipients,
            'signatures': [],
            'block_height': block_height,
            'executed': False,
            'required_signatures': DEV_FUND_MULTI_SIG_REQUIRED
        }
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO dev_fund_transactions 
            (tx_id, amount, recipients, signatures, block_height, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tx_id, amount, json.dumps(recipients), json.dumps([]), block_height, time.time()))
        self.db.commit()
        
        return proposal
    
    def sign_transaction(self, tx_id: str, signer_address: str) -> bool:
        """Add a signature to a dev fund transaction."""
        if signer_address not in self.signers:
            return False
        
        cursor = self.db.cursor()
        cursor.execute('SELECT signatures FROM dev_fund_transactions WHERE tx_id = ?', (tx_id,))
        result = cursor.fetchone()
        
        if not result:
            return False
        
        signatures = json.loads(result[0])
        if signer_address not in signatures:
            signatures.append(signer_address)
        
        cursor.execute('''
            UPDATE dev_fund_transactions SET signatures = ? WHERE tx_id = ?
        ''', (json.dumps(signatures), tx_id))
        self.db.commit()
        return True
    
    def execute_transaction(self, tx_id: str) -> Tuple[bool, str]:
        """Execute a dev fund transaction if enough signatures collected."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT signatures, amount, executed FROM dev_fund_transactions WHERE tx_id = ?
        ''', (tx_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, "Transaction not found"
        
        signatures, amount, executed = result
        if executed:
            return False, "Transaction already executed"
        
        sig_list = json.loads(signatures)
        if len(sig_list) < DEV_FUND_MULTI_SIG_REQUIRED:
            return False, f"Need {DEV_FUND_MULTI_SIG_REQUIRED} signatures, got {len(sig_list)}"
        
        cursor.execute('''
            UPDATE dev_fund_transactions SET executed = 1 WHERE tx_id = ?
        ''', (tx_id,))
        cursor.execute('''
            UPDATE dev_fund SET released_amount = released_amount + ?
        ''', (amount,))
        self.db.commit()
        
        return True, "Transaction executed"
    
    def get_status(self, current_block: int) -> Dict:
        """Get development fund status report."""
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT total_amount, released_amount, genesis_block, vesting_blocks FROM dev_fund LIMIT 1
        ''')
        result = cursor.fetchone()
        
        if not result:
            return {'error': 'Dev fund not initialized'}
        
        total, released, genesis, vesting = result
        vested = self.get_vested_amount(current_block)
        remaining = total - released - vested
        
        return {
            'fund_address': self.fund_address,
            'total_allocation': total,
            'released': released,
            'vested_available': vested,
            'remaining_locked': remaining,
            'genesis_block': genesis,
            'vesting_duration': vesting,
            'current_block': current_block,
            'vesting_progress': f"{((current_block - genesis) / vesting * 100):.2f}%" if current_block > genesis else "0%",
            'signers': self.signers,
            'multi_sig_required': DEV_FUND_MULTI_SIG_REQUIRED
        }


class Mempool:
    """Transaction mempool for pending transactions."""
    
    def __init__(self, max_size: int = 1000):
        self.transactions: Dict[str, Transaction] = {}
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def add_transaction(self, tx: Transaction) -> Tuple[bool, str]:
        """Add a transaction to the mempool."""
        with self.lock:
            if len(self.transactions) >= self.max_size:
                return False, "Mempool full"
            
            valid, msg = tx.validate()
            if not valid:
                return False, msg
            
            if not tx.tx_id:
                tx.tx_id = tx.compute_tx_id()
            
            self.transactions[tx.tx_id] = tx
            return True, "Added to mempool"
    
    def get_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get transactions from mempool for block inclusion."""
        with self.lock:
            # Sort by fee (highest first) for miner incentive
            sorted_txs = sorted(
                self.transactions.values(),
                key=lambda t: t.fee,
                reverse=True
            )
            return sorted_txs[:limit]
    
    def remove_transactions(self, tx_ids: List[str]) -> None:
        """Remove confirmed transactions from mempool."""
        with self.lock:
            for tx_id in tx_ids:
                self.transactions.pop(tx_id, None)
    
    def size(self) -> int:
        """Get current mempool size."""
        with self.lock:
            return len(self.transactions)
    
    def clear(self) -> None:
        """Clear all transactions from mempool."""
        with self.lock:
            self.transactions.clear()


class Blockchain:
    """Main blockchain class managing chain state and operations."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.db = self._init_db()
        self.mempool = Mempool()
        self.stake_manager = StakeManager(self.db)
        
        # Initialize dev fund address
        dev_fund_wallet = Wallet()
        self.dev_fund_address = dev_fund_wallet.address
        self.dev_fund_manager = DevFundManager(self.db, self.dev_fund_address)
        
        self.chain: List[Block] = []
        self.unspent_outputs: Dict[str, List[Dict]] = {}  # address -> [outputs]
        self.lock = threading.Lock()
        
        self._load_chain()
        
        # Create genesis block if chain is empty
        if not self.chain:
            self.create_genesis_block()
        
        self._init_dev_fund()
    
    def _init_db(self) -> sqlite3.Connection:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_index INTEGER PRIMARY KEY,
                timestamp REAL,
                transactions TEXT,
                prev_hash TEXT,
                nonce INTEGER,
                difficulty INTEGER,
                merkle_root TEXT,
                block_hash TEXT UNIQUE,
                validator TEXT,
                stake_amount REAL,
                checkpoint INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utxo (
                tx_id TEXT,
                output_index INTEGER,
                address TEXT,
                amount REAL,
                spent INTEGER DEFAULT 0,
                PRIMARY KEY (tx_id, output_index)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_utxo_address ON utxo(address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_utxo_spent ON utxo(spent)')
        
        conn.commit()
        return conn
    
    def _init_dev_fund(self):
        """Initialize development fund if not already done."""
        cursor = self.db.cursor()
        cursor.execute('SELECT COUNT(*) FROM dev_fund')
        if cursor.fetchone()[0] == 0:
            genesis_block = 0 if not self.chain else self.chain[-1].index
            self.dev_fund_manager.initialize_fund(
                DEV_FUND_TOTAL,
                genesis_block,
                DEV_FUND_VESTING_BLOCKS
            )
            # Add some default signers (simulated multi-sig)
            for i in range(3):
                signer_wallet = Wallet()
                self.dev_fund_manager.add_signer(signer_wallet.address)
    
    def _load_chain(self) -> None:
        """Load blockchain from database."""
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM blocks ORDER BY block_index')
        
        for row in cursor.fetchall():
            block = Block(
                index=row[0],
                timestamp=row[1],
                transactions=json.loads(row[2]) if row[2] else [],
                prev_hash=row[3],
                nonce=row[4],
                difficulty=row[5],
                merkle_root=row[6],
                block_hash=row[7],
                validator=row[8] or "",
                stake_amount=row[9] or 0.0,
                checkpoint=bool(row[10])
            )
            # Convert dict transactions back to Transaction objects
            block.transactions = [
                Transaction.from_dict(tx) if isinstance(tx, dict) else tx 
                for tx in block.transactions
            ]
            self.chain.append(block)
        
        self._rebuild_utxo()
    
    def _rebuild_utxo(self) -> None:
        """Rebuild UTXO set from blockchain."""
        cursor = self.db.cursor()
        cursor.execute('SELECT tx_id, output_index, address, amount, spent FROM utxo WHERE spent = 0')
        
        self.unspent_outputs = {}
        for row in cursor.fetchall():
            tx_id, out_idx, address, amount, spent = row
            if address not in self.unspent_outputs:
                self.unspent_outputs[address] = []
            self.unspent_outputs[address].append({
                'tx_id': tx_id,
                'output_index': out_idx,
                'amount': amount
            })
    
    def create_genesis_block(self) -> Block:
        """Create the genesis block."""
        genesis_tx = Transaction(
            tx_type="coinbase",
            outputs=[{'address': self.dev_fund_address, 'amount': INITIAL_BLOCK_REWARD}],
            timestamp=get_timestamp(),
            fee=0
        )
        genesis_tx.tx_id = genesis_tx.compute_tx_id()
        
        genesis = Block(
            index=0,
            timestamp=get_timestamp(),
            transactions=[genesis_tx],
            prev_hash="0" * 64,
            nonce=0,
            difficulty=INITIAL_DIFFICULTY,
            merkle_root=genesis_tx.tx_id
        )
        genesis.merkle_root = genesis.compute_merkle_root()
        genesis.block_hash = genesis.compute_hash()
        
        # Mine genesis block (find valid nonce)
        while not genesis.hash_meets_difficulty(genesis.block_hash, genesis.difficulty):
            genesis.nonce += 1
            genesis.block_hash = genesis.compute_hash()
        
        self._save_block(genesis)
        self.chain.append(genesis)
        self._add_utxo(genesis_tx, 0)
        
        return genesis
    
    def get_latest_block(self) -> Optional[Block]:
        """Get the latest block in the chain."""
        return self.chain[-1] if self.chain else None
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Get block by index."""
        for block in self.chain:
            if block.index == index:
                return block
        return None
    
    def _calculate_block_reward(self, block_index: int) -> float:
        """Calculate block reward with halving."""
        halvings = block_index // HALVING_INTERVAL
        reward = INITIAL_BLOCK_REWARD / (2 ** halvings)
        return max(0, reward)
    
    def _adjust_difficulty(self, new_block_index: int) -> int:
        """Adjust difficulty based on block time."""
        if new_block_index % DIFFICULTY_ADJUSTMENT_INTERVAL != 0:
            return self.chain[-1].difficulty if self.chain else INITIAL_DIFFICULTY
        
        # Get the last adjustment point
        adjustment_index = new_block_index - DIFFICULTY_ADJUSTMENT_INTERVAL
        if adjustment_index < 0:
            return INITIAL_DIFFICULTY
        
        old_block = self.get_block_by_index(adjustment_index)
        if not old_block:
            return INITIAL_DIFFICULTY
        
        actual_time = self.chain[-1].timestamp - old_block.timestamp
        expected_time = DIFFICULTY_ADJUSTMENT_INTERVAL * BLOCK_TIME_TARGET
        
        current_diff = self.chain[-1].difficulty
        return calculate_difficulty_adjustment(
            actual_time, expected_time, current_diff,
            min_diff=1, max_diff=32
        )
    
    def mine_block(self, miner_address: str, extra_transactions: List[Transaction] = None) -> Optional[Block]:
        """Mine a new block with PoW."""
        with self.lock:
            if not self.chain:
                # Genesis block - reward goes to dev fund
                return self.create_genesis_block()
            
            latest_block = self.get_latest_block()
            difficulty = self._adjust_difficulty(latest_block.index + 1)
            
            # Get transactions from mempool
            txs = self.mempool.get_transactions()
            if extra_transactions:
                txs = extra_transactions + txs
            
            # Calculate total fees
            total_fees = sum(tx.fee for tx in txs)
            
            # Create coinbase transaction for block reward + fees
            block_reward = self._calculate_block_reward(latest_block.index + 1)
            coinbase_tx = Transaction(
                tx_type="coinbase",
                outputs=[{'address': miner_address, 'amount': block_reward + total_fees}],
                timestamp=get_timestamp(),
                fee=0
            )
            coinbase_tx.tx_id = coinbase_tx.compute_tx_id()
            
            # Create new block
            new_block = Block(
                index=latest_block.index + 1,
                timestamp=get_timestamp(),
                transactions=[coinbase_tx] + txs,
                prev_hash=latest_block.block_hash,
                nonce=0,
                difficulty=difficulty,
                merkle_root=""
            )
            new_block.merkle_root = new_block.compute_merkle_root()
            
            # PoW mining loop
            while not new_block.hash_meets_difficulty(new_block.block_hash, difficulty):
                new_block.nonce += 1
                new_block.block_hash = new_block.compute_hash()
                
                # Safety check for very long mining
                if new_block.nonce % 1000000 == 0:
                    pass  # Could add logging here
            
            # Save and update state
            self._save_block(new_block)
            self.chain.append(new_block)
            
            # Update UTXO
            for tx in new_block.transactions:
                if tx.tx_type != "coinbase":
                    self._spend_inputs(tx)
                self._add_utxo(tx, new_block.index)
            
            # Remove confirmed transactions from mempool
            confirmed_ids = [tx.tx_id for tx in txs if tx.tx_type != "coinbase"]
            self.mempool.remove_transactions(confirmed_ids)
            
            # Check for finality checkpoint
            if new_block.index % FINALITY_CHECKPOINT_INTERVAL == 0:
                self.stake_manager.add_checkpoint(
                    new_block.index,
                    new_block.block_hash,
                    []  # In real implementation, collect validator signatures
                )
            
            return new_block
    
    def mine_pos_block(self, validator_address: str, stake_amount: float) -> Optional[Block]:
        """Create a block using Proof of Stake."""
        if not POS_ENABLED:
            return None
        
        with self.lock:
            if not self.chain:
                return self.create_genesis_block()
            
            latest_block = self.get_latest_block()
            
            # Verify validator is registered and has sufficient stake
            validators = self.stake_manager.get_validators()
            validator = next((v for v in validators if v['address'] == validator_address), None)
            
            if not validator or validator['stake_amount'] < MIN_STAKE_AMOUNT:
                return None
            
            # Get transactions from mempool
            txs = self.mempool.get_transactions()
            total_fees = sum(tx.fee for tx in txs)
            
            # Block reward for PoS (same as PoW but no competition)
            block_reward = self._calculate_block_reward(latest_block.index + 1)
            coinbase_tx = Transaction(
                tx_type="coinbase",
                outputs=[{'address': validator_address, 'amount': block_reward + total_fees}],
                timestamp=get_timestamp(),
                fee=0
            )
            coinbase_tx.tx_id = coinbase_tx.compute_tx_id()
            
            difficulty = self._adjust_difficulty(latest_block.index + 1)
            
            new_block = Block(
                index=latest_block.index + 1,
                timestamp=get_timestamp(),
                transactions=[coinbase_tx] + txs,
                prev_hash=latest_block.block_hash,
                nonce=0,  # No PoW needed
                difficulty=difficulty,
                merkle_root="",
                validator=validator_address,
                stake_amount=stake_amount,
                checkpoint=(latest_block.index + 1) % FINALITY_CHECKPOINT_INTERVAL == 0
            )
            new_block.merkle_root = new_block.compute_merkle_root()
            new_block.block_hash = new_block.compute_hash()
            
            # For PoS, hash just needs to be valid (no leading zeros requirement for simplicity)
            self._save_block(new_block)
            self.chain.append(new_block)
            
            for tx in new_block.transactions:
                if tx.tx_type != "coinbase":
                    self._spend_inputs(tx)
                self._add_utxo(tx, new_block.index)
            
            confirmed_ids = [tx.tx_id for tx in txs if tx.tx_type != "coinbase"]
            self.mempool.remove_transactions(confirmed_ids)
            
            if new_block.checkpoint:
                self.stake_manager.add_checkpoint(new_block.index, new_block.block_hash, [])
            
            return new_block
    
    def _save_block(self, block: Block) -> None:
        """Save block to database."""
        cursor = self.db.cursor()
        txs_json = json.dumps([tx.to_dict() for tx in block.transactions])
        
        cursor.execute('''
            INSERT OR REPLACE INTO blocks 
            (block_index, timestamp, transactions, prev_hash, nonce, difficulty, merkle_root, 
             block_hash, validator, stake_amount, checkpoint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            block.index, block.timestamp, txs_json, block.prev_hash,
            block.nonce, block.difficulty, block.merkle_root, block.block_hash,
            block.validator, block.stake_amount, 1 if block.checkpoint else 0
        ))
        self.db.commit()
    
    def _add_utxo(self, tx: Transaction, block_index: int) -> None:
        """Add unspent transaction outputs."""
        cursor = self.db.cursor()
        
        for i, output in enumerate(tx.outputs):
            address = output['address']
            amount = output['amount']
            
            cursor.execute('''
                INSERT OR REPLACE INTO utxo (tx_id, output_index, address, amount, spent)
                VALUES (?, ?, ?, ?, 0)
            ''', (tx.tx_id, i, address, amount))
            
            if address not in self.unspent_outputs:
                self.unspent_outputs[address] = []
            self.unspent_outputs[address].append({
                'tx_id': tx.tx_id,
                'output_index': i,
                'amount': amount
            })
        
        self.db.commit()
    
    def _spend_inputs(self, tx: Transaction) -> None:
        """Mark transaction inputs as spent."""
        cursor = self.db.cursor()
        
        for inp in tx.inputs:
            tx_id = inp['tx_id']
            output_index = inp['output_index']
            
            cursor.execute('''
                UPDATE utxo SET spent = 1 WHERE tx_id = ? AND output_index = ?
            ''', (tx_id, output_index))
            
            # Remove from in-memory UTXO
            for addr in self.unspent_outputs:
                self.unspent_outputs[addr] = [
                    u for u in self.unspent_outputs[addr]
                    if not (u['tx_id'] == tx_id and u['output_index'] == output_index)
                ]
        
        self.db.commit()
    
    def create_transaction(
        self,
        sender_wallet: Wallet,
        recipient_address: str,
        amount: float,
        fee: float = MIN_TRANSACTION_FEE
    ) -> Tuple[Optional[Transaction], str]:
        """Create and sign a new transaction."""
        if not verify_address(recipient_address):
            return None, "Invalid recipient address"
        
        # Find sufficient UTXOs
        sender_address = sender_wallet.address
        utxos = self.unspent_outputs.get(sender_address, [])
        
        total_available = sum(u['amount'] for u in utxos)
        if total_available < amount + fee:
            return None, f"Insufficient balance. Available: {total_available}, Need: {amount + fee}"
        
        # Select UTXOs (simple first-fit)
        selected_utxos = []
        total_selected = 0
        
        for utxo in utxos:
            selected_utxos.append(utxo)
            total_selected += utxo['amount']
            if total_selected >= amount + fee:
                break
        
        # Create inputs
        inputs = [
            {'tx_id': u['tx_id'], 'output_index': u['output_index'], 'amount': u['amount']}
            for u in selected_utxos
        ]
        
        # Create outputs
        outputs = [{'address': recipient_address, 'amount': amount}]
        change = total_selected - amount - fee
        if change > 0:
            outputs.append({'address': sender_address, 'amount': change})
        
        # Create transaction
        tx = Transaction(
            version=1,
            inputs=inputs,
            outputs=outputs,
            timestamp=get_timestamp(),
            fee=fee,
            public_key=bytes_to_hex(sender_wallet.get_public_key())
        )
        
        # Sign transaction
        signature = sender_wallet.sign_transaction(tx.serialize())
        tx.signature = bytes_to_hex(signature)
        tx.tx_id = tx.compute_tx_id()
        
        # Validate before adding
        valid, msg = tx.validate()
        if not valid:
            return None, msg
        
        return tx, "Transaction created successfully"
    
    def add_transaction(self, tx: Transaction) -> Tuple[bool, str]:
        """Add a transaction to the mempool."""
        return self.mempool.add_transaction(tx)
    
    def get_balance(self, address: str) -> float:
        """Get balance for an address."""
        utxos = self.unspent_outputs.get(address, [])
        return sum(u['amount'] for u in utxos)
    
    def validate_chain(self) -> Tuple[bool, str]:
        """Validate the entire blockchain."""
        if not self.chain:
            return False, "Empty chain"
        
        # Check genesis block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.prev_hash != "0" * 64:
            return False, "Invalid genesis block"
        
        for i in range(1, len(self.chain)):
            prev_block = self.chain[i - 1]
            curr_block = self.chain[i]
            
            # Check index continuity
            if curr_block.index != prev_block.index + 1:
                return False, f"Block index mismatch at {i}"
            
            # Check previous hash link
            if curr_block.prev_hash != prev_block.block_hash:
                return False, f"Previous hash mismatch at {i}"
            
            # Verify PoW difficulty
            if not curr_block.hash_meets_difficulty(curr_block.block_hash, curr_block.difficulty):
                return False, f"Block {i} does not meet difficulty requirement"
            
            # Verify Merkle root
            computed_merkle = curr_block.compute_merkle_root()
            if computed_merkle != curr_block.merkle_root:
                return False, f"Merkle root mismatch at block {i}"
            
            # Verify block hash
            computed_hash = curr_block.compute_hash()
            if computed_hash != curr_block.block_hash:
                return False, f"Block hash mismatch at {i}"
        
        return True, "Chain is valid"
    
    def get_chain_length(self) -> int:
        """Get the current chain length."""
        return len(self.chain)
    
    def resolve_conflicts(self, other_chain: List[Block]) -> bool:
        """Resolve conflicts using longest chain rule."""
        if len(other_chain) <= len(self.chain):
            return False
        
        # Validate the other chain
        temp_chain = Blockchain(":memory:")
        temp_chain.chain = other_chain
        
        valid, _ = temp_chain.validate_chain()
        if not valid:
            return False
        
        # Replace our chain
        with self.lock:
            self.chain = other_chain
            self._rebuild_utxo()
        
        return True
    
    def close(self) -> None:
        """Close database connection."""
        self.db.close()
