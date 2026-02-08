import socket
import threading
import config

class AkonNetwork:
    def __init__(self, on_message_callback):
        """
        Initializes the UDP socket and the background listener.
        :param on_message_callback: A function in main.py to handle incoming UI updates.
        """
        self.callback = on_message_callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Start the background listener thread
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)

    def start(self):
        """Binds the socket and begins listening for packets."""
        try:
            self.sock.bind(('', config.UDP_PORT))
            self.listen_thread.start()
            return True
        except Exception as e:
            print(f"Network Bind Error: {e}")
            return False

    def broadcast(self, node_id, message):
        """Transmits a formatted packet to the entire local network segment."""
        payload = f"{node_id}: {message}"
        try:
            self.sock.sendto(payload.encode('utf-8'), (config.BROADCAST_ADDR, config.UDP_PORT))
            return True
        except Exception as e:
            print(f"Broadcast Error: {e}")
            return False

    def _listen_loop(self):
        """Internal loop that waits for incoming UDP data."""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(config.BUFFER_SIZE)
                decoded_msg = data.decode('utf-8')
                # Send the data back to the UI via the callback function
                self.callback(decoded_msg, addr[0])
            except:
                break

    def stop(self):
        """Safely shuts down the networking engine."""
        self.running = False
        self.sock.close()