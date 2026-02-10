import socket
import threading
import config
from kivy.utils import platform

class AkonNetwork:
    def __init__(self, on_message_callback):
        self.callback = on_message_callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.running = True
        self.lock = None

    def _acquire_android_lock(self):
        """Unlocks WiFi for broadcast packets on Android"""
        if platform == 'android':
            try:
                from jnius import autoclass
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                wifi_manager = activity.getSystemService(Context.WIFI_SERVICE)
                self.lock = wifi_manager.createMulticastLock("akon_lock")
                self.lock.setReferenceCounted(True)
                self.lock.acquire()
            except Exception as e:
                print(f"Lock Error: {e}")

    def start(self):
        self._acquire_android_lock()
        try:
            self.sock.bind(('', config.UDP_PORT))
            threading.Thread(target=self._listen_loop, daemon=True).start()
            return True
        except Exception as e:
            return False

    def broadcast(self, node_id, message):
        payload = f"{node_id}: {message}"
        try:
            self.sock.sendto(payload.encode('utf-8'), (config.BROADCAST_ADDR, config.UDP_PORT))
            return True
        except:
            return False

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(config.BUFFER_SIZE)
                self.callback(data.decode('utf-8'), addr[0])
            except:
                break