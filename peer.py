import socket

import threading

import time


class Peer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.peers = []
        self.lock = threading.Lock()  # Thread-safe operations on peers list


    def start(self):
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()
        print(f"P2P network starting on {self.host}:{self.port}")


    def _run_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"New peer connected from {client_address}")

                with self.lock:
                    self.peers.append(client_socket)

                threading.Thread(target=self.handle_peer, args=(client_socket,), 
                    daemon=True).start()

        except OSError as e:
            print(f"Error starting server: {e}")


    def handle_peer(self, peer_socket):
        while True:
            try:
                data = peer_socket.recv(1024).decode()
                if not data:
                    break
                print(f"Received from peer: {data}")

            except ConnectionResetError:
                break

        # Cleanup when peer disconnects
        with self.lock:
            if peer_socket in self.peers:
                self.peers.remove(peer_socket)
        peer_socket.close()
        print("Peer disconnected")


    def connect_to_peer(self, peer_host: str, peer_port: int):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((peer_host, peer_port))
            with self.lock:
                self.peers.append(client_socket)
            print(f"Connected to peer {peer_host}:{peer_port}")

            threading.Thread(target=self.handle_peer, args=(client_socket,), 
                daemon=True).start()
        except ConnectionRefusedError:
            print(f"Connection to peer {peer_host}:{peer_port} refused")


    def send_to_peers(self, data: str):
        with self.lock:
            for peer_socket in self.peers.copy():
                try:
                    peer_socket.sendall(data.encode())
                except (ConnectionResetError, BrokenPipeError):
                    self.peers.remove(peer_socket)
                    peer_socket.close()


# Example usage
if __name__ == "__main__":
    network = Peer('127.0.0.1', 50001)
    network.start()  # non-blocking

    # Wait a moment to let server start
    time.sleep(1)

    # Connect to another peer (assuming another peer is running on 127.0.0.1:5001)
    network.connect_to_peer('127.0.0.1', 50005)

    # Send a message
    network.send_to_peers('Hello, peers!')
