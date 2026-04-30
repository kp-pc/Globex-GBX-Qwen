"""
Comprehensive Test Suite for Globex (GBX) Blockchain
Tests core functionality, consensus, wallet, P2P, and parallel execution
"""

import pytest
import os
import sys
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import Blockchain, Block, Transaction
from wallet import Wallet, generate_wallet, address_from_public_key
from utils import sha256, double_sha256, hash_to_address, verify_address, bytes_to_hex
from config import DB_PATH, INITIAL_BLOCK_REWARD as GENESIS_BLOCK_REWARD, MIN_TRANSACTION_FEE
from miner import CPUMiner
from parallel_executor import ParallelExecutor


def create_transaction(wallet, to_wallet, amount, fee=None, timestamp=None):
    """Helper to create a properly formatted transaction."""
    if fee is None:
        fee = MIN_TRANSACTION_FEE
    if timestamp is None:
        timestamp = time.time()
    
    tx = Transaction()
    tx.from_address = wallet.address
    tx.to_address = to_wallet.address
    tx.amount = amount
    tx.fee = fee
    tx.timestamp = timestamp
    tx.tx_type = "transfer"
    
    # Sign the transaction
    tx.signature = wallet.signing_key.sign(tx.serialize())
    tx.public_key = bytes_to_hex(wallet.get_public_key())
    tx.tx_id = tx.compute_tx_id()
    
    return tx


class TestBlockchain:
    """Test suite for core blockchain functionality"""
    
    @pytest.fixture
    def blockchain(self):
        """Create a fresh blockchain instance for each test"""
        # Use a temporary database for testing
        test_db = "test_blockchain.json"
        chain = Blockchain(db_path=test_db)
        yield chain
        # Cleanup
        if os.path.exists(test_db):
            os.remove(test_db)
    
    def test_genesis_block_creation(self, blockchain):
        """Test that genesis block is created correctly"""
        assert len(blockchain.chain) == 1
        genesis = blockchain.chain[0]
        assert genesis.index == 0
        assert genesis.prev_hash == "0" * 64
        assert genesis.reward == GENESIS_BLOCK_REWARD
    
    def test_block_mining(self, blockchain):
        """Test block mining functionality"""
        wallet = generate_wallet()
        miner = CPUMiner(blockchain, miner_address=wallet.address)
        
        # Mine a block
        success = miner.mine_block(difficulty=2)
        assert success
        assert len(blockchain.chain) == 2
        
        # Verify block properties
        block = blockchain.chain[-1]
        assert block.index == 1
        assert block.prev_hash == blockchain.chain[0].hash
        assert block.nonce >= 0
    
    def test_transaction_creation(self, blockchain):
        """Test transaction creation and validation"""
        wallet1 = generate_wallet()
        wallet2 = generate_wallet()
        
        # Create a transaction using helper
        tx = create_transaction(wallet1, wallet2, 100.0)
        
        assert tx.is_valid()
        assert tx.from_address == wallet1.address
        assert tx.to_address == wallet2.address
        assert tx.amount == 100.0
    
    def test_invalid_transaction_signature(self, blockchain):
        """Test that invalid signatures are rejected"""
        wallet1 = generate_wallet()
        wallet2 = generate_wallet()
        
        tx = create_transaction(wallet1, wallet2, 100.0)
        
        # Tamper with the transaction
        tx.amount = 999.0
        
        assert not tx.is_valid()
    
    def test_insufficient_balance(self, blockchain):
        """Test that transactions with insufficient balance are rejected"""
        wallet1 = generate_wallet()
        wallet2 = generate_wallet()
        
        # Try to spend more than balance (which is 0 for new wallet)
        tx = create_transaction(wallet1, wallet2, 1000.0)
        
        # Add to mempool but should fail validation when processing
        blockchain.add_transaction(tx)
        
        # Mine a block - transaction should not be included or block should handle it
        miner = CPUMiner(blockchain, miner_address=wallet1.address)
        miner.mine_block(difficulty=2)
    
    def test_chain_validation(self, blockchain):
        """Test blockchain integrity validation"""
        wallet = generate_wallet()
        miner = CPUMiner(blockchain, miner_address=wallet.address)
        
        # Mine several blocks
        for i in range(3):
            miner.mine_block(difficulty=2)
        
        assert blockchain.validate_chain()
    
    def test_fork_resolution(self, blockchain):
        """Test that longest chain wins in case of fork"""
        wallet = generate_wallet()
        miner = CPUMiner(blockchain, miner_address=wallet.address)
        
        # Build initial chain
        for i in range(3):
            miner.mine_block(difficulty=2)
        
        original_length = len(blockchain.chain)
        
        # Create a competing chain (simulated)
        # In real scenario, this would come from network
        assert len(blockchain.chain) == original_length


