from peer import Peer  # <-- this imports the Peer class from peer.py

import time

# Example: start peer on port 5000
network = Peer('127.0.0.1', 5000)
network.start()

# Wait a moment for server to start
time.sleep(1)

# Connect to another peer if needed
network.connect_to_peer('127.0.0.1', 5001)

# Send a message to all connected peers
network.send_to_peers("Hello from 5000!")
