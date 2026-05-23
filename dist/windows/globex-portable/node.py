"""
Globex (GBX) Node Implementation
REST API server with Flask for peer-to-peer communication
"""

import json
import threading
import time
from typing import List, Dict, Optional, Any
from flask import Flask, request, jsonify

from core import Blockchain, Transaction, Block
from wallet import Wallet, generate_wallet
from config import API_PORT, P2P_PORT, MIN_TRANSACTION_FEE


class GlobexNode:
    """Globex blockchain node with REST API."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = API_PORT):
        self.host = host
        self.port = port
        self.blockchain = Blockchain()
        self.peers: List[str] = []
        self.wallet: Optional[Wallet] = None
        self.mining = False
        self.mining_thread: Optional[threading.Thread] = None
        
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask REST API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                'status': 'healthy',
                'network': 'Globex',
                'port': self.port,
                'chain_length': self.blockchain.get_chain_length(),
                'mempool_size': self.blockchain.mempool.size(),
                'peers': len(self.peers)
            })
        
        @self.app.route('/mine', methods=['POST'])
        def mine():
            """Mine a new block."""
            data = request.get_json() or {}
            miner_address = data.get('address') or (self.wallet.address if self.wallet else None)
            
            if not miner_address:
                return jsonify({'error': 'Miner address required'}), 400
            
            block = self.blockchain.mine_block(miner_address)
            if block:
                # Broadcast to peers
                self._broadcast_block(block)
                
                return jsonify({
                    'success': True,
                    'message': 'Block mined successfully',
                    'block': {
                        'index': block.index,
                        'hash': block.block_hash,
                        'transactions': len(block.transactions),
                        'reward': self.blockchain._calculate_block_reward(block.index),
                        'timestamp': block.timestamp
                    }
                })
            
            return jsonify({'error': 'Failed to mine block'}), 500
        
        @self.app.route('/mine/start', methods=['POST'])
        def start_mining():
            """Start continuous mining."""
            data = request.get_json() or {}
            miner_address = data.get('address') or (self.wallet.address if self.wallet else None)
            
            if not miner_address:
                return jsonify({'error': 'Miner address required'}), 400
            
            if self.mining:
                return jsonify({'message': 'Already mining'})
            
            self.mining = True
            
            def mining_loop():
                while self.mining:
                    block = self.blockchain.mine_block(miner_address)
                    if block:
                        self._broadcast_block(block)
                        print(f"Mined block {block.index} with hash {block.block_hash[:16]}...")
                    time.sleep(1)
            
            self.mining_thread = threading.Thread(target=mining_loop, daemon=True)
            self.mining_thread.start()
            
            return jsonify({'success': True, 'message': 'Mining started'})
        
        @self.app.route('/mine/stop', methods=['POST'])
        def stop_mining():
            """Stop continuous mining."""
            self.mining = False
            return jsonify({'success': True, 'message': 'Mining stopped'})
        
        @self.app.route('/transactions/new', methods=['POST'])
        def new_transaction():
            """Create and broadcast a new transaction."""
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            sender_address = data.get('sender_address')
            recipient = data.get('recipient')
            amount = data.get('amount')
            fee = data.get('fee', MIN_TRANSACTION_FEE)
            signature = data.get('signature')
            public_key = data.get('public_key')
            
            if not all([sender_address, recipient, amount]):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # If we have the wallet, create the transaction
            if self.wallet and self.wallet.address == sender_address:
                tx, msg = self.blockchain.create_transaction(
                    self.wallet, recipient, amount, fee
                )
                if tx:
                    success, result = self.blockchain.add_transaction(tx)
                    if success:
                        self._broadcast_transaction(tx)
                        return jsonify({
                            'success': True,
                            'message': result,
                            'transaction': {
                                'tx_id': tx.tx_id,
                                'from': sender_address,
                                'to': recipient,
                                'amount': amount,
                                'fee': fee
                            }
                        })
                    return jsonify({'error': result}), 400
                return jsonify({'error': msg}), 400
            
            # Otherwise, accept a pre-signed transaction
            inputs = data.get('inputs', [])
            outputs = [{'address': recipient, 'amount': amount}]
            
            tx = Transaction(
                version=1,
                inputs=inputs,
                outputs=outputs,
                timestamp=time.time(),
                fee=fee,
                signature=signature or "",
                public_key=public_key or ""
            )
            tx.tx_id = tx.compute_tx_id()
            
            success, msg = self.blockchain.add_transaction(tx)
            if success:
                self._broadcast_transaction(tx)
                return jsonify({
                    'success': True,
                    'message': msg,
                    'transaction': {'tx_id': tx.tx_id}
                })
            
            return jsonify({'error': msg}), 400
        
        @self.app.route('/transactions/pending', methods=['GET'])
        def pending_transactions():
            """Get pending transactions in mempool."""
            txs = self.blockchain.mempool.get_transactions()
            return jsonify({
                'count': len(txs),
                'transactions': [
                    {
                        'tx_id': tx.tx_id,
                        'fee': tx.fee,
                        'timestamp': tx.timestamp
                    }
                    for tx in txs
                ]
            })
        
        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            """Get the full blockchain."""
            chain_data = [block.to_dict() for block in self.blockchain.chain]
            return jsonify({
                'length': len(chain_data),
                'chain': chain_data
            })
        
        @self.app.route('/chain/validate', methods=['GET'])
        def validate_chain():
            """Validate the blockchain."""
            valid, msg = self.blockchain.validate_chain()
            return jsonify({
                'valid': valid,
                'message': msg,
                'length': self.blockchain.get_chain_length()
            })
        
        @self.app.route('/chain/latest', methods=['GET'])
        def get_latest_block():
            """Get the latest block."""
            block = self.blockchain.get_latest_block()
            if block:
                return jsonify({
                    'block': block.to_dict()
                })
            return jsonify({'error': 'No blocks yet'}), 404
        
        @self.app.route('/balance/<address>', methods=['GET'])
        def get_balance(address):
            """Get balance for an address."""
            balance = self.blockchain.get_balance(address)
            return jsonify({
                'address': address,
                'balance': balance,
                'symbol': 'GBX'
            })
        
        @self.app.route('/nodes/register', methods=['POST'])
        def register_nodes():
            """Register new peer nodes."""
            data = request.get_json() or {}
            nodes = data.get('nodes', [])
            
            if not nodes:
                return jsonify({'error': 'No nodes provided'}), 400
            
            added = []
            for node in nodes:
                if node not in self.peers:
                    self.peers.append(node)
                    added.append(node)
            
            return jsonify({
                'success': True,
                'message': f'{len(added)} nodes registered',
                'total_peers': len(self.peers),
                'peers': self.peers
            })
        
        @self.app.route('/nodes/list', methods=['GET'])
        def list_nodes():
            """List all known peer nodes."""
            return jsonify({
                'peers': self.peers,
                'count': len(self.peers)
            })
        
        @self.app.route('/nodes/resolve', methods=['POST'])
        def resolve_conflicts():
            """Resolve conflicts using longest chain consensus."""
            replaced = False
            
            for peer_url in self.peers:
                try:
                    import urllib.request
                    req = urllib.request.Request(f"{peer_url}/chain")
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = json.loads(response.read().decode())
                    
                    if data.get('length', 0) > self.blockchain.get_chain_length():
                        chain = data.get('chain', [])
                        blocks = [Block.from_dict(b) for b in chain]
                        
                        if self.blockchain.resolve_conflicts(blocks):
                            replaced = True
                except Exception as e:
                    continue
            
            if replaced:
                return jsonify({
                    'success': True,
                    'message': 'Chain was replaced with longer valid chain',
                    'new_length': self.blockchain.get_chain_length()
                })
            
            return jsonify({
                'success': False,
                'message': 'Current chain is the longest valid chain'
            })
        
        @self.app.route('/wallet/create', methods=['POST'])
        def create_wallet():
            """Create a new wallet."""
            self.wallet = generate_wallet()
            return jsonify({
                'success': True,
                'wallet': {
                    'address': self.wallet.address,
                    'public_key': self.wallet.get_public_key().hex()
                },
                'warning': 'Save your private key securely!'
            })
        
        @self.app.route('/wallet/import', methods=['POST'])
        def import_wallet():
            """Import an existing wallet."""
            data = request.get_json()
            private_key = data.get('private_key')
            
            if not private_key:
                return jsonify({'error': 'Private key required'}), 400
            
            try:
                if len(private_key) == 64:
                    pk_bytes = bytes.fromhex(private_key)
                else:
                    pk_bytes = private_key.encode()
                
                self.wallet = Wallet(private_key=pk_bytes)
                return jsonify({
                    'success': True,
                    'wallet': {
                        'address': self.wallet.address,
                        'public_key': self.wallet.get_public_key().hex()
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/wallet/export', methods=['GET'])
        def export_wallet():
            """Export current wallet info."""
            if not self.wallet:
                return jsonify({'error': 'No wallet loaded'}), 404
            
            return jsonify({
                'address': self.wallet.address,
                'public_key': self.wallet.get_public_key().hex()
            })
        
        @self.app.route('/stake/register', methods=['POST'])
        def register_validator():
            """Register as a PoS validator."""
            data = request.get_json() or {}
            address = data.get('address') or (self.wallet.address if self.wallet else None)
            stake_amount = data.get('amount', 1000)
            
            if not address:
                return jsonify({'error': 'Address required'}), 400
            
            current_block = self.blockchain.get_chain_length()
            success = self.blockchain.stake_manager.register_validator(
                address, stake_amount, 100, current_block
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Validator registered',
                    'address': address,
                    'stake': stake_amount
                })
            
            return jsonify({'error': 'Failed to register validator'}), 400
        
        @self.app.route('/stake/validators', methods=['GET'])
        def get_validators():
            """Get all registered validators."""
            validators = self.blockchain.stake_manager.get_validators()
            return jsonify({
                'count': len(validators),
                'validators': validators
            })
        
        @self.app.route('/stake/mine', methods=['POST'])
        def mine_pos():
            """Mine a block using Proof of Stake."""
            data = request.get_json() or {}
            validator_address = data.get('address') or (self.wallet.address if self.wallet else None)
            stake_amount = data.get('stake_amount', 1000)
            
            if not validator_address:
                return jsonify({'error': 'Validator address required'}), 400
            
            block = self.blockchain.mine_pos_block(validator_address, stake_amount)
            if block:
                self._broadcast_block(block)
                return jsonify({
                    'success': True,
                    'message': 'PoS block created',
                    'block': {
                        'index': block.index,
                        'hash': block.block_hash,
                        'validator': block.validator
                    }
                })
            
            return jsonify({'error': 'Failed to create PoS block. Check validator registration.'}), 400
        
        @self.app.route('/devfund/status', methods=['GET'])
        def dev_fund_status():
            """Get development fund status."""
            current_block = self.blockchain.get_chain_length()
            status = self.blockchain.dev_fund_manager.get_status(current_block)
            return jsonify(status)
        
        @self.app.route('/devfund/propose', methods=['POST'])
        def propose_dev_transaction():
            """Propose a development fund transaction."""
            data = request.get_json() or {}
            amount = data.get('amount')
            recipients = data.get('recipients', [])
            
            if not amount or not recipients:
                return jsonify({'error': 'Amount and recipients required'}), 400
            
            import hashlib
            tx_id = hashlib.sha256(json.dumps(data).encode()).hexdigest()[:16]
            current_block = self.blockchain.get_chain_length()
            
            proposal = self.blockchain.dev_fund_manager.propose_transaction(
                tx_id, amount, recipients, current_block
            )
            
            return jsonify({
                'success': True,
                'proposal': proposal
            })
        
        @self.app.route('/devfund/sign', methods=['POST'])
        def sign_dev_transaction():
            """Sign a development fund transaction."""
            data = request.get_json() or {}
            tx_id = data.get('tx_id')
            signer_address = data.get('signer_address')
            
            if not tx_id or not signer_address:
                return jsonify({'error': 'tx_id and signer_address required'}), 400
            
            success = self.blockchain.dev_fund_manager.sign_transaction(tx_id, signer_address)
            
            if success:
                return jsonify({'success': True, 'message': 'Transaction signed'})
            
            return jsonify({'error': 'Failed to sign. Check signer authorization.'}), 400
        
        @self.app.route('/checkpoint/latest', methods=['GET'])
        def get_latest_checkpoint():
            """Get the latest finalized checkpoint."""
            cursor = self.blockchain.db.cursor()
            cursor.execute('''
                SELECT block_height, block_hash, finalized FROM checkpoints 
                ORDER BY block_height DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return jsonify({
                    'checkpoint': {
                        'block_height': row[0],
                        'block_hash': row[1],
                        'finalized': bool(row[2])
                    }
                })
            
            return jsonify({'message': 'No checkpoints yet'})
    
    def _broadcast_transaction(self, tx: Transaction) -> None:
        """Broadcast transaction to peers."""
        import urllib.request
        
        tx_data = json.dumps({
            'tx_id': tx.tx_id,
            'inputs': tx.inputs,
            'outputs': tx.outputs,
            'signature': tx.signature,
            'public_key': tx.public_key,
            'fee': tx.fee
        })
        
        for peer in self.peers:
            try:
                req = urllib.request.Request(
                    f"{peer}/transactions/new",
                    data=tx_data.encode(),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass
    
    def _broadcast_block(self, block: Block) -> None:
        """Broadcast block to peers (for consensus)."""
        # In a real implementation, this would push the block to peers
        # For now, peers will pull via /nodes/resolve
        pass
    
    def add_peer(self, peer_url: str) -> None:
        """Add a peer node."""
        if peer_url not in self.peers:
            self.peers.append(peer_url)
    
    def set_wallet(self, wallet: Wallet) -> None:
        """Set the node's wallet."""
        self.wallet = wallet
    
    def run(self, debug: bool = False) -> None:
        """Run the node server."""
        print(f"Starting Globex node on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)
    
    def close(self) -> None:
        """Shutdown the node."""
        self.mining = False
        self.blockchain.close()


def create_node(host: str = "0.0.0.0", port: int = API_PORT) -> GlobexNode:
    """Convenience function to create a node."""
    return GlobexNode(host, port)


if __name__ == '__main__':
    node = create_node()
    node.run(debug=True)
