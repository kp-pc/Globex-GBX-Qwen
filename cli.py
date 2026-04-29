#!/usr/bin/env python3
"""
Globex (GBX) Command Line Interface
Full-featured CLI for node operations, wallet management, and mining
"""

import argparse
import json
import sys
import os
import time
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import Blockchain, Transaction
from wallet import Wallet, generate_wallet, address_from_public_key
from utils import verify_address, bytes_to_hex
from config import API_PORT, DB_PATH, MIN_TRANSACTION_FEE
from miner import CPUMiner


def setup_parser() -> argparse.ArgumentParser:
    """Setup argument parser with all commands."""
    parser = argparse.ArgumentParser(
        prog='globex',
        description='Globex (GBX) Cryptocurrency CLI'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # start-node command
    node_parser = subparsers.add_parser('start-node', help='Start a Globex node')
    node_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    node_parser.add_argument('--port', type=int, default=API_PORT, help='API port')
    node_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    node_parser.add_argument('--peers', nargs='*', help='Peer node URLs to connect to')
    
    # mine command
    mine_parser = subparsers.add_parser('mine', help='Mine blocks')
    mine_parser.add_argument('--address', '-a', help='Miner address (wallet)')
    mine_parser.add_argument('--threads', '-t', type=int, default=2, help='Number of mining threads')
    mine_parser.add_argument('--continuous', '-c', action='store_true', help='Mine continuously')
    mine_parser.add_argument('--count', '-n', type=int, default=1, help='Number of blocks to mine')
    mine_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # create-wallet command
    wallet_parser = subparsers.add_parser('create-wallet', help='Create a new wallet')
    wallet_parser.add_argument('--output', '-o', help='Output file to save wallet')
    wallet_parser.add_argument('--password', '-p', help='Encrypt wallet with password')
    
    # send command
    send_parser = subparsers.add_parser('send', help='Send GBX to an address')
    send_parser.add_argument('--from', dest='from_wallet', required=True, help='Sender wallet file or address')
    send_parser.add_argument('--to', '-t', required=True, help='Recipient address')
    send_parser.add_argument('--amount', '-am', type=float, required=True, help='Amount to send')
    send_parser.add_argument('--fee', '-f', type=float, default=MIN_TRANSACTION_FEE, help='Transaction fee')
    send_parser.add_argument('--password', '-p', help='Wallet password (if encrypted)')
    send_parser.add_argument('--db', default=DB_PATH, help='Database path')
    send_parser.add_argument('--broadcast', action='store_true', help='Broadcast to network')
    
    # balance command
    balance_parser = subparsers.add_parser('balance', help='Check balance')
    balance_parser.add_argument('--address', '-a', required=True, help='Address to check')
    balance_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate the blockchain')
    validate_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # info command
    info_parser = subparsers.add_parser('info', help='Show blockchain info')
    info_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # list-transactions command
    tx_parser = subparsers.add_parser('list-tx', help='List pending transactions')
    tx_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # stake command
    stake_parser = subparsers.add_parser('stake', help='Register as PoS validator')
    stake_parser.add_argument('--address', '-a', required=True, help='Validator address')
    stake_parser.add_argument('--amount', type=float, default=1000, help='Stake amount')
    stake_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    # devfund command
    devfund_parser = subparsers.add_parser('devfund', help='Development fund operations')
    devfund_parser.add_argument('action', choices=['status', 'propose', 'sign'], help='Action to perform')
    devfund_parser.add_argument('--db', default=DB_PATH, help='Database path')
    devfund_parser.add_argument('--amount', type=float, help='Amount for proposal')
    devfund_parser.add_argument('--recipients', nargs='*', help='Recipients for proposal')
    devfund_parser.add_argument('--tx-id', help='Transaction ID for signing')
    devfund_parser.add_argument('--signer', help='Signer address')
    
    # checkpoint command
    checkpoint_parser = subparsers.add_parser('checkpoint', help='View finality checkpoints')
    checkpoint_parser.add_argument('--db', default=DB_PATH, help='Database path')
    
    return parser


def cmd_start_node(args):
    """Start a Globex node."""
    from node import GlobexNode
    
    node = GlobexNode(host=args.host, port=args.port)
    
    if args.peers:
        for peer in args.peers:
            node.add_peer(peer)
            print(f"Added peer: {peer}")
    
    print(f"\n{'='*50}")
    print("GLOBEX NODE")
    print(f"{'='*50}")
    print(f"Network: Globex (GBX)")
    print(f"API Port: {args.port}")
    print(f"Debug Mode: {args.debug}")
    print(f"Peers: {len(node.peers)}")
    print(f"\nEndpoints:")
    print(f"  GET  /health          - Node health check")
    print(f"  POST /mine            - Mine a block")
    print(f"  POST /transactions/new - Send transaction")
    print(f"  GET  /chain           - Get full chain")
    print(f"  GET  /balance/<addr>  - Check balance")
    print(f"  POST /nodes/register  - Register peers")
    print(f"  POST /nodes/resolve   - Resolve conflicts")
    print(f"  GET  /devfund/status  - Dev fund status")
    print(f"{'='*50}\n")
    
    try:
        node.run(debug=args.debug)
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.close()


def cmd_mine(args):
    """Mine blocks."""
    bc = Blockchain(db_path=args.db)
    
    # Determine miner address
    miner_address = args.address
    if not miner_address:
        # Try to load default wallet
        if os.path.exists('wallet.json'):
            wallet = Wallet.load_from_file('wallet.json')
            miner_address = wallet.address
            print(f"Using wallet: {miner_address}")
        else:
            # Create temporary wallet
            wallet = generate_wallet()
            miner_address = wallet.address
            print(f"Created temporary wallet: {miner_address}")
            print(f"Private key (SAVE THIS): {bytes_to_hex(wallet.get_private_key())}")
    
    print(f"\nMining to: {miner_address}")
    print(f"Threads: {args.threads}")
    
    if args.continuous:
        miner = CPUMiner(bc, miner_address, threads=args.threads)
        try:
            miner.start()
        except KeyboardInterrupt:
            miner.stop()
            stats = miner.get_stats()
            print(f"\nMining Statistics:")
            print(f"  Blocks Found: {stats['blocks_found']}")
            print(f"  Hashes Computed: {stats['hashes_computed']:,}")
            print(f"  Average Hash Rate: {stats['hash_rate']:.2f} H/s")
    else:
        # Mine specified number of blocks
        for i in range(args.count):
            print(f"\nMining block {i+1}/{args.count}...")
            block = bc.mine_block(miner_address)
            if block:
                print(f"Block found!")
                print(f"  Index: {block.index}")
                print(f"  Hash: {block.block_hash}")
                print(f"  Nonce: {block.nonce}")
                print(f"  Reward: {bc._calculate_block_reward(block.index):.4f} GBX")
            else:
                print("Failed to mine block")
                break
        
        print(f"\nChain length: {bc.get_chain_length()}")
    
    bc.close()


def cmd_create_wallet(args):
    """Create a new wallet."""
    wallet = generate_wallet()
    
    print(f"\n{'='*50}")
    print("NEW WALLET CREATED")
    print(f"{'='*50}")
    print(f"Address: {wallet.address}")
    print(f"Public Key: {bytes_to_hex(wallet.get_public_key())}")
    print(f"Private Key: {bytes_to_hex(wallet.get_private_key())}")
    print(f"{'='*50}")
    print("\n⚠️  IMPORTANT: Save your private key securely!")
    print("   Never share your private key with anyone.\n")
    
    if args.output:
        wallet.save_to_file(args.output, password=args.password)
        print(f"Wallet saved to: {args.output}")
        if args.password:
            print("Wallet is encrypted with password.")


def cmd_send(args):
    """Send GBX to an address."""
    bc = Blockchain(db_path=args.db)
    
    # Validate recipient address
    if not verify_address(args.to):
        print(f"Error: Invalid recipient address: {args.to}")
        bc.close()
        return
    
    # Load sender wallet
    sender_wallet = None
    
    if os.path.exists(args.from_wallet):
        # Load from file
        try:
            sender_wallet = Wallet.load_from_file(args.from_wallet, password=args.password)
        except Exception as e:
            print(f"Error loading wallet: {e}")
            bc.close()
            return
    else:
        # Try to find by address in UTXO
        balance = bc.get_balance(args.from_wallet)
        if balance > 0:
            print(f"Error: Cannot send from address without private key.")
            print(f"Provide wallet file for: {args.from_wallet}")
            bc.close()
            return
        else:
            print(f"Error: Wallet file not found: {args.from_wallet}")
            bc.close()
            return
    
    print(f"\nSending {args.amount} GBX")
    print(f"From: {sender_wallet.address}")
    print(f"To: {args.to}")
    print(f"Fee: {args.fee} GBX")
    
    # Create transaction
    tx, msg = bc.create_transaction(sender_wallet, args.to, args.amount, args.fee)
    
    if tx:
        success, result = bc.add_transaction(tx)
        if success:
            print(f"\n✓ Transaction created successfully!")
            print(f"  TX ID: {tx.tx_id}")
            print(f"  Status: Pending (in mempool)")
            
            if args.broadcast:
                print("  Broadcasting to network...")
                # In real implementation, broadcast to peers
        else:
            print(f"\n✗ Failed to add transaction: {result}")
    else:
        print(f"\n✗ Failed to create transaction: {msg}")
    
    bc.close()


def cmd_balance(args):
    """Check balance."""
    bc = Blockchain(db_path=args.db)
    
    if not verify_address(args.address):
        print(f"Error: Invalid address: {args.address}")
        bc.close()
        return
    
    balance = bc.get_balance(args.address)
    
    print(f"\n{'='*40}")
    print(f"BALANCE")
    print(f"{'='*40}")
    print(f"Address: {args.address}")
    print(f"Balance: {balance:.8f} GBX")
    print(f"{'='*40}\n")
    
    bc.close()


def cmd_validate(args):
    """Validate the blockchain."""
    bc = Blockchain(db_path=args.db)
    
    valid, msg = bc.validate_chain()
    
    print(f"\n{'='*40}")
    print(f"BLOCKCHAIN VALIDATION")
    print(f"{'='*40}")
    print(f"Valid: {'✓ Yes' if valid else '✗ No'}")
    print(f"Message: {msg}")
    print(f"Chain Length: {bc.get_chain_length()}")
    print(f"{'='*40}\n")
    
    bc.close()


def cmd_info(args):
    """Show blockchain info."""
    bc = Blockchain(db_path=args.db)
    
    latest = bc.get_latest_block()
    
    print(f"\n{'='*50}")
    print("GLOBEX BLOCKCHAIN INFO")
    print(f"{'='*50}")
    print(f"Network: Globex (GBX)")
    print(f"Chain Length: {bc.get_chain_length()}")
    print(f"Mempool Size: {bc.mempool.size()}")
    
    if latest:
        print(f"\nLatest Block:")
        print(f"  Index: {latest.index}")
        print(f"  Hash: {latest.block_hash[:32]}...")
        print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest.timestamp))}")
        print(f"  Transactions: {len(latest.transactions)}")
        print(f"  Difficulty: {latest.difficulty}")
        print(f"  Nonce: {latest.nonce}")
        
        reward = bc._calculate_block_reward(latest.index)
        print(f"  Block Reward: {reward:.4f} GBX")
    
    # Dev fund info
    current_block = bc.get_chain_length()
    dev_status = bc.dev_fund_manager.get_status(current_block)
    if 'error' not in dev_status:
        print(f"\nDevelopment Fund:")
        print(f"  Address: {dev_status['fund_address'][:32]}...")
        print(f"  Total Allocation: {dev_status['total_allocation']:,.0f} GBX")
        print(f"  Released: {dev_status['released']:,.2f} GBX")
        print(f"  Vesting Progress: {dev_status['vesting_progress']}")
    
    print(f"{'='*50}\n")
    
    bc.close()


