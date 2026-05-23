"""
Globex (GBX) Wallet Implementation
ECDSA key generation, signing, and address derivation using SECP256k1
"""

import os
import json
from typing import Optional, Tuple, Dict, Any
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from ecdsa.util import sigencode_der, sigdecode_der

from utils import sha256, ripemd160, hash_to_address, verify_address, double_sha256, bytes_to_hex, hex_to_bytes


class Wallet:
    """Globex wallet for managing ECDSA keys and addresses."""
    
    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize wallet with optional private key.
        If no private key is provided, a new one is generated.
        """
        if private_key:
            self.signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.signing_key = SigningKey.generate(curve=SECP256k1)
        
        self.verifying_key = self.signing_key.get_verifying_key()
        self.address = self._derive_address()
    
    def _derive_address(self) -> str:
        """Derive Globex address from public key."""
        # Get uncompressed public key (without prefix byte)
        pubkey_bytes = self.verifying_key.to_string()
        
        # SHA-256 then RIPEMD-160
        pubkey_hash = ripemd160(sha256(pubkey_bytes))
        
        # Convert to Base58 address
        return hash_to_address(pubkey_hash)
    
    def get_public_key(self) -> bytes:
        """Get the raw public key bytes."""
        return self.verifying_key.to_string()
    
    def get_private_key(self) -> bytes:
        """Get the raw private key bytes."""
        return self.signing_key.to_string()
    
    def sign_message(self, message: bytes) -> bytes:
        """Sign a message with the private key."""
        signature = self.signing_key.sign(message, sigencode=sigencode_der)
        return signature
    
    def sign_transaction(self, transaction_data: bytes) -> bytes:
        """Sign transaction data."""
        return self.sign_message(double_sha256(transaction_data))
    
    @staticmethod
    def verify_signature(public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Verify a signature using the public key."""
        try:
            verifying_key = VerifyingKey.from_string(public_key, curve=SECP256k1)
            return verifying_key.verify(signature, message, sigdecode=sigdecode_der)
        except Exception:
            return False
    
    @staticmethod
    def verify_transaction_signature(
        public_key: bytes,
        transaction_data: bytes,
        signature: bytes
    ) -> bool:
        """Verify a transaction signature."""
        return Wallet.verify_signature(public_key, double_sha256(transaction_data), signature)
    
    def save_to_file(self, filename: str, password: Optional[str] = None) -> None:
        """Save wallet to a JSON file."""
        wallet_data = {
            'address': self.address,
            'private_key': bytes_to_hex(self.get_private_key()),
            'public_key': bytes_to_hex(self.get_public_key())
        }
        
        # Simple encryption with password (XOR-based for lightweight implementation)
        if password:
            key = sha256(password.encode())
            encrypted_pk = bytes(a ^ b for a, b in zip(
                hex_to_bytes(wallet_data['private_key']),
                (key * ((len(wallet_data['private_key']) // 64) + 1))[:len(wallet_data['private_key']) // 2]
            ))
            wallet_data['private_key'] = bytes_to_hex(encrypted_pk)
            wallet_data['encrypted'] = True
        
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=2)
    
    @staticmethod
    def load_from_file(filename: str, password: Optional[str] = None) -> 'Wallet':
        """Load wallet from a JSON file."""
        with open(filename, 'r') as f:
            wallet_data = json.load(f)
        
        private_key_hex = wallet_data['private_key']
        
        if wallet_data.get('encrypted'):
            if not password:
                raise ValueError("Password required to decrypt wallet")
            
            key = sha256(password.encode())
            decrypted_pk = bytes(a ^ b for a, b in zip(
                hex_to_bytes(private_key_hex),
                (key * ((len(private_key_hex) // 64) + 1))[:len(private_key_hex) // 2]
            ))
            private_key_hex = bytes_to_hex(decrypted_pk)
        
        private_key = hex_to_bytes(private_key_hex)
        return Wallet(private_key=private_key)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export wallet data as dictionary."""
        return {
            'address': self.address,
            'public_key': bytes_to_hex(self.get_public_key()),
            # Never export private key in normal operations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], private_key: Optional[bytes] = None) -> 'Wallet':
        """Create wallet from dictionary (requires private key separately)."""
        if private_key:
            return cls(private_key=private_key)
        raise ValueError("Private key required to create wallet from dict")


def generate_wallet() -> Wallet:
    """Convenience function to generate a new wallet."""
    return Wallet()


def address_from_public_key(public_key: bytes) -> str:
    """Derive address from a raw public key."""
    pubkey_hash = ripemd160(sha256(public_key))
    return hash_to_address(pubkey_hash)
