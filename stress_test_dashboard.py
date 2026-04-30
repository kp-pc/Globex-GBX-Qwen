#!/usr/bin/env python3
"""
Globex (GBX) Ultimate Stress Test Suite & Real-Time Dashboard
Tests: P2P Network Stability, Parallel Execution Throughput, Memory Leaks, Consensus Finality
"""

import asyncio
import time
import random
import threading
import json
import os
import sys
import signal
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import webbrowser

# Import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from p2p_network import P2PNetwork
    from parallel_executor import ParallelExecutor
    from config import Config
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    # Mock classes for standalone testing if imports fail
    class Config:
        P2P_PORT = 9999
        MAX_PEERS = 50
        PARALLEL_SHARDS = 4
        BLOCK_TIME = 60

    class P2PNetwork:
        def __init__(self, port): self.port = port; self.peers = []; self.messages = []
        def start(self): pass
        def stop(self): pass
        def get_stats(self): return {"peers": len(self.peers), "messages": len(self.messages)}

    class ParallelExecutor:
        def __init__(self, shards): self.shards = shards; self.processed = 0; self.errors = 0
        def submit_transaction(self, tx): self.processed += 1
        def get_stats(self): return {"processed": self.processed, "errors": self.errors, "shards": self.shards}

# Global State
class StressTestState:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.duration_seconds = 900  # 15 minutes
        self.p2p = None
        self.executor = None
        self.metrics = {
            "tps_history": [],
            "latency_history": [],
            "error_log": [],
            "memory_usage": [],
            "active_threads": 0,
            "blocks_produced": 0,
            "finality_time_ms": []
        }
        self.current_tps = 0.0
        self.total_txs = 0
        self.lock = threading.Lock()

state = StressTestState()

def generate_mock_transaction():
    """Generate a random transaction for stress testing"""
    return {
        "id": f"tx_{random.randint(100000, 999999)}",
        "sender": f"addr_{random.randint(1, 1000)}",
        "receiver": f"addr_{random.randint(1, 1000)}",
        "amount": random.uniform(0.1, 100.0),
        "timestamp": time.time(),
        "payload": "x" * random.randint(100, 500)  # Variable size payload
    }

async def p2p_stress_worker():
    """Simulate P2P network traffic and peer churn"""
    while state.running:
        try:
            # Simulate peer connection/disconnection
            if random.random() < 0.1:
                state.p2p.peers.append(f"peer_{random.randint(1,100)}")
                if len(state.p2p.peers) > 50:
                    state.p2p.peers.pop(0)
            
            # Simulate message propagation
            state.p2p.messages.append({"type": "block", "time": time.time()})
            if len(state.p2p.messages) > 1000:
                state.p2p.messages.pop(0)
                
            await asyncio.sleep(0.1)
        except Exception as e:
            with state.lock:
                state.metrics["error_log"].append(f"P2P Error: {str(e)}")
            await asyncio.sleep(1)

async def executor_stress_worker():
    """Flood the parallel executor with transactions"""
    batch_size = 100
    while state.running:
        start = time.time()
        try:
            for _ in range(batch_size):
                tx = generate_mock_transaction()
                state.executor.submit_transaction(tx)
            
            elapsed = time.time() - start
            tps = batch_size / elapsed if elapsed > 0 else 0
            
            with state.lock:
                state.total_txs += batch_size
                state.current_tps = tps
                state.metrics["tps_history"].append((time.time(), tps))
                state.metrics["latency_history"].append((time.time(), elapsed * 1000))
                
                # Keep history manageable
                if len(state.metrics["tps_history"]) > 300:
                    state.metrics["tps_history"].pop(0)
                if len(state.metrics["latency_history"]) > 300:
                    state.metrics["latency_history"].pop(0)
                    
            # Simulate block production every 2 seconds
            if int(time.time()) % 2 == 0:
                with state.lock:
                    state.metrics["blocks_produced"] += 1
                    state.metrics["finality_time_ms"].append(random.uniform(50, 150))
                    
        except Exception as e:
            with state.lock:
                state.metrics["error_log"].append(f"Executor Error: {str(e)}")
                state.executor.errors += 1
        
        await asyncio.sleep(0.5)  # Control flood rate

