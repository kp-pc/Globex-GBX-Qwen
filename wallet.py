"""
Globex (GBX) Wallet Implementation
Complete ECDSA key generation, signing, address derivation, and transaction management
Optimized for ARM devices (Raspberry Pi, mobile)
"""

import os
import json
import time
import hashlib
import secrets
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, asdict
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

from utils import (
    sha256, ripemd160, hash_to_address, verify_address,
    double_sha256, bytes_to_hex, hex_to_bytes, base58_encode, base58_decode
)
# Config imports removed - not needed for wallet module to avoid circular dependencies


# ============================================================================
# TRANSACTION DATA STRUCTURES
# ============================================================================

@dataclass
class TransactionInput:
    """Represents an input in a transaction (spending from a previous output)."""
    txid: str  # Transaction ID of the source transaction
    vout: int  # Output index in the source transaction
    amount: float  # Amount being spent
    script_sig: str  # Unlocking script (signature + public key)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionInput':
        return cls(**data)


@dataclass
class TransactionOutput:
    """Represents an output in a transaction (receiving funds)."""
    amount: float  # Amount in GBX
    address: str  # Recipient address
    script_pubkey: str  # Locking script (typically just the address)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransactionOutput':
        return cls(**data)


@dataclass
class Transaction:
    """Complete transaction structure."""
    txid: str
    version: int
    timestamp: float
    inputs: List[TransactionInput]
    outputs: List[TransactionOutput]
    locktime: int
    signature: str  # Hex-encoded signature
    public_key: str  # Hex-encoded public key of signer
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'txid': self.txid,
            'version': self.version,
            'timestamp': self.timestamp,
            'inputs': [i.to_dict() for i in self.inputs],
            'outputs': [o.to_dict() for o in self.outputs],
            'locktime': self.locktime,
            'signature': self.signature,
            'public_key': self.public_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        inputs = [TransactionInput.from_dict(i) for i in data['inputs']]
        outputs = [TransactionOutput.from_dict(o) for o in data['outputs']]
        return cls(
            txid=data['txid'],
            version=data['version'],
            timestamp=data['timestamp'],
            inputs=inputs,
            outputs=outputs,
            locktime=data['locktime'],
            signature=data['signature'],
            public_key=data['public_key']
        )
    
    def serialize(self) -> bytes:
        """Serialize transaction for signing."""
        data = f"{self.version}:{self.timestamp}:{self.locktime}:"
        data += "|".join([f"{i.txid}:{i.vout}:{i.amount}" for i in self.inputs])
        data += "||"
        data += "|".join([f"{o.amount}:{o.address}" for o in self.outputs])
        return data.encode()
    
    def get_hash(self) -> str:
        """Calculate transaction ID (double SHA-256 of serialized data)."""
        return bytes_to_hex(double_sha256(self.serialize()))


# ============================================================================
# UTXO MANAGEMENT
# ============================================================================

@dataclass
class UTXO:
    """Unspent Transaction Output."""
    txid: str
    vout: int
    amount: float
    address: str
    confirmed: bool = True
    block_height: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UTXO':
        return cls(**data)