def cmd_list_tx(args):
    """List pending transactions."""
    bc = Blockchain(db_path=args.db)
    
    txs = bc.mempool.get_transactions()
    
    print(f"\n{'='*50}")
    print(f"PENDING TRANSACTIONS ({len(txs)})")
    print(f"{'='*50}")
    
    if not txs:
        print("No pending transactions.")
    else:
        for tx in txs:
            print(f"\nTX ID: {tx.tx_id}")
            print(f"  Type: {tx.tx_type}")
            print(f"  Fee: {tx.fee:.6f} GBX")
            print(f"  Inputs: {len(tx.inputs)}")
            print(f"  Outputs: {len(tx.outputs)}")
    
    print(f"\n{'='*50}\n")
    
    bc.close()


def cmd_stake(args):
    """Register as PoS validator."""
    bc = Blockchain(db_path=args.db)
    
    current_block = bc.get_chain_length()
    success = bc.stake_manager.register_validator(
        args.address, args.amount, 100, current_block
    )
    
    if success:
        print(f"\n✓ Validator registered successfully!")
        print(f"  Address: {args.address}")
        print(f"  Stake: {args.amount} GBX")
        print(f"  Lockup Period: 100 blocks")
    else:
        print(f"\n✗ Failed to register validator.")
        print(f"  Minimum stake: 1000 GBX")
    
    bc.close()


