import socket
import threading
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

# --- UI CONSTANTS ---
BG_COLOR = (0.05, 0.05, 0.1, 1)  # Deep Midnight Blue
ACCENT_COLOR = (0, 0.7, 1, 1)    # Cyber Blue
MY_MSG_COLOR = (0, 0.5, 0.8, 1)  # Your bubbles
THEIR_MSG_COLOR = (0.2, 0.2, 0.3, 1) # Laptop bubbles

class AkonApp(App):
    def build(self):
        self.title = "AKON P2P GATEWAY"
        self.root_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Set Global Background
        with self.root_layout.canvas.before:
            Color(*BG_COLOR)
            self.rect = RoundedRectangle(pos=self.root_layout.pos, size=self.root_layout.size)
            self.root_layout.bind(pos=self.update_rect, size=self.update_rect)

        # --- LOGIN SCREEN ---
        self.login_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5})
        self.login_layout.add_widget(Label(text="[b]AKON[/b]\nAgnostic Gateway", font_size=32, markup=True, halign='center', color=ACCENT_COLOR))
        
        self.username_input = TextInput(hint_text="Enter ID", multiline=False, background_color=(1,1,1,0.1), foreground_color=(1,1,1,1), cursor_color=ACCENT_COLOR, padding=[10, 10])
        self.login_btn = Button(text="INITIALIZE CONNECTION", background_normal='', background_color=ACCENT_COLOR, bold=True)
        self.login_btn.bind(on_press=self.start_app)
        
        self.login_layout.add_widget(self.username_input)
        self.login_layout.add_widget(self.login_btn)
        
        self.root_layout.add_widget(self.login_layout)
        return self.root_layout

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def start_app(self, instance):
        self.username = self.username_input.text.strip() or "Node_1"
        self.root_layout.remove_widget(self.login_layout)
        self.setup_chat_ui()
        self.start_networking()

    def setup_chat_ui(self):
        # Header Info
        header = Label(text=f"CONNECTED AS: {self.username}", size_hint_y=0.05, color=ACCENT_COLOR, bold=True)
        self.root_layout.add_widget(header)

        # Chat History with Scroll
        self.scroll = ScrollView(size_hint=(1, 0.85), do_scroll_x=False)
        self.history = Label(text="", markup=True, size_hint_y=None, halign='left', valign='top', padding=[10, 10])
        self.history.bind(texture_size=self.history.setter('size'))
        self.scroll.add_widget(self.history)

        # Message Input Area
        self.input_area = BoxLayout(size_hint=(1, 0.1), spacing=10)
        self.msg_input = TextInput(hint_text="Secure packet message...", multiline=False, background_color=(1,1,1,0.05), foreground_color=(1,1,1,1), padding=[10, 10])
        self.send_btn = Button(text="SEND", size_hint_x=0.25, background_normal='', background_color=ACCENT_COLOR, bold=True)
        self.send_btn.bind(on_press=self.send_msg)

        self.input_area.add_widget(self.msg_input)
        self.input_area.add_widget(self.send_btn)

        self.root_layout.add_widget(self.scroll)
        self.root_layout.add_widget(self.input_area)

    def start_networking(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.sock.bind(('', 5000))
            threading.Thread(target=self.receive_msgs, daemon=True).start()
        except Exception as e:
            self.update_history(f"[color=ff3333]SYSTEM ERROR: {e}[/color]")

    def send_msg(self, instance):
        msg = self.msg_input.text
        if msg:
            timestamp = datetime.datetime.now().strftime("%H:%M")
            full_msg = f"{self.username}: {msg}"
            laptop_ip = '192.168.1.6' # Verify this matches your laptop's ipconfig
            
            try:
                self.sock.sendto(full_msg.encode(), (laptop_ip, 5000))
                # Local UI Update
                self.update_history(f"[b][color=33ccff]{timestamp} Me:[/color][/b]\n{msg}")
                self.msg_input.text = ""
            except Exception as e:
                self.update_history(f"[color=ff3333]FAIL: {e}[/color]")

    def receive_msgs(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                decoded = data.decode()
                timestamp = datetime.datetime.now().strftime("%H:%M")
                
                # Filter out our own broadcast if loopback occurs
                if not decoded.startswith(f"{self.username}:"):
                    sender, content = decoded.split(": ", 1) if ": " in decoded else (addr[0], decoded)
                    formatted = f"[b][color=aaaaaa]{timestamp} {sender}:[/color][/b]\n{content}"
                    Clock.schedule_once(lambda dt: self.update_history(formatted))
            except:
                break

    def update_history(self, message):
        self.history.text += message + "\n\n"
        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0))

if __name__ == "__main__":
    AkonApp().run()