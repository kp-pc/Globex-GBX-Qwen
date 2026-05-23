"""
Globex (GBX) P2P Network Implementation
Kademlia DHT-based peer-to-peer networking for Bitcoin-level decentralization
"""

import socket
import threading
import json
import time
import hashlib
import random
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import struct

from config import (
    P2P_PORT, NETWORK_NAME, BLOCK_TIME_TARGET,
    P2P_BOOTSTRAP_NODES
)


@dataclass
class PeerNode:
    """Represents a peer node in the network."""
    node_id: str
    host: str
    port: int
    last_seen: float = 0.0
    reputation: float = 1.0
    block_height: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'node_id': self.node_id,
            'host': self.host,
            'port': self.port,
            'last_seen': self.last_seen,
            'reputation': self.reputation,
            'block_height': self.block_height
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PeerNode':
        return cls(**data)


class KademliaBucket:
    """Kademlia routing table bucket for k-bucket management."""
    
    def __init__(self, prefix: str, k: int = 20):
        self.prefix = prefix
        self.k = k
        self.peers: List[PeerNode] = []
        self.lock = threading.Lock()
    
    def add_peer(self, peer: PeerNode) -> bool:
        """Add a peer to the bucket."""
        with self.lock:
            # Check if peer already exists
            for i, p in enumerate(self.peers):
                if p.node_id == peer.node_id:
                    # Update existing peer
                    self.peers[i] = peer
                    return True
            
            # Add new peer if bucket not full
            if len(self.peers) < self.k:
                self.peers.append(peer)
                return True
            
            # Bucket is full - could implement eviction logic here
            return False
    
    def remove_peer(self, node_id: str) -> bool:
        """Remove a peer from the bucket."""
        with self.lock:
            for i, p in enumerate(self.peers):
                if p.node_id == node_id:
                    self.peers.pop(i)
                    return True
            return False
    
    def get_peers(self) -> List[PeerNode]:
        """Get all peers in the bucket."""
        with self.lock:
            return self.peers.copy()


class KademliaRoutingTable:
    """Kademlia DHT routing table implementation."""
    
    def __init__(self, local_node_id: str, k: int = 20):
        self.local_node_id = local_node_id
        self.k = k
        self.buckets: Dict[int, KademliaBucket] = {}
        self.lock = threading.Lock()
        
        # Initialize 256 buckets (one for each bit position)
        for i in range(256):
            self.buckets[i] = KademliaBucket(prefix=f"{i:08b}", k=k)
    
    def _calculate_distance(self, id1: str, id2: str) -> int:
        """Calculate XOR distance between two node IDs."""
        h1 = hashlib.sha256(id1.encode()).hexdigest()
        h2 = hashlib.sha256(id2.encode()).hexdigest()
        
        xor_val = int(h1, 16) ^ int(h2, 16)
        return xor_val.bit_length() if xor_val > 0 else 0
    
    def _get_bucket_index(self, node_id: str) -> int:
        """Get the bucket index for a given node ID."""
        distance = self._calculate_distance(self.local_node_id, node_id)
        return min(distance, 255)
    
    def add_peer(self, peer: PeerNode) -> bool:
        """Add a peer to the routing table."""
        bucket_idx = self._get_bucket_index(peer.node_id)
        with self.lock:
            return self.buckets[bucket_idx].add_peer(peer)
    
    def remove_peer(self, node_id: str) -> bool:
        """Remove a peer from the routing table."""
        bucket_idx = self._get_bucket_index(node_id)
        with self.lock:
            return self.buckets[bucket_idx].remove_peer(node_id)
    
    def get_closest_peers(self, node_id: str, count: int = 20) -> List[PeerNode]:
        """Get the closest peers to a given node ID."""
        with self.lock:
            all_peers = []
            for bucket in self.buckets.values():
                all_peers.extend(bucket.get_peers())
            
            # Sort by distance to target node_id
            all_peers.sort(key=lambda p: self._calculate_distance(p.node_id, node_id))
            return all_peers[:count]
    
    def get_random_peers(self, count: int = 10) -> List[PeerNode]:
        """Get random peers from the routing table."""
        with self.lock:
            all_peers = []
            for bucket in self.buckets.values():
                all_peers.extend(bucket.get_peers())
            
            if len(all_peers) <= count:
                return all_peers
            
            return random.sample(all_peers, count)


