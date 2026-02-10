import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
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
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        return Builder.load_file('akon.kv')

    def start_session(self, user_id):
        self.node_id = user_id.strip() or "Node_X"
        if self.net.start():
            self.root.current = 'chat_screen'

    def send_broadcast(self, text_input_widget):
        """Fixed: Instant local feedback + Mesh broadcast"""
        text = text_input_widget.text
        if text.strip():
            # 1. Update your own screen immediately
            self.add_bubble_to_ui(text, self.node_id, is_me=True)
            
            # 2. Send to the network for others
            if self.net.broadcast(self.node_id, text):
                text_input_widget.text = ""

    def on_incoming(self, raw_data, sender_ip):
        """Processes packets from other nodes"""
        if not raw_data.startswith(f"{self.node_id}:"):
            sender = raw_data.split(":")[0] if ":" in raw_data else sender_ip
            content = raw_data.split(": ", 1)[1] if ": " in raw_data else raw_data
            Clock.schedule_once(lambda dt: self.add_bubble_to_ui(content, sender, is_me=False))

    def add_bubble_to_ui(self, text, sender, is_me):
        try:
            chat_screen = self.root.get_screen('chat_screen')
            chat_list = chat_screen.ids.chat_list
            bubble = MessageBubble(
                message=text, sender=sender,
                time=datetime.datetime.now().strftime("%H:%M"),
                is_me=is_me
            )
            chat_list.add_widget(bubble)
            scroll_view = chat_screen.ids.scroll_view
            Clock.schedule_once(lambda dt: setattr(scroll_view, 'scroll_y', 0))
        except Exception as e:
            print(f"UI Error: {e}")

if __name__ == "__main__":
    AkonApp().run()