import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window

# Modular Imports
import config
from network import AkonNetwork

class MessageBubble(BoxLayout):
    """Template for chat bubbles defined in akon.kv"""
    message = StringProperty("")
    sender = StringProperty("")
    time = StringProperty("")
    is_me = BooleanProperty(False)

class AkonApp(App):
    def build(self):
        Window.softinput_mode = "below_target"
        self.node_id = "Node_X"
        
        # Initialize the network engine
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        
        # Load the UI from akon.kv
        self.root_ui = Builder.load_file('akon.kv')
        return self.root_ui

    def start_session(self, user_id):
        """Triggered by the 'INITIALIZE' button in akon.kv"""
        self.node_id = user_id.strip() or "Node_X"
        if self.net.start():
            # In Phase 1, we can print status to console for debugging
            print(f"[*] Node {self.node_id} is now LIVE.")

    def send_broadcast(self, text):
        """Triggered by the 'SHOUT' button in akon.kv"""
        if text.strip():
            if self.net.broadcast(self.node_id, text):
                self.add_bubble_to_ui(text, self.node_id, is_me=True)

    def on_incoming(self, raw_data, sender_ip):
        """Handles packets caught by the network.py background thread"""
        if not raw_data.startswith(f"{self.node_id}:"):
            sender = raw_data.split(":")[0] if ":" in raw_data else sender_ip
            content = raw_data.split(": ", 1)[1] if ": " in raw_data else raw_data
            
            # Update UI safely from the background thread
            Clock.schedule_once(lambda dt: self.add_bubble_to_ui(content, sender, is_me=False))

    def add_bubble_to_ui(self, text, sender, is_me):
        """Instantiates a bubble and injects it into the ScrollView"""
        chat_list = self.root.ids.get('chat_list')
        if chat_list:
            bubble = MessageBubble(
                message=text,
                sender=sender,
                time=datetime.datetime.now().strftime("%H:%M"),
                is_me=is_me
            )
            chat_list.add_widget(bubble)
            
            # Auto-scroll to most recent message
            scroll_view = self.root.ids.get('scroll_view')
            if scroll_view:
                Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0))

if __name__ == "__main__":
    AkonApp().run()