def cmd_devfund(args):
    """Development fund operations."""
    bc = Blockchain(db_path=args.db)
    current_block = bc.get_chain_length()
    
    if args.action == 'status':
        status = bc.dev_fund_manager.get_status(current_block)
        
        print(f"\n{'='*50}")
        print("DEVELOPMENT FUND STATUS")
        print(f"{'='*50}")
        
        if 'error' in status:
            print(f"Error: {status['error']}")
        else:
            print(f"Fund Address: {status['fund_address']}")
            print(f"Total Allocation: {status['total_allocation']:,.0f} GBX")
            print(f"Released: {status['released']:,.2f} GBX")
            print(f"Vested Available: {status['vested_available']:,.2f} GBX")
            print(f"Remaining Locked: {status['remaining_locked']:,.2f} GBX")
            print(f"Vesting Progress: {status['vesting_progress']}")
            print(f"Multi-sig Required: {status['multi_sig_required']} signatures")
            print(f"Signers: {len(status['signers'])}")
        
        print(f"{'='*50}\n")
    
    elif args.action == 'propose':
        if not args.amount or not args.recipients:
            print("Error: --amount and --recipients required for proposal")
            bc.close()
            return
        
        recipients = [{'address': r, 'amount': args.amount / len(args.recipients)} 
                     for r in args.recipients]
        
        import hashlib
        tx_id = hashlib.sha256(json.dumps({'amount': args.amount, 'recipients': args.recipients}).encode()).hexdigest()[:16]
        
        proposal = bc.dev_fund_manager.propose_transaction(
            tx_id, args.amount, recipients, current_block
        )
        
        print(f"\n✓ Transaction proposed!")
        print(f"  TX ID: {tx_id}")
        print(f"  Amount: {args.amount} GBX")
        print(f"  Required Signatures: {proposal['required_signatures']}")
        print(f"\nNext: Sign with 'globex devfund sign --tx-id {tx_id} --signer <address>'")
    
    elif args.action == 'sign':
        if not args.tx_id or not args.signer:
            print("Error: --tx-id and --signer required")
            bc.close()
            return
        
        success = bc.dev_fund_manager.sign_transaction(args.tx_id, args.signer)
        
        if success:
            print(f"✓ Transaction signed by {args.signer}")
            
            # Try to execute if enough signatures
            executed, msg = bc.dev_fund_manager.execute_transaction(args.tx_id)
            if executed:
                print(f"✓ Transaction executed! Funds released.")
            else:
                print(f"  Waiting for more signatures... ({msg})")
        else:
            print(f"✗ Failed to sign. Check signer authorization.")
    
    bc.close()


