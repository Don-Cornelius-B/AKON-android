import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window

import config
from network import AkonNetwork

class MessageBubble(BoxLayout):
    message = StringProperty("")
    sender = StringProperty("")
    time = StringProperty("")
    is_me = BooleanProperty(False)

class AkonApp(App):
    def build(self):
        Window.softinput_mode = "below_target"
        self.node_id = "Node_X"
        # Initialize network but DON'T start it yet
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        return Builder.load_file('akon.kv')

    def start_session(self, user_id):
        """Starts the network and switches screens safely"""
        self.node_id = user_id.strip() or "Node_X"
        if self.net.start():
            # Use the ScreenManager ID to switch
            self.root.current = 'chat_screen'

    def send_broadcast(self, text_input):
        """Fixed: Uses local IDs to avoid global lookup crashes"""
        text = text_input.text
        if text.strip() and self.net.broadcast(self.node_id, text):
            self.add_bubble_to_ui(text, self.node_id, is_me=True)
            text_input.text = ""

    def on_incoming(self, raw_data, sender_ip):
        if not raw_data.startswith(f"{self.node_id}:"):
            sender = raw_data.split(":")[0] if ":" in raw_data else sender_ip
            content = raw_data.split(": ", 1)[1] if ": " in raw_data else raw_data
            Clock.schedule_once(lambda dt: self.add_bubble_to_ui(content, sender, is_me=False))

    def add_bubble_to_ui(self, text, sender, is_me):
        # Safely find the screen and its list
        chat_screen = self.root.get_screen('chat_screen')
        target_list = chat_screen.ids.chat_list
        
        bubble = MessageBubble(
            message=text, sender=sender,
            time=datetime.datetime.now().strftime("%H:%M"),
            is_me=is_me
        )
        target_list.add_widget(bubble)