#!/usr/bin/env python3
"""
Globex (GBX) Web Dashboard
Simple, user-friendly interface for managing your Globex cryptocurrency
"""

import argparse
import json
import os
import sys
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import Blockchain
from wallet import Wallet, generate_wallet
from utils import bytes_to_hex, verify_address
from config import DB_PATH

app = Flask(__name__)

# Global blockchain instance
blockchain = None
current_wallet = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 Globex Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .stat-label { color: #666; margin-top: 5px; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: transform 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .input-group { margin-bottom: 15px; }
        .input-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        .input-group input {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
        }
        .input-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .wallet-info {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .wallet-address {
            font-family: monospace;
            background: #e9ecef;
            padding: 8px;
            border-radius: 5px;
            word-break: break-all;
            font-size: 0.9em;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success { background: #d4edda; color: #155724; }
        .alert-error { background: #f8d7da; color: #721c24; }
        .alert-info { background: #d1ecf1; color: #0c5460; }
        .tx-list { max-height: 300px; overflow-y: auto; }
        .tx-item {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 0.9em;
        }
        .tx-item:last-child { border-bottom: none; }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .badge-success { background: #28a745; color: white; }
        .badge-warning { background: #ffc107; color: #333; }
        .private-key {
            font-family: monospace;
            background: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            word-break: break-all;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Globex Dashboard</h1>
            <p>Your friendly cryptocurrency management interface</p>
        </div>

        {% if message %}
        <div class="alert alert-{{ message_type }}">{{ message }}</div>
        {% endif %}

        <div class="dashboard">
            <!-- Blockchain Info Card -->
            <div class="card">
                <h2>📊 Network Status</h2>
                <div class="stat-value">{{ chain_length }}</div>
                <div class="stat-label">Blocks in Chain</div>
                <div style="margin-top: 15px;">
                    <div class="stat-value" style="font-size: 1.5em;">{{ mempool_size }}</div>
                    <div class="stat-label">Pending Transactions</div>
                </div>
                <button class="btn" onclick="location.reload()">🔄 Refresh</button>
            </div>

            <!-- Wallet Card -->
            <div class="card">
                <h2>👛 Your Wallet</h2>
                {% if wallet %}
                <div class="wallet-info">
                    <strong>Address:</strong>
                    <div class="wallet-address">{{ wallet.address }}</div>
                </div>
                <div class="stat-value">{{ balance }} GBX</div>
                <div class="stat-label">Current Balance</div>
                <button class="btn" onclick="document.getElementById('send-form').scrollIntoView({behavior: 'smooth'})">💸 Send GBX</button>
                <button class="btn" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);" onclick="mineBlock()">⛏️ Mine Block</button>
                {% else %}
                <p style="color: #666; margin-bottom: 15px;">No wallet created yet. Create one to get started!</p>
                <form method="POST" action="/create-wallet">
                    <button class="btn" type="submit">✨ Create New Wallet</button>
                </form>
                {% endif %}
            </div>

            <!-- Quick Actions Card -->
            <div class="card">
                <h2>⚡ Quick Actions</h2>
                <form method="POST" action="/mine">
                    <button class="btn" type="submit" {% if not wallet %}disabled{% endif %}>⛏️ Mine 1 Block</button>
                </form>
                <form method="POST" action="/validate">
                    <button class="btn" type="submit" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">✓ Validate Chain</button>
                </form>
                <form method="POST" action="/reset" onsubmit="return confirm('Are you sure? This will reset the blockchain!')">
                    <button class="btn" type="submit" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">🗑️ Reset Demo</button>
                </form>
            </div>
        </div>

        {% if wallet %}
        <!-- Send Transaction Form -->
        <div class="card" id="send-form" style="margin-bottom: 30px;">
            <h2>💸 Send GBX</h2>
            <form method="POST" action="/send">
                <div class="input-group">
                    <label>Recipient Address</label>
                    <input type="text" name="to" required placeholder="Enter recipient address" pattern="[A-Za-z0-9]{34}">
                </div>
                <div class="input-group">
                    <label>Amount (GBX)</label>
                    <input type="number" name="amount" step="0.0001" min="0.0001" required placeholder="0.00">
                </div>
                <div class="input-group">
                    <label>Transaction Fee (GBX)</label>
                    <input type="number" name="fee" step="0.0001" min="0.0001" value="0.001" placeholder="0.001">
                </div>
                <button class="btn" type="submit">Send Transaction</button>
            </form>
        </div>

        <!-- Private Key Warning -->
        <div class="warning-box">
            <strong>⚠️ Important Security Notice:</strong>
            <p style="margin-top: 10px;">Your private key was shown when you created your wallet. Make sure you saved it securely! Never share your private key with anyone.</p>
        </div>
        {% endif %}

        <!-- Recent Blocks -->
        <div class="card" style="margin-bottom: 30px;">
            <h2>🔗 Recent Blocks</h2>
            <div class="tx-list">
                {% for block in recent_blocks %}
                <div class="tx-item">
                    <strong>Block #{{ block.index }}</strong>
                    <span class="badge badge-success">{{ block.tx_count }} transactions</span>
                    <div style="font-family: monospace; font-size: 0.85em; color: #666; margin-top: 5px;">
                        {{ block.hash[:50] }}...
                    </div>
                    <div style="font-size: 0.85em; color: #999; margin-top: 5px;">
                        Reward: {{ block.reward }} GBX
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        function mineBlock() {
            fetch('/mine', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Block mined successfully!');
                        location.reload();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
        }
    </script>
</body>
</html>
"""

def init_blockchain():
    global blockchain
    blockchain = Blockchain(db_path=DB_PATH)

@app.route('/')
def dashboard():
    global blockchain, current_wallet
    
    if blockchain is None:
        init_blockchain()
    
    # Load wallet if exists
    wallet_data = None
    balance = 0
    if os.path.exists('dashboard_wallet.json'):
        try:
            current_wallet = Wallet.load_from_file('dashboard_wallet.json')
            balance = blockchain.get_balance(current_wallet.address)
            wallet_data = {'address': current_wallet.address}
        except:
            pass
    
    # Get blockchain info
    chain_length = blockchain.get_chain_length()
    mempool_size = blockchain.mempool.size()
    
    # Get recent blocks
    recent_blocks = []
    current_block = blockchain.get_latest_block()
    for i in range(min(5, chain_length)):
        if current_block:
            reward = blockchain._calculate_block_reward(current_block.index)
            recent_blocks.append({
                'index': current_block.index,
                'hash': current_block.block_hash,
                'tx_count': len(current_block.transactions),
                'reward': f"{reward:.2f}"
            })
            # Get previous block
            if current_block.index > 0:
                current_block = blockchain.get_block_by_index(current_block.index - 1)
            else:
                break
    
    return render_template_string(
        HTML_TEMPLATE,
        wallet=wallet_data,
        balance=f"{balance:.4f}",
        chain_length=chain_length,
        mempool_size=mempool_size,
        recent_blocks=recent_blocks,
        message=request.args.get('message'),
        message_type=request.args.get('message_type', 'info')
    )

@app.route('/create-wallet', methods=['POST'])
def create_wallet():
    global current_wallet
    
    wallet = generate_wallet()
    wallet.save_to_file('dashboard_wallet.json')
    current_wallet = wallet
    
    private_key = bytes_to_hex(wallet.get_private_key())
    
    return redirect(url_for('dashboard', 
                          message=f"Wallet created! Address: {wallet.address}. SAVE YOUR PRIVATE KEY: {private_key}",
                          message_type='success'))

@app.route('/mine', methods=['POST'])
def mine():
    global blockchain, current_wallet
    
    if not current_wallet:
        return jsonify({'success': False, 'error': 'No wallet found. Create one first.'})
    
    block = blockchain.mine_block(current_wallet.address)
    if block:
        return jsonify({
            'success': True,
            'block_index': block.index,
            'hash': block.block_hash,
            'reward': blockchain._calculate_block_reward(block.index)
        })
    else:
        return jsonify({'success': False, 'error': 'Failed to mine block'})

@app.route('/send', methods=['POST'])
def send():
    global blockchain, current_wallet
    
    if not current_wallet:
        return redirect(url_for('dashboard', message='No wallet found', message_type='error'))
    
    to_address = request.form.get('to')
    amount = float(request.form.get('amount'))
    fee = float(request.form.get('fee', 0.001))
    
    if not verify_address(to_address):
        return redirect(url_for('dashboard', message='Invalid recipient address', message_type='error'))
    
    tx, msg = blockchain.create_transaction(current_wallet, to_address, amount, fee)
    
    if tx:
        success, result = blockchain.add_transaction(tx)
        if success:
            # Mine a block to include the transaction
            blockchain.mine_block(current_wallet.address)
            return redirect(url_for('dashboard', 
                                  message=f"Transaction sent! TX ID: {tx.tx_id[:16]}...",
                                  message_type='success'))
        else:
            return redirect(url_for('dashboard', message=f'Error: {result}', message_type='error'))
    else:
        return redirect(url_for('dashboard', message=f'Error: {msg}', message_type='error'))

@app.route('/validate', methods=['POST'])
def validate():
    global blockchain
    
    valid, msg = blockchain.validate_chain()
    message = f"✓ Chain is valid! {msg}" if valid else f"✗ Chain validation failed: {msg}"
    message_type = 'success' if valid else 'error'
    
    return redirect(url_for('dashboard', message=message, message_type=message_type))

@app.route('/reset', methods=['POST'])
def reset():
    global blockchain
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists('dashboard_wallet.json'):
        os.remove('dashboard_wallet.json')
    
    blockchain.close()
    init_blockchain()
    
    return redirect(url_for('dashboard', 
                          message='Dashboard reset! Create a new wallet to start fresh.',
                          message_type='info'))

def run_dashboard(host='0.0.0.0', port=5000, debug=False):
    init_blockchain()
    print(f"\n{'='*60}")
    print("🌐 GLOBEX DASHBOARD")
    print(f"{'='*60}")
    print(f"Opening dashboard at: http://localhost:{port}")
    print(f"Database: {DB_PATH}")
    print(f"{'='*60}")
    print("\nPress Ctrl+C to stop the dashboard\n")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
        blockchain.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Globex Web Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    run_dashboard(host=args.host, port=args.port, debug=args.debug)