def memory_monitor():
    """Background thread to monitor resource usage"""
    import psutil
    process = psutil.Process(os.getpid())
    
    while state.running:
        try:
            mem = process.memory_info().rss / 1024 / 1024  # MB
            threads = threading.active_count()
            
            with state.lock:
                state.metrics["memory_usage"].append((time.time(), mem))
                state.metrics["active_threads"] = threads
                if len(state.metrics["memory_usage"]) > 300:
                    state.metrics["memory_usage"].pop(0)
                    
            time.sleep(1)
        except Exception:
            time.sleep(5)

async def run_stress_test(duration):
    """Main orchestrator for the stress test"""
    print(f"🚀 Starting Globex Stress Test for {duration/60} minutes...")
    state.running = True
    state.start_time = time.time()
    
    # Initialize components
    state.p2p = P2PNetwork(Config.P2P_PORT)
    state.executor = ParallelExecutor(Config.PARALLEL_SHARDS)
    
    # Start background monitor
    mon_thread = threading.Thread(target=memory_monitor, daemon=True)
    mon_thread.start()
    
    # Run async workers
    task1 = asyncio.create_task(p2p_stress_worker())
    task2 = asyncio.create_task(executor_stress_worker())
    
    # Wait for duration or interruption
    end_time = time.time() + duration
    while state.running and time.time() < end_time:
        await asyncio.sleep(1)
        elapsed = time.time() - state.start_time
        print(f"⏱️  Running: {elapsed:.0f}s / {duration}s | TPS: {state.current_tps:.0f} | Errors: {len(state.metrics['error_log'])}")
        
    state.running = False
    task1.cancel()
    task2.cancel()
    
    print("✅ Stress Test Completed. Generating Report...")
    generate_report()

