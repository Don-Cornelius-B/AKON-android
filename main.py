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
    """Matches the <MessageBubble> template in akon.kv"""
    message = StringProperty("")
    sender = StringProperty("")
    time = StringProperty("")
    is_me = BooleanProperty(False)

class AkonApp(App):
    def build(self):
        # Keeps input bar above the Android keyboard
        Window.softinput_mode = "below_target"
        self.node_id = "Node_X"
        
        # Initialize the network engine but wait for 'Initialize' to start it
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        
        return Builder.load_file('akon.kv')

    def start_session(self, user_id):
        """Starts the P2P engine and switches to Chat Screen"""
        self.node_id = user_id.strip() or "Node_X"
        if self.net.start():
            self.root.current = 'chat_screen'

    def send_broadcast(self, text_input_widget):
        """Handles the 'SHOUT' button logic without crashing"""
        text = text_input_widget.text
        if text.strip():
            if self.net.broadcast(self.node_id, text):
                self.add_bubble_to_ui(text, self.node_id, is_me=True)
                # Clear the input field after sending
                text_input_widget.text = ""

    def on_incoming(self, raw_data, sender_ip):
        """Processes incoming UDP packets from the background thread"""
        if not raw_data.startswith(f"{self.node_id}:"):
            sender = raw_data.split(":")[0] if ":" in raw_data else sender_ip
            content = raw_data.split(": ", 1)[1] if ": " in raw_data else raw_data
            
            # Use Clock to safely update UI from a non-main thread
            Clock.schedule_once(lambda dt: self.add_bubble_to_ui(content, sender, is_me=False))

    def add_bubble_to_ui(self, text, sender, is_me):
        """Finds the correct Screen and adds the message bubble"""
        try:
            chat_screen = self.root.get_screen('chat_screen')
            chat_list = chat_screen.ids.chat_list
            
            bubble = MessageBubble(
                message=text,
                sender=sender,
                time=datetime.datetime.now().strftime("%H:%M"),
                is_me=is_me
            )
            chat_list.add_widget(bubble)
            
            # Scroll to the bottom to show the latest message
            scroll_view = chat_screen.ids.scroll_view
            Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0))
        except Exception as e:
            print(f"UI Update Error: {e}")

if __name__ == "__main__":
    AkonApp().run()