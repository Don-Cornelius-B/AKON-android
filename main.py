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
from kivy.core.window import Window

# --- UI Theme Constants ---
BACKGROUND_COLOR = (0.05, 0.05, 0.1, 1)  # Midnight Blue
ACCENT_COLOR = (0, 0.7, 1, 1)            # Cyber Blue
TEXT_COLOR = (1, 1, 1, 1)

class AkonApp(App):
    def build(self):
        """Initializes the AKON UI and handles window/keyboard events."""
        self.title = "AKON P2P GATEWAY"
        
        # Configure the window to adjust when the keyboard appears
        Window.softinput_mode = "below_target"
        
        self.root_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        with self.root_layout.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.rect = RoundedRectangle(pos=self.root_layout.pos, size=self.root_layout.size)
            self.root_layout.bind(pos=self.update_canvas, size=self.update_canvas)

        # --- Initial Login Interface ---
        self.login_container = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.8, 0.4), pos_hint={'center_x': 0.5})
        self.login_container.add_widget(Label(text="[b]AKON[/b]\nP2P Node", font_size=32, markup=True, color=ACCENT_COLOR))
        
        self.id_input = TextInput(hint_text="Enter Node ID", multiline=False, background_color=(1,1,1,0.1), foreground_color=TEXT_COLOR, padding=[10, 10])
        self.start_btn = Button(text="INITIALIZE", background_normal='', background_color=ACCENT_COLOR, bold=True)
        self.start_btn.bind(on_press=self.enter_chat)
        
        self.login_container.add_widget(self.id_input)
        self.login_container.add_widget(self.start_btn)
        self.root_layout.add_widget(self.login_container)
        
        return self.root_layout

    def update_canvas(self, instance, value):
        """Maintains background rectangle alignment during resizing."""
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def enter_chat(self, instance):
        """Transfers the user from login to the active chat interface."""
        self.username = self.id_input.text.strip() or "Node_1"
        self.root_layout.remove_widget(self.login_container)
        self.setup_main_interface()
        self.activate_network_service()

    def setup_main_interface(self):
        """Builds the primary chat window with a scrollable history and fixed input."""
        # Active ID Header
        self.root_layout.add_widget(Label(text=f"ACTIVE NODE: {self.username}", size_hint_y=0.05, color=ACCENT_COLOR, bold=True))

        # Scrollable Chat History
        self.scroll_area = ScrollView(size_hint=(1, 0.85), do_scroll_x=False)
        self.chat_log = Label(text="", markup=True, size_hint_y=None, halign='left', valign='top', padding=[15, 15])
        self.chat_log.bind(texture_size=self.chat_log.setter('size'))
        self.scroll_area.add_widget(self.chat_log)

        # Keyboard-Aware Input Area
        # Using a fixed size_hint_y for the input area keeps it consistent
        self.input_dock = BoxLayout(size_hint=(1, None), height=60, spacing=10)
        self.entry_field = TextInput(hint_text="Type packet data...", multiline=False, background_color=(1,1,1,0.05), foreground_color=TEXT_COLOR, padding=[10, 10])
        self.send_trigger = Button(text="SEND", size_hint_x=0.25, background_normal='', background_color=ACCENT_COLOR, bold=True)
        self.send_trigger.bind(on_press=self.dispatch_packet)

        self.input_dock.add_widget(self.entry_field)
        self.input_dock.add_widget(self.send_trigger)

        self.root_layout.add_widget(self.scroll_area)
        self.root_layout.add_widget(self.input_dock)

    def activate_network_service(self):
        """Starts the background UDP listener thread."""
        self.socket_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket_service.bind(('', 5000))
            threading.Thread(target=self.packet_listener, daemon=True).start()
        except Exception as e:
            self.log_event(f"[color=ff3333]BIND ERROR: {e}[/color]")

    def dispatch_packet(self, instance):
        """Encodes and sends the message to the laptop node."""
        content = self.entry_field.text
        if content:
            stamp = datetime.datetime.now().strftime("%H:%M")
            payload = f"{self.username}: {content}"
            # Ensure this matches your current laptop IPv4 from ipconfig
            target_ip = '192.168.1.6' 
            
            try:
                self.socket_service.sendto(payload.encode('utf-8'), (target_ip, 5000))
                self.log_event(f"[b][color=33ccff]{stamp} Me:[/color][/b]\n{content}")
                self.entry_field.text = ""
            except Exception as e:
                self.log_event(f"[color=ff3333]SEND FAILED: {e}[/color]")

    def packet_listener(self):
        """Background thread for receiving incoming P2P data."""
        while True:
            try:
                data, addr = self.socket_service.recvfrom(1024)
                text = data.decode('utf-8')
                stamp = datetime.datetime.now().strftime("%H:%M")
                
                if not text.startswith(f"{self.username}:"):
                    sender = text.split(": ", 1)[0] if ": " in text else addr[0]
                    msg_body = text.split(": ", 1)[1] if ": " in text else text
                    display = f"[b][color=aaaaaa]{stamp} {sender}:[/color][/b]\n{msg_body}"
                    Clock.schedule_once(lambda dt: self.log_event(display))
            except:
                break

    def log_event(self, text):
        """Appends text to the UI log and handles auto-scrolling."""
        self.chat_log.text += text + "\n\n"
        Clock.schedule_once(lambda dt: setattr(self.scroll_area, 'scroll_y', 0))

if __name__ == "__main__":
    AkonApp().run()