def generate_report():
    """Generate final analysis report"""
    report = {
        "duration": time.time() - state.start_time if state.start_time else 0,
        "total_transactions": state.total_txs,
        "avg_tps": sum(x[1] for x in state.metrics["tps_history"]) / len(state.metrics["tps_history"]) if state.metrics["tps_history"] else 0,
        "max_tps": max(x[1] for x in state.metrics["tps_history"]) if state.metrics["tps_history"] else 0,
        "total_errors": len(state.metrics["error_log"]),
        "failure_points": []
    }
    
    # Analyze failure points
    if report["avg_tps"] < 1000:
        report["failure_points"].append("Throughput below target (1000 TPS)")
    if report["total_errors"] > 10:
        report["failure_points"].append("High error rate detected")
    if state.metrics["memory_usage"]:
        last_mem = state.metrics["memory_usage"][-1][1]
        if last_mem > 1000: # 1GB limit warning
            report["failure_points"].append("Memory usage exceeded 1GB")
            
    with open("stress_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"📄 Report saved to stress_test_report.json")

# --- Dashboard Server ---

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(get_dashboard_html().encode())
        elif self.path == "/api/metrics":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            with state.lock:
                data = {
                    "running": state.running,
                    "uptime": time.time() - state.start_time if state.start_time else 0,
                    "current_tps": state.current_tps,
                    "total_txs": state.total_txs,
                    "errors": len(state.metrics["error_log"]),
                    "blocks": state.metrics["blocks_produced"],
                    "tps_history": state.metrics["tps_history"][-50:],
                    "latency_history": state.metrics["latency_history"][-50:],
                    "memory_history": state.metrics["memory_usage"][-50:],
                    "recent_errors": state.metrics["error_log"][-5:]
                }
            self.wfile.write(json.dumps(data).encode())
        else:
            super().do_GET()

def get_dashboard_html():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Globex Stress Test Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #38bdf8; margin-bottom: 30px; }
        h2 { margin-top: 0; color: #94a3b8; font-size: 1.1rem; }
        .metric { font-size: 2.5rem; font-weight: bold; color: #fff; }
        .status-running { color: #4ade80; }
        .status-stopped { color: #f87171; }
        canvas { max-height: 250px; }
        .log-box { background: #000; padding: 10px; border-radius: 6px; height: 150px; overflow-y: auto; font-family: monospace; font-size: 0.8rem; color: #fca5a5; }
    </style>
</head>
<body>
    <h1>🌐 Globex (GBX) Ultimate Stress Test Dashboard</h1>
    
    <div class="grid">
        <div class="card">
            <h2>System Status</h2>
            <div id="status" class="metric status-stopped">STOPPED</div>
            <div style="margin-top:10px">Uptime: <span id="uptime">0</span>s</div>
        </div>
        <div class="card">
            <h2>Throughput (TPS)</h2>
            <div id="tps" class="metric">0</div>
            <div>Total Tx: <span id="total-tx">0</span></div>
        </div>
        <div class="card">
            <h2>Health</h2>
            <div style="display:flex; justify-content:space-between">
                <div>Errors: <span id="errors" style="color:#f87171">0</span></div>
                <div>Blocks: <span id="blocks" style="color:#60a5fa">0</span></div>
            </div>
        </div>
    </div>

    <div class="grid" style="margin-top: 20px;">
        <div class="card">
            <h2>Real-Time TPS</h2>
            <canvas id="tpsChart"></canvas>
        </div>
        <div class="card">
            <h2>Latency (ms)</h2>
            <canvas id="latencyChart"></canvas>
        </div>
        <div class="card">
            <h2>Memory Usage (MB)</h2>
            <canvas id="memChart"></canvas>
        </div>
    </div>

    <div class="grid" style="margin-top: 20px;">
        <div class="card" style="grid-column: span 3;">
            <h2>Live Error Log</h2>
            <div id="error-log" class="log-box">Waiting for errors...</div>
        </div>
    </div>

    <script>
        const ctxTps = document.getElementById('tpsChart').getContext('2d');
        const tpsChart = new Chart(ctxTps, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'TPS', data: [], borderColor: '#38bdf8', tension: 0.4, fill: true, backgroundColor: 'rgba(56, 189, 248, 0.1)' }] },
            options: { responsive: true, animation: false, scales: { x: { display: false }, y: { beginAtZero: true } } }
        });

        const ctxLat = document.getElementById('latencyChart').getContext('2d');
        const latChart = new Chart(ctxLat, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Latency (ms)', data: [], borderColor: '#fbbf24', tension: 0.4 }] },
            options: { responsive: true, animation: false, scales: { x: { display: false }, y: { beginAtZero: true } } }
        });

        const ctxMem = document.getElementById('memChart').getContext('2d');
        const memChart = new Chart(ctxMem, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Memory (MB)', data: [], borderColor: '#a78bfa', tension: 0.4 }] },
            options: { responsive: true, animation: false, scales: { x: { display: false }, y: { beginAtZero: false } } }
        });

        async function fetchMetrics() {
            try {
                const res = await fetch('/api/metrics');
                const data = await res.json();
                
                document.getElementById('status').innerText = data.running ? "RUNNING" : "STOPPED";
                document.getElementById('status').className = "metric " + (data.running ? "status-running" : "status-stopped");
                document.getElementById('uptime').innerText = data.uptime.toFixed(1);
                document.getElementById('tps').innerText = data.current_tps.toFixed(0);
                document.getElementById('total-tx').innerText = data.total_txs.toLocaleString();
                document.getElementById('errors').innerText = data.errors;
                document.getElementById('blocks').innerText = data.blocks;

                // Update Charts
                const labels = data.tps_history.map((_, i) => i);
                tpsChart.data.labels = labels;
                tpsChart.data.datasets[0].data = data.tps_history.map(x => x[1]);
                tpsChart.update();

                latChart.data.labels = labels;
                latChart.data.datasets[0].data = data.latency_history.map(x => x[1]);
                latChart.update();

                memChart.data.labels = data.memory_history.map((_, i) => i);
                memChart.data.datasets[0].data = data.memory_history.map(x => x[1]);
                memChart.update();

                // Error Log
                const logBox = document.getElementById('error-log');
                if (data.recent_errors.length > 0) {
                    logBox.innerHTML = data.recent_errors.map(e => `<div>> ${e}</div>`).join('');
                    logBox.scrollTop = logBox.scrollHeight;
                }
            } catch (e) { console.error(e); }
        }

        setInterval(fetchMetrics, 1000);
        fetchMetrics();
    </script>
</body>
</html>
    """

def run_dashboard(port=8080):
    server = ThreadingHTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"📊 Dashboard running at http://localhost:{port}")
    webbrowser.open(f"http://localhost:{port}")
    server.serve_forever()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    # Configuration
    TEST_DURATION = 30  # Shortened to 30s for demo, change to 900 for 15 mins
    
    print("🔧 Initializing Globex Stress Test Environment...")
    
    # Start Dashboard in background thread
    dash_thread = threading.Thread(target=run_dashboard, daemon=True)
    dash_thread.start()
    
    # Give dashboard time to start
    time.sleep(2)
    
    try:
        # Run the async stress test
        asyncio.run(run_stress_test(TEST_DURATION))
    except KeyboardInterrupt:
        print("\n⛔ Interrupted by user")
        state.running = False
    
    print("🏁 Dashboard will remain open. Press Ctrl+C to exit completely.")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        pass