class P2PNetwork:
    """Main P2P network manager for Globex blockchain."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = P2P_PORT):
        self.host = host
        self.port = port
        self.node_id = self._generate_node_id()
        self.routing_table = KademliaRoutingTable(self.node_id)
        self.connected_peers: Set[str] = set()
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.message_handlers: Dict[str, callable] = {}
        self.lock = threading.Lock()
        
        # Register default message handlers
        self._register_default_handlers()
    
    def _generate_node_id(self) -> str:
        """Generate a unique node ID."""
        unique_data = f"{self.host}:{self.port}:{time.time()}:{random.random()}"
        return hashlib.sha256(unique_data.encode()).hexdigest()
    
    def _register_default_handlers(self):
        """Register default P2P message handlers."""
        self.message_handlers = {
            'ping': self._handle_ping,
            'pong': self._handle_pong,
            'get_peers': self._handle_get_peers,
            'peers': self._handle_peers,
            'get_blocks': self._handle_get_blocks,
            'blocks': self._handle_blocks,
            'transaction': self._handle_transaction,
            'block': self._handle_block,
            'get_latest_block': self._handle_get_latest_block,
        }
    
    def start(self):
        """Start the P2P server."""
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(50)
        self.server_socket.settimeout(1.0)
        
        print(f"P2P Server started on {self.host}:{self.port}")
        print(f"Node ID: {self.node_id[:16]}...")
        
        # Start connection acceptor thread
        acceptor_thread = threading.Thread(target=self._accept_connections, daemon=True)
        acceptor_thread.start()
        
        # Connect to bootstrap nodes
        self._connect_to_bootstrap_nodes()
    
    def stop(self):
        """Stop the P2P server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
    
    def _accept_connections(self):
        """Accept incoming connections."""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr),
                    daemon=True
                )
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")
                break
    
    def _handle_client(self, client_socket: socket.socket, addr: tuple):
        """Handle a client connection."""
        try:
            client_socket.settimeout(30.0)
            buffer = b""
            
            while self.running:
                # Receive data
                data = client_socket.recv(4096)
                if not data:
                    break
                
                buffer += data
                
                # Process complete messages (simple length-prefixed protocol)
                while len(buffer) >= 4:
                    msg_length = struct.unpack('>I', buffer[:4])[0]
                    if len(buffer) < 4 + msg_length:
                        break
                    
                    msg_data = buffer[4:4+msg_length]
                    buffer = buffer[4+msg_length:]
                    
                    try:
                        message = json.loads(msg_data.decode('utf-8'))
                        self._process_message(message, client_socket)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from {addr}")
            
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()
    
    def _process_message(self, message: Dict, client_socket: socket.socket):
        """Process an incoming P2P message."""
        msg_type = message.get('type')
        
        if msg_type in self.message_handlers:
            response = self.message_handlers[msg_type](message, client_socket)
            if response:
                self._send_message(client_socket, response)
    
    def _send_message(self, sock: socket.socket, message: Dict):
        """Send a message over a socket."""
        try:
            msg_data = json.dumps(message).encode('utf-8')
            msg_length = struct.pack('>I', len(msg_data))
            sock.sendall(msg_length + msg_data)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _handle_ping(self, message: Dict, sock: socket.socket) -> Dict:
        """Handle ping message."""
        return {'type': 'pong', 'node_id': self.node_id, 'timestamp': time.time()}
    
    def _handle_pong(self, message: Dict, sock: socket.socket) -> None:
        """Handle pong message."""
        node_id = message.get('node_id')
        if node_id:
            with self.lock:
                self.connected_peers.add(node_id)
    
    def _handle_get_peers(self, message: Dict, sock: socket.socket) -> Dict:
        """Handle get_peers request."""
        count = message.get('count', 10)
        peers = self.routing_table.get_random_peers(count)
        return {
            'type': 'peers',
            'peers': [p.to_dict() for p in peers],
            'node_id': self.node_id
        }
    
    def _handle_peers(self, message: Dict, sock: socket.socket) -> None:
        """Handle peers response."""
        peers_data = message.get('peers', [])
        for peer_data in peers_data:
            peer = PeerNode.from_dict(peer_data)
            self.routing_table.add_peer(peer)
    
    def _handle_get_blocks(self, message: Dict, sock: socket.socket) -> Dict:
        """Handle get_blocks request - placeholder for blockchain integration."""
        return {'type': 'blocks', 'blocks': [], 'node_id': self.node_id}
    
    def _handle_blocks(self, message: Dict, sock: socket.socket) -> None:
        """Handle blocks response - placeholder for blockchain integration."""
        pass
    
    def _handle_transaction(self, message: Dict, sock: socket.socket) -> None:
        """Handle transaction broadcast - placeholder for mempool integration."""
        pass
    
    def _handle_block(self, message: Dict, sock: socket.socket) -> None:
        """Handle block broadcast - placeholder for chain integration."""
        pass
    
    def _handle_get_latest_block(self, message: Dict, sock: socket.socket) -> Dict:
        """Handle get_latest_block request - placeholder."""
        return {'type': 'latest_block', 'block': None, 'node_id': self.node_id}
    
    def _connect_to_bootstrap_nodes(self):
        """Connect to bootstrap nodes to join the network."""
        for bootstrap in P2P_BOOTSTRAP_NODES:
            try:
                host, port = bootstrap.split(':')
                self.connect_to_peer(host, int(port))
            except Exception as e:
                print(f"Failed to connect to bootstrap node {bootstrap}: {e}")
    
    def connect_to_peer(self, host: str, port: int) -> bool:
        """Connect to a peer node."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((host, port))
            
            # Send ping to establish connection
            ping_msg = {
                'type': 'ping',
                'node_id': self.node_id,
                'timestamp': time.time()
            }
            self._send_message(sock, ping_msg)
            
            # Request peers
            peers_msg = {'type': 'get_peers', 'count': 20}
            self._send_message(sock, peers_msg)
            
            # Add to routing table
            peer = PeerNode(
                node_id="",  # Will be updated from pong
                host=host,
                port=port,
                last_seen=time.time()
            )
            self.routing_table.add_peer(peer)
            
            sock.close()
            return True
            
        except Exception as e:
            print(f"Failed to connect to {host}:{port}: {e}")
            return False
    
    def broadcast(self, message: Dict, exclude: Set[str] = None):
        """Broadcast a message to all connected peers."""
        exclude = exclude or set()
        # In a full implementation, this would send to all active connections
        pass
    
    def discover_peers(self):
        """Discover new peers through the DHT."""
        peers = self.routing_table.get_random_peers(10)
        for peer in peers:
            try:
                self.connect_to_peer(peer.host, peer.port)
            except:
                pass
    
    def get_peer_count(self) -> int:
        """Get the number of known peers."""
        all_peers = []
        for bucket in self.routing_table.buckets.values():
            all_peers.extend(bucket.get_peers())
        return len(all_peers)


# Example usage and testing
if __name__ == "__main__":
    network = P2PNetwork(host="0.0.0.0", port=P2P_PORT)
    network.start()
    
    try:
        while True:
            time.sleep(1)
            print(f"Connected peers: {network.get_peer_count()}")
    except KeyboardInterrupt:
        network.stop()