def cmd_checkpoint(args):
    """View finality checkpoints."""
    bc = Blockchain(db_path=args.db)
    
    cursor = bc.db.cursor()
    cursor.execute('''
        SELECT block_height, block_hash, finalized FROM checkpoints 
        ORDER BY block_height DESC LIMIT 10
    ''')
    rows = cursor.fetchall()
    
    print(f"\n{'='*50}")
    print("FINALITY CHECKPOINTS (Last 10)")
    print(f"{'='*50}")
    
    if not rows:
        print("No checkpoints yet.")
    else:
        for row in rows:
            status = "✓ Finalized" if row[2] else "Pending"
            print(f"\nBlock: {row[0]}")
            print(f"  Hash: {row[1][:48]}...")
            print(f"  Status: {status}")
    
    print(f"\n{'='*50}\n")
    
    bc.close()


def main():
    """Main entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    commands = {
        'start-node': cmd_start_node,
        'mine': cmd_mine,
        'create-wallet': cmd_create_wallet,
        'send': cmd_send,
        'balance': cmd_balance,
        'validate': cmd_validate,
        'info': cmd_info,
        'list-tx': cmd_list_tx,
        'stake': cmd_stake,
        'devfund': cmd_devfund,
        'checkpoint': cmd_checkpoint,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
