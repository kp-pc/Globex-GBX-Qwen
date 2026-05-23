"""
Globex (GBX) Parallel Transaction Executor
High-performance parallel execution engine for Polygon-level speed
"""

import threading
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

from config import (
    PARALLEL_EXECUTION_ENABLED, MAX_PARALLEL_TX_BATCH,
    EXECUTION_SHARDS, TARGET_TPS
)
from core import Transaction, Block


@dataclass
class ExecutionResult:
    """Result of transaction execution."""
    tx_id: str
    success: bool
    state_changes: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    gas_used: int = 0
    execution_time: float = 0.0


class StateShard:
    """Represents a shard of the blockchain state for parallel execution."""
    
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self.state: Dict[str, Any] = {}
        self.lock = threading.RLock()
        self.account_range: Tuple[int, int] = (0, 0)
    
    def get_account(self, address: str) -> Optional[Dict]:
        """Get account data from this shard."""
        with self.lock:
            return self.state.get(address)
    
    def set_account(self, address: str, data: Dict):
        """Set account data in this shard."""
        with self.lock:
            self.state[address] = data
    
    def update_balance(self, address: str, amount: float):
        """Update account balance atomically."""
        with self.lock:
            if address not in self.state:
                self.state[address] = {'balance': 0, 'nonce': 0}
            self.state[address]['balance'] += amount
    
    def get_accounts_in_range(self, start: int, end: int) -> List[str]:
        """Get accounts within a hash range."""
        with self.lock:
            accounts = []
            for addr in self.state.keys():
                addr_hash = int(hashlib.sha256(addr.encode()).hexdigest(), 16)
                if start <= addr_hash < end:
                    accounts.append(addr)
            return accounts


