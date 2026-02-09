import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
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
    # This stores our network engine
    net = ObjectProperty(None)

    def build(self):
        Window.softinput_mode = "below_target"
        self.node_id = "Node_X"
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        
        # Returns the ScreenManager defined in akon.kv
        return Builder.load_file('akon.kv')

    def start_session(self, user_id):
        """Called by the INITIALIZE button"""
        self.node_id = user_id.strip() or "Node_X"
        if self.net.start():
            # Switch to the Chat Screen
            self.root.current = 'chat_screen'

    def send_broadcast(self, text_input):
        """Sends the message and clears the input field"""
        text = text_input.text
        if text.strip():
            if self.net.broadcast(self.node_id, text):
                self.add_bubble_to_ui(text, self.node_id, is_me=True)
                text_input.text = ""

    def on_incoming(self, raw_data, sender_ip):
        if not raw_data.startswith(f"{self.node_id}:"):
            sender = raw_data.split(":")[0] if ":" in raw_data else sender_ip
            content = raw_data.split(": ", 1)[1] if ": " in raw_data else raw_data
            Clock.schedule_once(lambda dt: self.add_bubble_to_ui(content, sender, is_me=False))

    def add_bubble_to_ui(self, text, sender, is_me):
        # We find the chat_list inside the 'chat_screen'
        chat_screen = self.root.get_screen('chat_screen')
        chat_list = chat_screen.ids.chat_list
        
        bubble = MessageBubble(
            message=text, sender=sender,
            time=datetime.datetime.now().strftime("%H:%M"),
            is_me=is_me
        )
        chat_list.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(chat_screen.ids.scroll_view, 'scroll_y', 0))

if __name__ == "__main__":
    AkonApp().run()