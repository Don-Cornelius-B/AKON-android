import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class AkonApp(App):
    def build(self):
        self.title = "AKON P2P"
        # Root Layout
        self.root_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # --- STEP 1: Login Screen (Shown at Start) ---
        self.login_layout = BoxLayout(orientation='vertical', spacing=10)
        self.login_layout.add_widget(Label(text="Welcome to AKON", font_size=24))
        self.username_input = TextInput(hint_text="Enter your username", multiline=False)
        self.login_btn = Button(text="Start Chatting", background_color=(0, 0.7, 1, 1))
        self.login_btn.bind(on_press=self.start_app)
        
        self.login_layout.add_widget(self.username_input)
        self.login_layout.add_widget(self.login_btn)
        
        self.root_layout.add_widget(self.login_layout)
        return self.root_layout

    def start_app(self, instance):
        # Capture username and switch UI
        self.username = self.username_input.text.strip() or "User"
        self.root_layout.remove_widget(self.login_layout)
        self.setup_chat_ui()
        self.start_networking()

    def setup_chat_ui(self):
        # Chat History
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.history = Label(text=f"[b]Logged in as {self.username}[/b]\n", 
                             markup=True, size_hint_y=None, halign='left', valign='top')
        self.history.bind(texture_size=self.history.setter('size'))
        self.scroll.add_widget(self.history)

        # Message Input Area
        self.input_area = BoxLayout(size_hint=(1, 0.2), spacing=5)
        self.msg_input = TextInput(hint_text="Type a message...", multiline=False)
        self.send_btn = Button(text="Send", size_hint_x=0.3)
        self.send_btn.bind(on_press=self.send_msg)

        self.input_area.add_widget(self.msg_input)
        self.input_area.add_widget(self.send_btn)

        self.root_layout.add_widget(self.scroll)
        self.root_layout.add_widget(self.input_area)

    def start_networking(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 5000)) # Bind to all interfaces on port 5000
        threading.Thread(target=self.receive_msgs, daemon=True).start()

    def send_msg(self, instance):
        msg = self.msg_input.text
        if msg:
            full_msg = f"{self.username}: {msg}"
            
            # --- THE FIX ---
            # Replace '192.168.137.XX' with your laptop's actual last two digits
            laptop_ip = '192.168.1.6' 
            self.sock.sendto(full_msg.encode(), (laptop_ip, 5000)) 
            # ---------------

            self.update_history(f"[color=33ccff]Me:[/color] {msg}")
            self.msg_input.text = ""

    def receive_msgs(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                # Ensure we don't display our own broadcasted message
                if not data.decode().startswith(f"{self.username}:"):
                    Clock.schedule_once(lambda dt: self.update_history(data.decode()))
            except:
                break

    def update_history(self, message):
        self.history.text += message + "\n"

if __name__ == "__main__":
    AkonApp().run()