class TransactionScheduler:
    """Schedules transactions for parallel execution based on dependencies."""
    
    def __init__(self, num_shards: int = EXECUTION_SHARDS):
        self.num_shards = num_shards
        self.shards = [StateShard(i) for i in range(num_shards)]
        self.pending_txs: List[Transaction] = []
        self.executed_txs: Set[str] = set()
        self.lock = threading.Lock()
    
    def _get_shard_for_address(self, address: str) -> int:
        """Determine which shard an address belongs to."""
        addr_hash = int(hashlib.sha256(address.encode()).hexdigest(), 16)
        max_hash = 2 ** 256
        shard_size = max_hash // self.num_shards
        return min(addr_hash // shard_size, self.num_shards - 1)
    
    def _get_dependencies(self, tx: Transaction) -> Set[str]:
        """Get addresses that this transaction depends on."""
        deps = set()
        for inp in tx.inputs:
            if 'address' in inp:
                deps.add(inp['address'])
        for out in tx.outputs:
            if 'address' in out:
                deps.add(out['address'])
        return deps
    
    def _can_execute_parallel(self, tx1: Transaction, tx2: Transaction) -> bool:
        """Check if two transactions can be executed in parallel."""
        deps1 = self._get_dependencies(tx1)
        deps2 = self._get_dependencies(tx2)
        
        # No overlapping dependencies = can execute in parallel
        return len(deps1.intersection(deps2)) == 0
    
    def schedule_batch(self, transactions: List[Transaction]) -> List[List[Transaction]]:
        """
        Schedule a batch of transactions into parallel execution groups.
        Returns list of groups, where each group can be executed in parallel.
        """
        if not transactions:
            return []
        
        groups: List[List[Transaction]] = []
        remaining = transactions.copy()
        
        while remaining:
            current_group = [remaining.pop(0)]
            next_remaining = []
            
            for tx in remaining:
                # Check if tx can execute in parallel with all txs in current group
                can_add = all(
                    self._can_execute_parallel(tx, group_tx)
                    for group_tx in current_group
                )
                
                if can_add:
                    current_group.append(tx)
                else:
                    next_remaining.append(tx)
            
            groups.append(current_group)
            remaining = next_remaining
        
        return groups
    
    def get_shard(self, address: str) -> StateShard:
        """Get the shard for an address."""
        shard_id = self._get_shard_for_address(address)
        return self.shards[shard_id]


class ParallelExecutor:
    """Main parallel execution engine for high-throughput transaction processing."""
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or EXECUTION_SHARDS
        self.scheduler = TransactionScheduler(num_shards=self.num_workers)
        self.executor = ThreadPoolExecutor(max_workers=self.num_workers)
        self.execution_stats = {
            'total_executed': 0,
            'successful': 0,
            'failed': 0,
            'avg_execution_time': 0.0,
            'tps': 0.0
        }
        self.stats_lock = threading.Lock()
        self.enabled = PARALLEL_EXECUTION_ENABLED
    
    def execute_transaction(self, tx: Transaction, state: Dict) -> ExecutionResult:
        """Execute a single transaction."""
        start_time = time.time()
        
        try:
            # Validate transaction
            valid, msg = tx.validate()
            if not valid:
                return ExecutionResult(
                    tx_id=tx.tx_id,
                    success=False,
                    error=msg
                )
            
            # Simulate execution (in real implementation, this would apply state changes)
            state_changes = {}
            
            # Update balances
            for inp in tx.inputs:
                addr = inp.get('address', '')
                if addr in state:
                    state[addr]['balance'] -= inp.get('amount', 0)
                    state_changes[addr] = state[addr].copy()
            
            for out in tx.outputs:
                addr = out.get('address', '')
                if addr not in state:
                    state[addr] = {'balance': 0, 'nonce': 0}
                state[addr]['balance'] += out.get('amount', 0)
                state_changes[addr] = state[addr].copy()
            
            execution_time = time.time() - start_time
            
            with self.stats_lock:
                self.execution_stats['total_executed'] += 1
                self.execution_stats['successful'] += 1
                
                # Update running average
                n = self.execution_stats['total_executed']
                avg = self.execution_stats['avg_execution_time']
                self.execution_stats['avg_execution_time'] = avg + (execution_time - avg) / n
            
            return ExecutionResult(
                tx_id=tx.tx_id,
                success=True,
                state_changes=state_changes,
                execution_time=execution_time,
                gas_used=21000  # Standard gas cost
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            with self.stats_lock:
                self.execution_stats['total_executed'] += 1
                self.execution_stats['failed'] += 1
            
            return ExecutionResult(
                tx_id=tx.tx_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def execute_batch_parallel(self, transactions: List[Transaction], 
                               global_state: Dict) -> List[ExecutionResult]:
        """Execute a batch of transactions in parallel."""
        if not self.enabled or len(transactions) <= 1:
            # Sequential execution for small batches or if disabled
            return [self.execute_transaction(tx, global_state) for tx in transactions]
        
        # Schedule transactions into parallel groups
        groups = self.scheduler.schedule_batch(transactions[:MAX_PARALLEL_TX_BATCH])
        
        results: List[ExecutionResult] = []
        futures = []
        
        # Execute each group in parallel
        for group in groups:
            group_futures = []
            for tx in group:
                future = self.executor.submit(
                    self.execute_transaction,
                    tx,
                    global_state
                )
                group_futures.append(future)
            
            # Wait for all transactions in this group to complete
            for future in as_completed(group_futures):
                result = future.result()
                results.append(result)
        
        # Update TPS metric
        if results:
            total_time = sum(r.execution_time for r in results)
            if total_time > 0:
                tps = len(results) / total_time
                with self.stats_lock:
                    self.execution_stats['tps'] = tps
        
        return results
    
    def get_stats(self) -> Dict:
        """Get execution statistics."""
        with self.stats_lock:
            return self.execution_stats.copy()
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)


# Example usage and benchmarking
if __name__ == "__main__":
    import random
    
    print("Parallel Executor Benchmark")
    print("=" * 50)
    
    executor = ParallelExecutor(num_workers=4)
    
    # Create test transactions
    def create_test_tx(sender: str, receiver: str, amount: float) -> Transaction:
        from core import Transaction
        tx = Transaction(
            version=1,
            inputs=[{'address': sender, 'amount': amount}],
            outputs=[{'address': receiver, 'amount': amount}],
            timestamp=time.time(),
            fee=0.0001
        )
        tx.tx_id = tx.compute_tx_id()
        return tx
    
    # Generate test transactions
    test_state = {f"addr_{i}": {'balance': 10000, 'nonce': 0} for i in range(100)}
    test_txs = []
    
    for i in range(100):
        sender = f"addr_{random.randint(0, 99)}"
        receiver = f"addr_{random.randint(0, 99)}"
        while receiver == sender:
            receiver = f"addr_{random.randint(0, 99)}"
        
        tx = create_test_tx(sender, receiver, random.uniform(1, 100))
        test_txs.append(tx)
    
    # Execute in parallel
    start = time.time()
    results = executor.execute_batch_parallel(test_txs, test_state)
    elapsed = time.time() - start
    
    stats = executor.get_stats()
    
    print(f"Transactions executed: {len(results)}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total time: {elapsed:.3f}s")
    print(f"Avg execution time: {stats['avg_execution_time']*1000:.2f}ms")
    print(f"Throughput: {len(results)/elapsed:.1f} TPS")
    print(f"Target TPS: {TARGET_TPS}")
    
    executor.shutdown()
