"""
Globex (GBX) Utility Functions
Hashing, Base58 encoding, Merkle tree implementation
"""

import hashlib
import time
from typing import List, Optional


def sha256(data: bytes) -> bytes:
    """Compute SHA-256 hash of data."""
    return hashlib.sha256(data).digest()


def double_sha256(data: bytes) -> bytes:
    """Compute double SHA-256 hash (Bitcoin-style)."""
    return sha256(sha256(data))


def ripemd160(data: bytes) -> bytes:
    """Compute RIPEMD-160 hash of data."""
    h = hashlib.new('ripemd160')
    h.update(data)
    return h.digest()


# Base58 alphabet (Bitcoin-style, excluding 0, O, I, l)
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58 string."""
    # Count leading zeros
    leading_zeros = len(data) - len(data.lstrip(b'\x00'))
    
    # Convert bytes to integer
    num = int.from_bytes(data, 'big')
    
    # Convert to Base58
    result = []
    while num > 0:
        num, remainder = divmod(num, 58)
        result.append(BASE58_ALPHABET[remainder])
    
    # Add leading '1's for each leading zero byte
    result.extend(BASE58_ALPHABET[0] * leading_zeros)
    
    return ''.join(reversed(result)) if result else BASE58_ALPHABET[0]


def base58_decode(s: str) -> bytes:
    """Decode Base58 string to bytes."""
    # Convert Base58 string to integer
    num = 0
    for char in s:
        num = num * 58 + BASE58_ALPHABET.index(char)
    
    # Convert integer to bytes
    result = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    
    # Add back leading zeros
    leading_ones = len(s) - len(s.lstrip(BASE58_ALPHABET[0]))
    return b'\x00' * leading_ones + result


def hash_to_address(pubkey_hash: bytes) -> str:
    """Convert public key hash to Base58 address with version prefix."""
    version = b'\x30'  # Globex version byte (0x30 = 48)
    payload = version + pubkey_hash
    checksum = double_sha256(payload)[:4]
    return base58_encode(payload + checksum)


def verify_address(address: str) -> bool:
    """Verify a Globex address format and checksum."""
    try:
        decoded = base58_decode(address)
        if len(decoded) != 25:  # 1 version + 20 pubkey hash + 4 checksum
            return False
        
        payload = decoded[:-4]
        checksum = decoded[-4:]
        
        expected_checksum = double_sha256(payload)[:4]
        return checksum == expected_checksum
    except Exception:
        return False


class MerkleTree:
    """Merkle Tree implementation for transaction hashing."""
    
    def __init__(self, data_items: List[bytes]):
        """Initialize Merkle tree with list of data items (transaction hashes)."""
        self.leaves = [double_sha256(item) if isinstance(item, bytes) else double_sha256(item.encode()) 
                       for item in data_items]
        self.tree = self._build_tree()
        self.root = self.tree[-1] if self.tree else double_sha256(b'')
    
    def _build_tree(self) -> List[bytes]:
        """Build the Merkle tree from leaves."""
        if not self.leaves:
            return [double_sha256(b'')]
        
        # Pad to power of 2 if necessary
        nodes = self.leaves[:]
        while len(nodes) & (len(nodes) - 1) != 0 or len(nodes) < 2:
            nodes.append(nodes[-1])  # Duplicate last node
        
        tree = nodes[:]
        
        while len(nodes) > 1:
            next_level = []
            for i in range(0, len(nodes), 2):
                combined = nodes[i] + nodes[i + 1]
                parent = double_sha256(combined)
                next_level.append(parent)
            tree.extend(next_level)
            nodes = next_level
        
        return tree
    
    def get_root(self) -> bytes:
        """Get the Merkle root hash."""
        return self.root
    
    def get_proof(self, index: int) -> List[tuple]:
        """Get Merkle proof for leaf at given index."""
        if index < 0 or index >= len(self.leaves):
            return []
        
        proof = []
        nodes = self.leaves[:]
        
        # Pad to power of 2
        while len(nodes) & (len(nodes) - 1) != 0 or len(nodes) < 2:
            nodes.append(nodes[-1])
        
        idx = index
        level_start = 0
        
        while len(nodes) > 1:
            level_size = len(nodes)
            sibling_idx = idx ^ 1  # XOR to get sibling
            
            if sibling_idx < level_size:
                direction = 'left' if idx % 2 == 1 else 'right'
                proof.append((nodes[sibling_idx], direction))
            
            # Move to next level
            idx //= 2
            nodes = nodes[level_start:level_start + level_size]
            next_level = []
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    combined = nodes[i] + nodes[i + 1]
                    next_level.append(double_sha256(combined))
                else:
                    next_level.append(nodes[i])
            level_start += level_size
            nodes = next_level
        
        return proof
    
    @staticmethod
    def verify_proof(leaf: bytes, proof: List[tuple], root: bytes) -> bool:
        """Verify a Merkle proof."""
        current = double_sha256(leaf) if len(leaf) != 32 else leaf
        
        for sibling, direction in proof:
            if direction == 'left':
                current = double_sha256(sibling + current)
            else:
                current = double_sha256(current + sibling)
        
        return current == root


def get_timestamp() -> float:
    """Get current Unix timestamp."""
    return time.time()


def calculate_difficulty_adjustment(
    actual_time: float,
    expected_time: float,
    current_difficulty: int,
    min_diff: int = 1,
    max_diff: int = 32
) -> int:
    """
    Calculate adjusted difficulty based on block time.
    If blocks are too fast, increase difficulty; if too slow, decrease.
    """
    ratio = expected_time / actual_time if actual_time > 0 else 1
    
    # Limit adjustment factor to prevent extreme swings
    ratio = max(0.25, min(4.0, ratio))
    
    new_difficulty = int(current_difficulty * ratio)
    return max(min_diff, min(max_diff, new_difficulty))


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hexadecimal string."""
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hexadecimal string to bytes."""
    return bytes.fromhex(hex_str)
