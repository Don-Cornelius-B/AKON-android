import socket
import threading
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.window import Window

# --- UI Theme Palette ---
DARK_SPACE = (0.02, 0.02, 0.05, 1)  # Deep navy background
CYBER_BLUE = (0, 0.6, 0.9, 1)      # Accent color for user and buttons
DARK_GREY = (0.15, 0.15, 0.2, 1)   # Color for incoming message bubbles
TEXT_WHITE = (0.9, 0.9, 0.9, 1)

class AkonApp(App):
    def build(self):
        """Initializes the UI and enables the keyboard-aware layout."""
        self.title = "AKON GATEWAY"
        # Shifts the app view up so the keyboard doesn't cover the input box
        Window.softinput_mode = "below_target"
        
        self.root = AnchorLayout()
        
        # Apply global background
        with self.root.canvas.before:
            Color(*DARK_SPACE)
            self.bg = RoundedRectangle(pos=self.root.pos, size=self.root.size)
            self.root.bind(pos=self.update_bg, size=self.update_bg)

        # --- LOGIN SCREEN: Glass-Morphism Card ---
        self.login_card = BoxLayout(orientation='vertical', padding=30, spacing=20, 
                                    size_hint=(0.85, None), height=320)
        
        with self.login_card.canvas.before:
            Color(1, 1, 1, 0.05) 
            self.card_bg = RoundedRectangle(pos=self.login_card.pos, size=self.login_card.size, radius=[20,])
            Color(*CYBER_BLUE)
            self.card_border = Line(rounded_rectangle=[0,0,0,0,20], width=1.2)
            self.login_card.bind(pos=self.update_card, size=self.update_card)

        self.login_card.add_widget(Label(text="[b]AKON[/b]\n[size=14]P2P DISCOVERY NODE[/size]", 
                                        markup=True, halign='center', font_size=28, color=CYBER_BLUE))
        
        self.id_input = TextInput(hint_text="Enter Node ID", multiline=False, size_hint_y=None, height=50,
                                  background_color=(0,0,0,0), foreground_color=TEXT_WHITE, cursor_color=CYBER_BLUE,
                                  padding=[15, 15], hint_text_color=(0.5, 0.5, 0.5, 1))
        
        self.join_btn = Button(text="INITIALIZE GATEWAY", background_normal='', background_color=CYBER_BLUE,
                               bold=True, size_hint_y=None, height=55)
        self.join_btn.bind(on_press=self.start_session)
        
        self.login_card.add_widget(self.id_input)
        self.login_card.add_widget(self.join_btn)
        
        self.root.add_widget(self.login_card)
        return self.root

    def update_bg(self, *args):
        self.bg.pos = self.root.pos
        self.bg.size = self.root.size

    def update_card(self, instance, value):
        self.card_bg.pos = instance.pos
        self.card_bg.size = instance.size
        self.card_border.rounded_rectangle = [instance.x, instance.y, instance.width, instance.height, 20]

    def start_session(self, instance):
        """Sets the Node ID and transitions to the chat dashboard."""
        self.node_id = self.id_input.text.strip() or "Node_X"
        self.root.remove_widget(self.login_card)
        self.setup_chat_dashboard()
        self.init_p2p_engine()

    def setup_chat_dashboard(self):
        """Builds the main chat interface with directional bubbles."""
        self.root.anchor_x = 'center'
        self.root.anchor_y = 'top'
        chat_main = BoxLayout(orientation='vertical', padding=[10, 20, 10, 10], spacing=10)

        chat_main.add_widget(Label(text=f"ACTIVE NODE: {self.node_id} (Broadcasting)", 
                                   size_hint_y=None, height=30, color=CYBER_BLUE, bold=True))

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.chat_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=[5, 10])
        self.chat_list.bind(minimum_height=self.chat_list.setter('height'))
        self.scroll.add_widget(self.chat_list)

        # Message Input Area
        dock_container = BoxLayout(size_hint_y=None, height=70, spacing=10, padding=[5, 10])
        self.entry = TextInput(hint_text="Broadcast to neighbors...", multiline=False,
                               background_color=(1,1,1,0.05), foreground_color=TEXT_WHITE, padding=[12, 12])
        self.send_btn = Button(text="SHOUT", size_hint_x=0.25, background_normal='', background_color=CYBER_BLUE, bold=True)
        self.send_btn.bind(on_press=self.send_broadcast)

        dock_container.add_widget(self.entry)
        dock_container.add_widget(self.send_btn)

        chat_main.add_widget(self.scroll)
        chat_main.add_widget(dock_container)
        self.root.add_widget(chat_main)

    def init_p2p_engine(self):
        """Initializes the UDP socket for zero-config P2P broadcasting."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allows for immediate port reuse and enables broadcast capability
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            self.sock.bind(('', 5000))
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except Exception as e:
            self.add_message(f"Network Error: {e}", is_me=False)

    def send_broadcast(self, instance):
        """Shouts a packet to the entire local network."""
        val = self.entry.text
        if val:
            try:
                # 255.255.255.255 targets every device in the WiFi range
                self.sock.sendto(f"{self.node_id}: {val}".encode(), ('255.255.255.255', 5000))
                self.add_message(val, is_me=True)
                self.entry.text = ""
            except Exception as e:
                self.add_message(f"Transmission Error: {e}", is_me=False)

    def receive_loop(self):
        """Continuously monitors Port 5000 for incoming data."""
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                text = data.decode()
                # Do not display our own shouts in the chat
                if not text.startswith(f"{self.node_id}:"):
                    sender = text.split(":")[0] if ":" in text else addr[0]
                    content = text.split(": ", 1)[1] if ": " in text else text
                    Clock.schedule_once(lambda dt: self.add_message(content, is_me=False, sender=sender))
            except:
                break

    def add_message(self, text, is_me=True, sender=""):
        """Creates a stylized bubble and adds it to the chat flow."""
        time_tag = datetime.datetime.now().strftime("%H:%M")
        bubble_container = BoxLayout(orientation='vertical', size_hint=(0.75, None), spacing=2)
        
        # Align: Me (Right/Blue), Neighbors (Left/Grey)
        bubble_container.pos_hint = {'right': 1} if is_me else {'left': 1}
        bubble_color = CYBER_BLUE if is_me else DARK_GREY
        
        display_text = f"[b]{'Me' if is_me else sender}[/b]  [size=12]{time_tag}[/size]\n{text}"
        msg_label = Label(text=display_text, markup=True, padding=[12, 12], size_hint_y=None, halign='left')
        msg_label.bind(texture_size=msg_label.setter('size'))
        
        with msg_label.canvas.before:
            Color(*bubble_color)
            RoundedRectangle(pos=msg_label.pos, size=msg_label.size, radius=[15,])
            msg_label.bind(pos=self.update_bubble, size=self.update_bubble)

        bubble_container.add_widget(msg_label)
        bubble_container.height = msg_label.texture_size[1] + 20
        self.chat_list.add_widget(bubble_container)
        
        # Auto-scroll to the bottom for the newest message
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0))

    def update_bubble(self, instance, value):
        """Maintains the bubble's background alignment."""
        instance.canvas.before.children[-1].pos = instance.pos
        instance.canvas.before.children[-1].size = instance.size

if __name__ == "__main__":
    AkonApp().run()