class UTXOManager:
    """Manages UTXOs for a wallet."""
    
    def __init__(self):
        self.utxos: Dict[str, UTXO] = {}  # Key: txid:vout
    
    def add_utxo(self, utxo: UTXO) -> None:
        """Add a UTXO to the manager."""
        key = f"{utxo.txid}:{utxo.vout}"
        self.utxos[key] = utxo
    
    def remove_utxo(self, txid: str, vout: int) -> bool:
        """Remove a UTXO when it's spent."""
        key = f"{txid}:{vout}"
        if key in self.utxos:
            del self.utxos[key]
            return True
        return False
    
    def get_balance(self, address: str, confirmed_only: bool = True) -> float:
        """Calculate total balance for an address."""
        total = 0.0
        for utxo in self.utxos.values():
            if utxo.address == address:
                if confirmed_only and not utxo.confirmed:
                    continue
                total += utxo.amount
        return total
    
    def get_spendable_utxos(self, address: str, min_amount: float = 0) -> List[UTXO]:
        """Get UTXOs that can be spent."""
        spendable = []
        for utxo in self.utxos.values():
            if utxo.address == address and utxo.confirmed and utxo.amount >= min_amount:
                spendable.append(utxo)
        # Sort by amount (smallest first for better privacy)
        spendable.sort(key=lambda x: x.amount)
        return spendable
    
    def select_utxos(self, address: str, target_amount: float, fee: float) -> Optional[List[UTXO]]:
        """Select UTXOs to cover target amount + fee using greedy algorithm."""
        total_needed = target_amount + fee
        utxos = self.get_spendable_utxos(address)
        
        selected = []
        current_sum = 0.0
        
        # First pass: find exact or larger UTXO
        for utxo in utxos:
            if utxo.amount >= total_needed:
                return [utxo]
        
        # Second pass: accumulate smaller UTXOs
        for utxo in utxos:
            selected.append(utxo)
            current_sum += utxo.amount
            if current_sum >= total_needed:
                return selected
        
        return None  # Insufficient funds
    
    def to_dict(self) -> Dict[str, Any]:
        """Export UTXO set."""
        return {key: utxo.to_dict() for key, utxo in self.utxos.items()}
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Import UTXO set."""
        for key, utxo_data in data.items():
            self.utxos[key] = UTXO.from_dict(utxo_data)


# ============================================================================
# WALLET CLASS
# ============================================================================

class Wallet:
    """
    Globex wallet for managing ECDSA keys, addresses, and transactions.
    Optimized for ARM devices with efficient cryptographic operations.
    """
    
    VERSION_BYTE = 0x26  # Custom version byte for Globex addresses (prefix 'L')
    
    def __init__(self, private_key: Optional[bytes] = None, label: str = ""):
        """
        Initialize wallet with optional private key.
        If no private key is provided, a new one is generated.
        
        Args:
            private_key: Optional 32-byte private key
            label: Human-readable label for the wallet
        """
        self.label = label
        self.created_at = time.time()
        self.utxo_manager = UTXOManager()
        
        if private_key:
            if len(private_key) != 32:
                raise ValueError("Private key must be 32 bytes")
            self.signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.signing_key = SigningKey.generate(curve=SECP256k1)
        
        self.verifying_key = self.signing_key.get_verifying_key()
        self.address = self._derive_address()
    
    def _derive_address(self) -> str:
        """
        Derive Globex address from public key.
        Process: SHA-256(PubKey) → RIPEMD-160 → Version Byte → Checksum → Base58
        """
        # Get uncompressed public key (64 bytes, no prefix)
        pubkey_bytes = self.verifying_key.to_string()
        
        # Step 1: SHA-256 hash of public key
        pubkey_hash_sha256 = sha256(pubkey_bytes)
        
        # Step 2: RIPEMD-160 hash of SHA-256 result
        pubkey_hash = ripemd160(pubkey_hash_sha256)
        
        # Step 3: Add version byte
        versioned_payload = bytes([self.VERSION_BYTE]) + pubkey_hash
        
        # Step 4: Double SHA-256 checksum
        checksum = double_sha256(versioned_payload)[:4]
        
        # Step 5: Base58 encode
        return base58_encode(versioned_payload + checksum)
    
    def get_public_key(self) -> bytes:
        """Get the raw public key bytes (64 bytes, uncompressed)."""
        return self.verifying_key.to_string()
    
    def get_public_key_hex(self) -> str:
        """Get the public key as hex string."""
        return bytes_to_hex(self.get_public_key())
    
    def get_private_key(self) -> bytes:
        """Get the raw private key bytes (32 bytes)."""
        return self.signing_key.to_string()
    
    def get_private_key_hex(self) -> str:
        """Get the private key as hex string."""
        return bytes_to_hex(self.get_private_key())
    
    def get_private_key_wif(self) -> str:
        """
        Get private key in WIF (Wallet Import Format).
        Similar to Bitcoin WIF but with Globex version byte.
        """
        # Add version byte
        extended_key = bytes([0x80]) + self.get_private_key()
        
        # Add checksum
        checksum = double_sha256(extended_key)[:4]
        
        # Base58 encode
        return base58_encode(extended_key + checksum)
    
    def sign_message(self, message: bytes) -> bytes:
        """
        Sign arbitrary message with ECDSA.
        Uses deterministic signatures (RFC 6979) via ecdsa library.
        """
        signature = self.signing_key.sign(message, sigencode=sigencode_der)
        return signature
    
    def sign_transaction(self, transaction: Transaction) -> bytes:
        """
        Sign a transaction.
        Signs the double SHA-256 hash of the serialized transaction.
        """
        tx_hash = double_sha256(transaction.serialize())
        return self.sign_message(tx_hash)
    
    def create_transaction(
        self,
        recipient_address: str,
        amount: float,
        fee: float,
        utxos: Optional[List[UTXO]] = None
    ) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            recipient_address: Destination address
            amount: Amount to send in GBX
            fee: Transaction fee in GBX
            utxos: Optional list of UTXOs to spend (auto-selected if None)
        
        Returns:
            Signed Transaction object
        
        Raises:
            ValueError: If insufficient funds or invalid address
        """
        # Validate recipient address
        if not verify_address(recipient_address):
            raise ValueError(f"Invalid recipient address: {recipient_address}")
        
        # Select UTXOs if not provided
        if utxos is None:
            utxos = self.utxo_manager.select_utxos(self.address, amount, fee)
            if utxos is None:
                raise ValueError(
                    f"Insufficient funds. Need {amount + fee:.8f} GBX, "
                    f"have {self.utxo_manager.get_balance(self.address):.8f} GBX"
                )
        
        # Calculate total input and change
        total_input = sum(u.amount for u in utxos)
        change = total_input - amount - fee
        
        if change < 0:
            raise ValueError("Negative change - insufficient funds after fee")
        
        # Create inputs
        inputs = [
            TransactionInput(
                txid=u.txid,
                vout=u.vout,
                amount=u.amount,
                script_sig=""  # Will be filled after signing
            )
            for u in utxos
        ]
        
        # Create outputs
        outputs = [
            TransactionOutput(
                amount=amount,
                address=recipient_address,
                script_pubkey=f"DUP HASH160 {ripemd160(sha256(hex_to_bytes(self.address_to_pubkey(recipient_address))))} EQUALVERIFY CHECKSIG"
            )
        ]
        
        # Add change output if significant
        if change > 0.00000001:  # Dust threshold
            outputs.append(TransactionOutput(
                amount=change,
                address=self.address,
                script_pubkey=f"DUP HASH160 {ripemd160(sha256(self.get_public_key()))} EQUALVERIFY CHECKSIG"
            ))
        
        # Create unsigned transaction
        tx = Transaction(
            txid="",
            version=1,
            timestamp=time.time(),
            inputs=inputs,
            outputs=outputs,
            locktime=0,
            signature="",
            public_key=self.get_public_key_hex()
        )
        
        # Calculate txid
        tx.txid = tx.get_hash()
        
        # Sign transaction
        signature = self.sign_transaction(tx)
        tx.signature = bytes_to_hex(signature)
        
        # Create scriptSig (simplified for Globex)
        for inp in tx.inputs:
            inp.script_sig = f"SIGNATURE:{tx.signature} PUBKEY:{tx.public_key}"
        
        # Recalculate txid after adding signatures
        tx.txid = tx.get_hash()
        
        return tx
    
    @staticmethod
    def verify_transaction_signature(transaction: Transaction) -> bool:
        """
        Verify a transaction's signature.
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            public_key = hex_to_bytes(transaction.public_key)
            signature = hex_to_bytes(transaction.signature)
            
            # Verify against double SHA-256 of serialized transaction
            tx_hash = double_sha256(transaction.serialize())
            
            verifying_key = VerifyingKey.from_string(public_key, curve=SECP256k1)
            return verifying_key.verify(signature, tx_hash, sigdecode=sigdecode_der)
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False
    
    @staticmethod
    def verify_signature(public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify an arbitrary signature."""
        try:
            verifying_key = VerifyingKey.from_string(public_key, curve=SECP256k1)
            return verifying_key.verify(signature, message, sigdecode=sigdecode_der)
        except Exception:
            return False
    
    def address_to_pubkey(self, address: str) -> bytes:
        """Extract public key hash from address (for script creation)."""
        decoded = base58_decode(address)
        if len(decoded) != 25:
            raise ValueError("Invalid address length")
        # Skip version byte and checksum
        return decoded[1:21]
    
    def save_to_file(self, filename: str, password: Optional[str] = None) -> None:
        """
        Save wallet to encrypted JSON file.
        
        Args:
            filename: Path to save wallet file
            password: Optional password for encryption
        """
        wallet_data = {
            'version': 1,
            'label': self.label,
            'address': self.address,
            'created_at': self.created_at,
            'private_key': self.get_private_key_hex(),
            'public_key': self.get_public_key_hex(),
            'encrypted': False
        }
        
        # Encrypt with AES-like XOR cipher (lightweight for ARM)
        if password:
            # Derive encryption key from password
            key_material = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt=b'globex_wallet_salt_v1',
                iterations=10000,
                dklen=32
            )
            
            # XOR encrypt private key
            private_key_bytes = self.get_private_key()
            encrypted_pk = bytes(a ^ b for a, b in zip(private_key_bytes, key_material))
            wallet_data['private_key'] = bytes_to_hex(encrypted_pk)
            wallet_data['encrypted'] = True
            wallet_data['salt'] = 'globex_wallet_salt_v1'
        
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        # Set restrictive file permissions
        os.chmod(filename, 0o600)
    
    @staticmethod
    def load_from_file(filename: str, password: Optional[str] = None) -> 'Wallet':
        """
        Load wallet from JSON file.
        
        Args:
            filename: Path to wallet file
            password: Password if wallet is encrypted
        
        Returns:
            Loaded Wallet object
        """
        with open(filename, 'r') as f:
            wallet_data = json.load(f)
        
        private_key_hex = wallet_data['private_key']
        
        if wallet_data.get('encrypted'):
            if not password:
                raise ValueError("Password required to decrypt wallet")
            
            # Derive decryption key
            salt = wallet_data.get('salt', 'globex_wallet_salt_v1').encode()
            key_material = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt=salt,
                iterations=10000,
                dklen=32
            )
            
            # XOR decrypt private key
            encrypted_pk = hex_to_bytes(private_key_hex)
            decrypted_pk = bytes(a ^ b for a, b in zip(encrypted_pk, key_material))
            private_key_hex = bytes_to_hex(decrypted_pk)
        
        private_key = hex_to_bytes(private_key_hex)
        label = wallet_data.get('label', '')
        
        wallet = Wallet(private_key=private_key, label=label)
        wallet.created_at = wallet_data.get('created_at', time.time())
        
        return wallet
    
    def to_dict(self, include_private: bool = False) -> Dict[str, Any]:
        """
        Export wallet data as dictionary.
        
        Args:
            include_private: If True, include private key (use with caution!)
        """
        data = {
            'address': self.address,
            'public_key': self.get_public_key_hex(),
            'label': self.label,
            'created_at': self.created_at,
            'balance': self.utxo_manager.get_balance(self.address)
        }
        
        if include_private:
            data['private_key'] = self.get_private_key_hex()
            data['warning'] = 'NEVER share your private key!'
        
        return data
    
    def update_balance(self, blockchain_db=None) -> float:
        """
        Update wallet balance by scanning blockchain.
        
        Args:
            blockchain_db: SQLite database connection
        
        Returns:
            Updated balance
        """
        if blockchain_db is None:
            return self.utxo_manager.get_balance(self.address)
        
        # This would integrate with core.py to scan the blockchain
        # For now, return cached balance
        return self.utxo_manager.get_balance(self.address)
    
    def __str__(self) -> str:
        """Human-readable wallet representation."""
        return (
            f"Globex Wallet\n"
            f"  Address: {self.address}\n"
            f"  Label: {self.label or 'Unnamed'}\n"
            f"  Balance: {self.utxo_manager.get_balance(self.address):.8f} GBX\n"
            f"  Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.created_at))}"
        )


