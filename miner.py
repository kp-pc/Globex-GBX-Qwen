"""
Globex (GBX) CPU Miner
Lightweight mining client optimized for CPU/ARM devices
"""

import time
import threading
import hashlib
import json
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from core import Blockchain, Block, Transaction
from wallet import Wallet, generate_wallet
from utils import double_sha256, bytes_to_hex, get_timestamp
from config import (
    INITIAL_DIFFICULTY, BLOCK_TIME_TARGET, MINER_THREADS, MINER_NONCE_BATCH_SIZE
)


class CPUMiner:
    """CPU-based Proof-of-Work miner for Globex."""
    
    def __init__(
        self,
        blockchain: Blockchain,
        miner_address: str,
        threads: int = MINER_THREADS,
        on_block_found: Optional[Callable[[Block], None]] = None
    ):
        self.blockchain = blockchain
        self.miner_address = miner_address
        self.threads = threads
        self.on_block_found = on_block_found
        
        self.mining = False
        self.current_job: Optional[dict] = None
        self.nonce_counter = 0
        self.hashes_computed = 0
        self.blocks_found = 0
        self.start_time: Optional[float] = None
        
        self.lock = threading.Lock()
        self.executor: Optional[ThreadPoolExecutor] = None
    
    def _compute_hash(self, header_data: bytes, nonce: int, difficulty: int) -> tuple:
        """Compute hash for a given nonce and check if it meets difficulty."""
        header = json.loads(header_data.decode())
        header['nonce'] = nonce
        new_header_data = json.dumps(header, sort_keys=True).encode()
        block_hash = bytes_to_hex(double_sha256(new_header_data))
        
        self._increment_hashes(1)
        
        target = '0' * difficulty
        if block_hash.startswith(target):
            return True, nonce, block_hash
        
        return False, nonce, block_hash
    
    def _increment_hashes(self, count: int) -> None:
        """Increment the hash counter."""
        with self.lock:
            self.hashes_computed += count
    
    def _get_hash_rate(self) -> float:
        """Get current hash rate (hashes per second)."""
        if not self.start_time:
            return 0.0
        
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        
        return self.hashes_computed / elapsed
    
    def _mine_nonce_range(self, start_nonce: int, end_nonce: int, 
                          header_data: bytes, difficulty: int) -> Optional[tuple]:
        """Mine a range of nonces."""
        header = json.loads(header_data.decode())
        
        for nonce in range(start_nonce, end_nonce):
            if not self.mining:
                return None
            
            header['nonce'] = nonce
            new_header_data = json.dumps(header, sort_keys=True).encode()
            block_hash = bytes_to_hex(double_sha256(new_header_data))
            
            self._increment_hashes(1)
            
            target = '0' * difficulty
            if block_hash.startswith(target):
                return (nonce, block_hash)
            
            # Check every 10000 nonces
            if nonce % 10000 == 0:
                pass
        
        return None
    
    def _worker(self, job: dict) -> Optional[tuple]:
        """Worker thread for mining."""
        header_data = job['header_data']
        difficulty = job['difficulty']
        base_nonce = job['base_nonce']
        
        result = self._mine_nonce_range(
            base_nonce,
            base_nonce + MINER_NONCE_BATCH_SIZE,
            header_data,
            difficulty
        )
        
        return result
    
    def start(self) -> bool:
        """Start the mining process."""
        if self.mining:
            return False
        
        self.mining = True
        self.start_time = time.time()
        self.hashes_computed = 0
        self.executor = ThreadPoolExecutor(max_workers=self.threads)
        
        print(f"Miner started with {self.threads} threads")
        print(f"Mining to address: {self.miner_address}")
        
        self._mining_loop()
        return True
    
    def stop(self) -> None:
        """Stop the mining process."""
        self.mining = False
        if self.executor:
            self.executor.shutdown(wait=False)
        print("Miner stopped")
    
    def _mining_loop(self) -> None:
        """Main mining loop."""
        while self.mining:
            try:
                # Get latest block and prepare new block template
                latest_block = self.blockchain.get_latest_block()
                
                if not latest_block:
                    # Create genesis block
                    block = self.blockchain.mine_block(self.miner_address)
                    if block:
                        self.blocks_found += 1
                        print(f"\n{'='*50}")
                        print(f"GENESIS BLOCK FOUND!")
                        print(f"Index: {block.index}")
                        print(f"Hash: {block.block_hash}")
                        print(f"Reward: {self.blockchain._calculate_block_reward(block.index)} GBX")
                        print(f"{'='*50}\n")
                        
                        if self.on_block_found:
                            self.on_block_found(block)
                    continue
                
                # Calculate difficulty for next block
                difficulty = self.blockchain._adjust_difficulty(latest_block.index + 1)
                
                # Prepare block template
                timestamp = get_timestamp()
                merkle_root = ""  # Will be computed
                
                # Get pending transactions
                txs = self.blockchain.mempool.get_transactions()
                
                # Calculate fees
                total_fees = sum(tx.fee for tx in txs)
                block_reward = self.blockchain._calculate_block_reward(latest_block.index + 1)
                
                # Create coinbase transaction
                coinbase_tx = Transaction(
                    tx_type="coinbase",
                    outputs=[{'address': self.miner_address, 'amount': block_reward + total_fees}],
                    timestamp=timestamp,
                    fee=0
                )
                coinbase_tx.tx_id = coinbase_tx.compute_tx_id()
                
                # Build block
                new_block = Block(
                    index=latest_block.index + 1,
                    timestamp=timestamp,
                    transactions=[coinbase_tx] + txs,
                    prev_hash=latest_block.block_hash,
                    nonce=0,
                    difficulty=difficulty,
                    merkle_root=""
                )
                new_block.merkle_root = new_block.compute_merkle_root()
                
                # Prepare header for mining
                header = {
                    'index': new_block.index,
                    'timestamp': new_block.timestamp,
                    'prev_hash': new_block.prev_hash,
                    'merkle_root': new_block.merkle_root,
                    'difficulty': new_block.difficulty,
                    'nonce': 0
                }
                header_data = json.dumps(header, sort_keys=True).encode()
                
                # Mine with multiple threads
                futures = []
                batch_size = MINER_NONCE_BATCH_SIZE
                
                for i in range(self.threads):
                    base_nonce = self.nonce_counter + (i * batch_size)
                    job = {
                        'header_data': header_data,
                        'difficulty': difficulty,
                        'base_nonce': base_nonce
                    }
                    future = self.executor.submit(self._worker, job)
                    futures.append(future)
                
                # Wait for results
                found = False
                for future in futures:
                    result = future.result(timeout=5)
                    if result:
                        nonce, block_hash = result
                        
                        # Found valid block!
                        new_block.nonce = nonce
                        new_block.block_hash = block_hash
                        
                        # Save block to chain
                        self.blockchain._save_block(new_block)
                        self.blockchain.chain.append(new_block)
                        
                        # Update UTXO
                        for tx in new_block.transactions:
                            if tx.tx_type != "coinbase":
                                self.blockchain._spend_inputs(tx)
                            self.blockchain._add_utxo(tx, new_block.index)
                        
                        # Clear mempool
                        confirmed_ids = [tx.tx_id for tx in txs if tx.tx_type != "coinbase"]
                        self.blockchain.mempool.remove_transactions(confirmed_ids)
                        
                        self.blocks_found += 1
                        self.nonce_counter = 0
                        
                        print(f"\n{'='*50}")
                        print(f"BLOCK FOUND!")
                        print(f"Index: {new_block.index}")
                        print(f"Hash: {new_block.block_hash}")
                        print(f"Nonce: {new_block.nonce}")
                        print(f"Difficulty: {new_block.difficulty}")
                        print(f"Transactions: {len(new_block.transactions)}")
                        print(f"Reward: {block_reward + total_fees:.4f} GBX")
                        print(f"Hash Rate: {self._get_hash_rate():.2f} H/s")
                        print(f"Total Blocks: {self.blocks_found}")
                        print(f"{'='*50}\n")
                        
                        if self.on_block_found:
                            self.on_block_found(new_block)
                        
                        found = True
                        break
                
                if not found:
                    self.nonce_counter += self.threads * batch_size
                
                # Print status every 10 seconds
                if self.start_time and (time.time() - self.start_time) % 10 < 1:
                    print(f"Mining... Hash Rate: {self._get_hash_rate():.2f} H/s | "
                          f"Blocks: {self.blocks_found} | "
                          f"Chain Length: {self.blockchain.get_chain_length()}")
                
                time.sleep(0.1)  # Small delay between iterations
                
            except Exception as e:
                print(f"Mining error: {e}")
                time.sleep(1)
    
    def get_stats(self) -> dict:
        """Get mining statistics."""
        return {
            'mining': self.mining,
            'miner_address': self.miner_address,
            'threads': self.threads,
            'hashes_computed': self.hashes_computed,
            'hash_rate': self._get_hash_rate(),
            'blocks_found': self.blocks_found,
            'running_time': time.time() - self.start_time if self.start_time else 0
        }


def mine_single_block(blockchain: Blockchain, miner_address: str, 
                      verbose: bool = True) -> Optional[Block]:
    """Mine a single block (convenience function)."""
    return blockchain.mine_block(miner_address)


if __name__ == '__main__':
    # Example usage
    from core import Blockchain
    from wallet import generate_wallet
    
    # Create blockchain and wallet
    bc = Blockchain()
    wallet = generate_wallet()
    
    print(f"Miner address: {wallet.address}")
    print(f"Private key (SAVE THIS): {wallet.get_private_key().hex()}")
    
    # Create miner
    miner = CPUMiner(bc, wallet.address, threads=2)
    
    try:
        miner.start()
    except KeyboardInterrupt:
        miner.stop()