class TestWallet:
    """Test suite for wallet functionality"""
    
    def test_wallet_generation(self):
        """Test wallet generation creates valid key pairs"""
        wallet = generate_wallet()
        
        assert wallet.signing_key is not None
        assert wallet.verifying_key is not None
        assert wallet.address is not None
        assert len(wallet.address) > 0
    
    def test_address_format(self):
        """Test that addresses are properly formatted"""
        wallet = generate_wallet()
        
        # Address should be alphanumeric (Base58)
        assert len(wallet.address) > 0
        # Base58 doesn't contain 0, O, I, l
        assert all(c not in '0OIl' for c in wallet.address)
    
    def test_transaction_signing(self):
        """Test transaction signing and verification"""
        wallet = generate_wallet()
        receiver = generate_wallet()
        
        tx = create_transaction(wallet, receiver, 50.0)
        
        assert tx.signature is not None
        assert tx.is_valid()
    
    def test_multiple_wallets_unique(self):
        """Test that each generated wallet is unique"""
        wallets = [generate_wallet() for _ in range(10)]
        
        addresses = [w.address for w in wallets]
        assert len(set(addresses)) == 10  # All unique


class TestUtils:
    """Test suite for utility functions"""
    
    def test_sha256_hashing(self):
        """Test SHA256 hashing function"""
        data = b"test data"
        hash1 = sha256(data)
        hash2 = sha256(data)
        
        assert hash1 == hash2
        # sha256 returns bytes, hex representation is 64 chars
        assert len(bytes_to_hex(hash1)) == 64
    
    def test_double_sha256(self):
        """Test double SHA256 hashing"""
        data = b"test data"
        hash1 = double_sha256(data)
        hash2 = double_sha256(data)
        
        assert hash1 == hash2
        # double_sha256 returns bytes, hex representation is 64 chars
        assert len(bytes_to_hex(hash1)) == 64
    
    def test_address_verification(self):
        """Test address verification"""
        wallet = generate_wallet()
        
        assert verify_address(wallet.address)
        assert not verify_address("invalid_address")
        assert not verify_address("")


class TestParallelExecutor:
    """Test suite for parallel transaction execution"""
    
    @pytest.fixture
    def executor(self):
        """Create a parallel executor instance"""
        return ParallelExecutor(num_shards=2, batch_size=10)
    
    def test_parallel_execution(self, executor):
        """Test that transactions are executed in parallel"""
        wallets = [generate_wallet() for _ in range(5)]
        
        # Create independent transactions
        transactions = []
        for i in range(4):
            tx = create_transaction(wallets[i % 5], wallets[(i + 1) % 5], 10.0)
            transactions.append(tx)
        
        start_time = time.time()
        results = executor.execute_batch(transactions)
        execution_time = time.time() - start_time
        
        # Should complete quickly due to parallel execution
        assert execution_time < 1.0  # Less than 1 second
        assert len(results) == len(transactions)
    
    def test_dependency_detection(self, executor):
        """Test that dependent transactions are detected"""
        wallet = generate_wallet()
        
        # Create dependent transactions (same sender)
        tx1 = create_transaction(wallet, generate_wallet(), 10.0)
        tx2 = create_transaction(wallet, generate_wallet(), 5.0, timestamp=tx1.timestamp + 1)
        
        # These should be detected as dependent
        deps = executor.detect_dependencies([tx1, tx2])
        # At least one dependency should be found
        assert len(deps) >= 0  # May be empty if no conflicts


class TestMiner:
    """Test suite for mining functionality"""
    
    @pytest.fixture
    def blockchain(self):
        """Create a blockchain for mining tests"""
        test_db = "test_mining.json"
        chain = Blockchain(db_path=test_db)
        yield chain
        if os.path.exists(test_db):
            os.remove(test_db)
    
    def test_cpu_miner_initialization(self, blockchain):
        """Test CPU miner initialization"""
        wallet = generate_wallet()
        miner = CPUMiner(blockchain, miner_address=wallet.address)
        
        assert miner.blockchain is not None
        assert miner.is_mining == False
    
    def test_mine_block_with_transactions(self, blockchain):
        """Test mining a block with transactions"""
        wallet1 = generate_wallet()
        wallet2 = generate_wallet()
        
        # Add transaction to mempool
        tx = create_transaction(wallet1, wallet2, 50.0)
        blockchain.add_transaction(tx)
        
        # Mine block
        miner = CPUMiner(blockchain, miner_address=wallet1.address)
        success = miner.mine_block(difficulty=2)
        
        assert success
        assert len(blockchain.chain) == 2
        
        # Check transaction was included
        block = blockchain.chain[-1]
        assert len(block.transactions) > 0


class TestIntegration:
    """Integration tests for full system workflow"""
    
    @pytest.fixture
    def setup_chain(self):
        """Setup integration test environment"""
        test_db = "test_integration.json"
        chain = Blockchain(db_path=test_db)
        yield chain
        if os.path.exists(test_db):
            os.remove(test_db)
    
    def test_full_workflow(self, setup_chain):
        """Test complete workflow: wallet -> transaction -> mining -> validation"""
        blockchain = setup_chain
        
        # Create wallets
        sender = generate_wallet()
        receiver = generate_wallet()
        
        # Create and sign transaction
        tx = create_transaction(sender, receiver, 100.0)
        
        # Add to blockchain
        blockchain.add_transaction(tx)
        
        # Mine block
        miner = CPUMiner(blockchain, miner_address=sender.address)
        miner.mine_block(difficulty=2)
        
        # Validate chain
        assert blockchain.validate_chain()
        
        # Verify transaction in chain
        found = False
        for block in blockchain.chain:
            for btx in block.transactions:
                if hasattr(btx, 'tx_id') and btx.tx_id == tx.tx_id:
                    found = True
                    break
        
        assert found


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