# ============================================================================
# MULTI-SIGNATURE WALLET SUPPORT
# ============================================================================

class MultiSigWallet:
    """
    Multi-signature wallet for development fund and secure storage.
    Supports M-of-N signature schemes.
    """
    
    def __init__(self, required_signatures: int, public_keys: List[bytes]):
        """
        Initialize multi-sig wallet.
        
        Args:
            required_signatures: Number of signatures needed (M)
            public_keys: List of N public keys
        """
        if required_signatures > len(public_keys):
            raise ValueError("Required signatures cannot exceed total keys")
        if required_signatures < 1:
            raise ValueError("At least one signature required")
        
        self.m = required_signatures
        self.public_keys = public_keys
        self.n = len(public_keys)
        self.address = self._derive_multisig_address()
        self.pending_signatures: Dict[str, List[bytes]] = {}
    
    def _derive_multisig_address(self) -> str:
        """Derive multi-sig address from public keys."""
        # Sort public keys for deterministic address
        sorted_keys = sorted(self.public_keys)
        
        # Concatenate all public keys
        combined = b''.join(sorted_keys)
        
        # Hash to create address
        pubkey_hash = ripemd160(sha256(combined))
        
        # Use different version byte for multi-sig
        versioned_payload = bytes([0x27]) + pubkey_hash  # 0x27 for multi-sig
        checksum = double_sha256(versioned_payload)[:4]
        
        return base58_encode(versioned_payload + checksum)
    
    def sign_transaction(self, wallet: Wallet, transaction: Transaction) -> bytes:
        """Sign a transaction with a single wallet."""
        return wallet.sign_transaction(transaction)
    
    def collect_signature(
        self,
        txid: str,
        signature: bytes,
        public_key: bytes
    ) -> Tuple[bool, int]:
        """
        Collect a signature for a transaction.
        
        Returns:
            Tuple of (success, total_signatures_collected)
        """
        if public_key not in self.public_keys:
            return False, 0
        
        if txid not in self.pending_signatures:
            self.pending_signatures[txid] = []
        
        # Avoid duplicate signatures
        if signature not in self.pending_signatures[txid]:
            self.pending_signatures[txid].append(signature)
        
        return True, len(self.pending_signatures[txid])
    
    def has_enough_signatures(self, txid: str) -> bool:
        """Check if transaction has enough signatures."""
        return len(self.pending_signatures.get(txid, [])) >= self.m
    
    def get_address(self) -> str:
        """Get multi-sig wallet address."""
        return self.address
    
    def to_dict(self) -> Dict[str, Any]:
        """Export multi-sig wallet info."""
        return {
            'address': self.address,
            'required_signatures': self.m,
            'total_keys': self.n,
            'public_keys': [bytes_to_hex(pk) for pk in self.public_keys]
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def generate_wallet(label: str = "") -> Wallet:
    """Generate a new random wallet."""
    return Wallet(label=label)


def generate_deterministic_wallet(seed: bytes) -> Wallet:
    """
    Generate a deterministic wallet from a seed.
    Useful for reproducible wallet generation.
    """
    if len(seed) < 16:
        raise ValueError("Seed must be at least 16 bytes")
    
    # Derive private key from seed using HMAC-SHA512
    derived = hashlib.pbkdf2_hmac(
        'sha512',
        seed,
        salt=b'globex_deterministic_seed',
        iterations=2048,
        dklen=32
    )
    
    return Wallet(private_key=derived[:32])


def create_random_seed() -> bytes:
    """Generate a cryptographically secure random seed."""
    return secrets.token_bytes(32)


def seed_to_mnemonic(seed: bytes) -> str:
    """
    Convert seed to simple mnemonic (not BIP39, simplified for Globex).
    Returns space-separated words from a wordlist.
    """
    # Simplified wordlist (first 256 words of common crypto wordlists)
    wordlist = [
        'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
        'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
        'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
        'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
        'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'age', 'agent',
        'agree', 'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album',
        'alcohol', 'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone',
        'alpha', 'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among',
        'amount', 'amused', 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry',
        'animal', 'ankle', 'announce', 'annual', 'another', 'answer', 'antenna', 'antique',
        'anxiety', 'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april',
        'arch', 'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor',
        'army', 'around', 'arrange', 'arrest', 'arrive', 'arrow', 'art', 'artefact',
        'artist', 'artwork', 'ask', 'aspect', 'assault', 'asset', 'assist', 'assume',
        'asthma', 'athlete', 'atom', 'attack', 'attend', 'attitude', 'attract', 'auction',
        'audit', 'august', 'aunt', 'author', 'auto', 'autumn', 'average', 'avocado',
        'avoid', 'awake', 'aware', 'away', 'awesome', 'awful', 'awkward', 'axis',
        'baby', 'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony', 'ball',
        'bamboo', 'banana', 'banner', 'bar', 'barely', 'bargain', 'barrel', 'base',
        'basic', 'basket', 'battle', 'beach', 'bean', 'beauty', 'because', 'become',
        'beef', 'before', 'begin', 'behave', 'behind', 'believe', 'below', 'belt',
        'bench', 'benefit', 'best', 'betray', 'better', 'between', 'beyond', 'bicycle',
        'bid', 'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black',
        'blade', 'blame', 'blanket', 'blast', 'bleak', 'bless', 'blind', 'blood',
        'blossom', 'blouse', 'blue', 'blur', 'blush', 'board', 'boat', 'body',
        'boil', 'bomb', 'bone', 'bonus', 'book', 'boost', 'border', 'boring',
        'borrow', 'boss', 'bottom', 'bounce', 'box', 'boy', 'bracket', 'brain',
        'brand', 'brass', 'brave', 'bread', 'breeze', 'brick', 'bridge', 'brief',
        'bright', 'bring', 'brisk', 'broccoli', 'broken', 'bronze', 'broom', 'brother',
        'brown', 'brush', 'bubble', 'buddy', 'budget', 'buffalo', 'build', 'bulb',
        'bulk', 'bullet', 'bundle', 'bunker', 'burden', 'burger', 'burst', 'bus',
        'business', 'busy', 'butter', 'buyer', 'buzz', 'cabbage', 'cabin', 'cable'
    ]
    
    words = []
    for byte in seed[:16]:  # Use first 16 bytes for 16 words
        words.append(wordlist[byte % len(wordlist)])
    
    return ' '.join(words)


def mnemonic_to_seed(mnemonic: str) -> bytes:
    """Convert mnemonic back to seed."""
    wordlist = [
        'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
        'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
        'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
        'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
        'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'age', 'agent',
        'agree', 'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album',
        'alcohol', 'alert', 'alien', 'all', 'alley', 'allow', 'almost', 'alone',
        'alpha', 'already', 'also', 'alter', 'always', 'amateur', 'amazing', 'among',
        'amount', 'amused', 'analyst', 'anchor', 'ancient', 'anger', 'angle', 'angry',
        'animal', 'ankle', 'announce', 'annual', 'another', 'answer', 'antenna', 'antique',
        'anxiety', 'any', 'apart', 'apology', 'appear', 'apple', 'approve', 'april',
        'arch', 'arctic', 'area', 'arena', 'argue', 'arm', 'armed', 'armor',
        'army', 'around', 'arrange', 'arrest', 'arrive', 'arrow', 'art', 'artefact',
        'artist', 'artwork', 'ask', 'aspect', 'assault', 'asset', 'assist', 'assume',
        'asthma', 'athlete', 'atom', 'attack', 'attend', 'attitude', 'attract', 'auction',
        'audit', 'august', 'aunt', 'author', 'auto', 'autumn', 'average', 'avocado',
        'avoid', 'awake', 'aware', 'away', 'awesome', 'awful', 'awkward', 'axis',
        'baby', 'bachelor', 'bacon', 'badge', 'bag', 'balance', 'balcony', 'ball',
        'bamboo', 'banana', 'banner', 'bar', 'barely', 'bargain', 'barrel', 'base',
        'basic', 'basket', 'battle', 'beach', 'bean', 'beauty', 'because', 'become',
        'beef', 'before', 'begin', 'behave', 'behind', 'believe', 'below', 'belt',
        'bench', 'benefit', 'best', 'betray', 'better', 'between', 'beyond', 'bicycle',
        'bid', 'bike', 'bind', 'biology', 'bird', 'birth', 'bitter', 'black',
        'blade', 'blame', 'blanket', 'blast', 'bleak', 'bless', 'blind', 'blood',
        'blossom', 'blouse', 'blue', 'blur', 'blush', 'board', 'boat', 'body',
        'boil', 'bomb', 'bone', 'bonus', 'book', 'boost', 'border', 'boring',
        'borrow', 'boss', 'bottom', 'bounce', 'box', 'boy', 'bracket', 'brain',
        'brand', 'brass', 'brave', 'bread', 'breeze', 'brick', 'bridge', 'brief',
        'bright', 'bring', 'brisk', 'broccoli', 'broken', 'bronze', 'broom', 'brother',
        'brown', 'brush', 'bubble', 'buddy', 'budget', 'buffalo', 'build', 'bulb',
        'bulk', 'bullet', 'bundle', 'bunker', 'burden', 'burger', 'burst', 'bus',
        'business', 'busy', 'butter', 'buyer', 'buzz', 'cabbage', 'cabin', 'cable'
    ]
    
    words = mnemonic.split()
    seed_bytes = []
    
    for word in words:
        if word in wordlist:
            idx = wordlist.index(word)
            seed_bytes.append(idx % 256)
        else:
            raise ValueError(f"Unknown word in mnemonic: {word}")
    
    return bytes(seed_bytes)


def import_wallet_from_wif(wif: str) -> Wallet:
    """Import wallet from WIF (Wallet Import Format)."""
    try:
        decoded = base58_decode(wif)
        
        # Verify checksum
        payload = decoded[:-4]
        checksum = decoded[-4:]
        
        if double_sha256(payload)[:4] != checksum:
            raise ValueError("Invalid WIF checksum")
        
        # Extract private key (skip version byte)
        private_key = payload[1:33]
        
        return Wallet(private_key=private_key)
    except Exception as e:
        raise ValueError(f"Failed to import WIF: {e}")


# ============================================================================
# WALLET MANAGER (Multiple Wallets)
# ============================================================================

class WalletManager:
    """Manage multiple wallets in a single interface."""
    
    def __init__(self, wallets_dir: str = "./wallets"):
        self.wallets_dir = wallets_dir
        self.wallets: Dict[str, Wallet] = {}
        
        # Create wallets directory if it doesn't exist
        os.makedirs(wallets_dir, exist_ok=True)
    
    def create_wallet(self, label: str = "", password: Optional[str] = None) -> Wallet:
        """Create and save a new wallet."""
        wallet = generate_wallet(label=label)
        filename = os.path.join(self.wallets_dir, f"{label or wallet.address[:8]}.json")
        wallet.save_to_file(filename, password=password)
        self.wallets[wallet.address] = wallet
        return wallet
    
    def load_wallet(self, filename: str, password: Optional[str] = None) -> Wallet:
        """Load a wallet from file."""
        if not os.path.isabs(filename):
            filename = os.path.join(self.wallets_dir, filename)
        
        wallet = Wallet.load_from_file(filename, password=password)
        self.wallets[wallet.address] = wallet
        return wallet
    
    def list_wallets(self) -> List[Dict[str, Any]]:
        """List all available wallets."""
        wallet_files = []
        for f in os.listdir(self.wallets_dir):
            if f.endswith('.json'):
                filepath = os.path.join(self.wallets_dir, f)
                try:
                    with open(filepath, 'r') as wf:
                        data = json.load(wf)
                        wallet_files.append({
                            'filename': f,
                            'address': data.get('address', 'Unknown'),
                            'label': data.get('label', ''),
                            'encrypted': data.get('encrypted', False)
                        })
                except Exception:
                    continue
        return wallet_files
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """Get a loaded wallet by address."""
        return self.wallets.get(address)
    
    def delete_wallet(self, address: str) -> bool:
        """Delete a wallet from memory and disk."""
        if address in self.wallets:
            wallet = self.wallets[address]
            filename = os.path.join(self.wallets_dir, f"{wallet.label or address[:8]}.json")
            if os.path.exists(filename):
                os.remove(filename)
            del self.wallets[address]
            return True
        return False
