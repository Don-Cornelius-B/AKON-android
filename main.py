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

# --- Professional UI Styling ---
CYBER_NAVY = (0.05, 0.08, 0.15, 1)
GLOW_BLUE = (0, 0.75, 1, 1)

class AkonApp(App):
    def build(self):
        """Builds the AKON interface and sets up mobile-specific window behavior."""
        self.title = "AKON P2P DISCOVERY"
        # Forces the app layout to shift up when the virtual keyboard opens
        Window.softinput_mode = "below_target"
        
        self.root_node = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        with self.root_node.canvas.before:
            Color(*CYBER_NAVY)
            self.bg_rect = RoundedRectangle(pos=self.root_node.pos, size=self.root_node.size)
            self.root_node.bind(pos=self.update_ui_geometry, size=self.update_ui_geometry)

        # --- Login and Discovery Initialization ---
        self.init_layout = BoxLayout(orientation='vertical', spacing=25, size_hint=(0.85, 0.45), pos_hint={'center_x': 0.5})
        self.init_layout.add_widget(Label(
            text="[b]AKON[/b]\nNode Discovery Active", 
            font_size=34, 
            markup=True, 
            color=GLOW_BLUE, 
            halign='center'
        ))
        
        self.id_input = TextInput(
            hint_text="Assign Node ID", 
            multiline=False, 
            background_color=(1,1,1,0.08), 
            foreground_color=(1,1,1,1),
            padding=[15, 15]
        )
        
        self.join_btn = Button(
            text="START DISCOVERY", 
            background_normal='', 
            background_color=GLOW_BLUE, 
            bold=True,
            font_size=18
        )
        self.join_btn.bind(on_press=self.launch_chat_session)
        
        self.init_layout.add_widget(self.id_input)
        self.init_layout.add_widget(self.join_btn)
        self.root_node.add_widget(self.init_layout)
        
        return self.root_node

    def update_ui_geometry(self, *args):
        """Ensures the background color scales with the window size."""
        self.bg_rect.pos = self.root_node.pos
        self.bg_rect.size = self.root_node.size

    def launch_chat_session(self, instance):
        """Switches UI to chat mode and initializes the networking thread."""
        self.node_id = self.id_input.text.strip() or "Mobile_Node"
        self.root_node.remove_widget(self.init_layout)
        self.setup_chat_dashboard()
        self.start_p2p_engine()

    def setup_chat_dashboard(self):
        """Creates the scrollable history and the keyboard-aligned input field."""
        self.root_node.add_widget(Label(
            text=f"ACTIVE NODE: {self.node_id}", 
            size_hint_y=0.06, 
            color=GLOW_BLUE, 
            bold=True
        ))

        self.scroll_view = ScrollView(size_hint=(1, 0.84))
        self.message_log = Label(
            text="", 
            markup=True, 
            size_hint_y=None, 
            halign='left', 
            valign='top', 
            padding=[20, 20]
        )
        self.message_log.bind(texture_size=self.message_log.setter('size'))
        self.scroll_view.add_widget(self.message_log)

        # Input Dock remains at the bottom, shifting with the keyboard
        self.input_dock = BoxLayout(size_hint=(1, None), height=65, spacing=12)
        self.msg_field = TextInput(
            hint_text="Broadcast packet data...", 
            multiline=False, 
            padding=[12, 12],
            background_color=(1,1,1,0.1),
            foreground_color=(1,1,1,1)
        )
        self.shout_btn = Button(
            text="SHOUT", 
            size_hint_x=0.28, 
            background_normal='', 
            background_color=GLOW_BLUE, 
            bold=True
        )
        self.shout_btn.bind(on_press=self.dispatch_broadcast)

        self.input_dock.add_widget(self.msg_field)
        self.input_dock.add_widget(self.shout_btn)
        
        self.root_node.add_widget(self.scroll_view)
        self.root_node.add_widget(self.input_dock)

    def start_p2p_engine(self):
        """Binds the socket for broadcast communication and starts the listener."""
        self.net_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Allows reusing the same port if the app restarts quickly
        self.net_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Enables sending to the broadcast address (255.255.255.255)
        self.net_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        try:
            self.net_socket.bind(('', 5000))
            threading.Thread(target=self.incoming_packet_handler, daemon=True).start()
        except Exception as err:
            self.post_log_entry(f"[color=ff4444]SYS_ERROR: {err}[/color]")

    def dispatch_broadcast(self, instance):
        """Sends the message to every listener on the local network segment."""
        msg_text = self.msg_field.text
        if msg_text:
            time_tag = datetime.datetime.now().strftime("%H:%M")
            full_packet = f"{self.node_id}: {msg_text}"
            
            try:
                # Shout to the entire local network
                self.net_socket.sendto(full_packet.encode('utf-8'), ('255.255.255.255', 5000))
                self.post_log_entry(f"[b][color=33ccff]{time_tag} ME:[/color][/b]\n{msg_text}")
                self.msg_field.text = ""
            except Exception as err:
                self.post_log_entry(f"[color=ff4444]FAILED_SEND: {err}[/color]")

    def incoming_packet_handler(self):
        """Continuously monitors Port 5000 for incoming broadcast traffic."""
        while True:
            try:
                raw_data, remote_addr = self.net_socket.recvfrom(1024)
                decoded_msg = raw_data.decode('utf-8')
                
                # Filter out our own shouts
                if not decoded_msg.startswith(f"{self.node_id}:"):
                    time_tag = datetime.datetime.now().strftime("%H:%M")
                    # Display the sender's ID or IP address
                    sender_id = decoded_msg.split(": ", 1)[0] if ": " in decoded_msg else remote_addr[0]
                    content = decoded_msg.split(": ", 1)[1] if ": " in decoded_msg else decoded_msg
                    
                    entry = f"[b][color=aaaaaa]{time_tag} {sender_id}:[/color][/b]\n{content}"
                    Clock.schedule_once(lambda dt: self.post_log_entry(entry))
            except:
                break

    def post_log_entry(self, content):
        """Adds a new message to the history and forces an auto-scroll."""
        self.message_log.text += content + "\n\n"
        # Ensures the scroll view stays at the most recent message
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0))

if __name__ == "__main__":
    AkonApp().run()