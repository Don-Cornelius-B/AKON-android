import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window

import config
from network import AkonNetwork

KV_INTERFACE = """
#:import config config

<MessageBubble>:
    orientation: 'vertical'
    size_hint: 0.8, None
    height: self.minimum_height
    padding: [12, 10]
    pos_hint: {'right': 1} if self.is_me else {'left': 1}
    canvas.before:
        Color:
            rgba: config.MY_BUBBLE if self.is_me else config.THEIR_BUBBLE
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15, 15, (0, 15) if self.is_me else (15, 0), 15]
    Label:
        text: root.sender + "  " + root.time
        font_size: '10sp'
        size_hint_y: None
        height: 15
        halign: 'left'
        text_size: self.width, None
    Label:
        text: root.message
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None

ScreenManager:
    Screen:
        name: 'login_screen'
        AnchorLayout:
            canvas.before:
                Color:
                    rgba: config.DARK_SPACE
                Rectangle:
                    pos: self.pos
                    size: self.size
            BoxLayout:
                orientation: 'vertical'
                size_hint: 0.85, None
                height: 280
                padding: 25
                spacing: 20
                canvas.before:
                    Color:
                        rgba: 1, 1, 1, 0.05
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20,]
                Label:
                    text: "AKON IDENTITY"
                    bold: True
                    font_size: '22sp'
                TextInput:
                    id: user_input
                    hint_text: "Node Name..."
                    multiline: False
                Button:
                    text: "INITIALIZE GATEWAY"
                    on_release: app.start_gateway(user_input.text)

    Screen:
        name: 'chat_screen'
        BoxLayout:
            orientation: 'vertical'
            canvas.before:
                Color:
                    rgba: config.DARK_SPACE
                Rectangle:
                    pos: self.pos
                    size: self.size
            ScrollView:
                on_kv_post: app.scroller = self 
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [15, 15]
                    spacing: 12
                    on_kv_post: app.chat_list = self
            BoxLayout:
                size_hint_y: 0.12
                padding: 8
                TextInput:
                    id: shout_box
                    multiline: False
                Button:
                    text: "SHOUT"
                    size_hint_x: 0.25
                    on_release: app.send_shout(shout_box)
"""

class MessageBubble(BoxLayout):
    message = StringProperty("")
    sender = StringProperty("")
    time = StringProperty("")
    is_me = BooleanProperty(False)

class AkonGateway(App):
    chat_list = ObjectProperty(None)
    scroller = ObjectProperty(None)

    def build(self):
        Window.softinput_mode = "below_target"
        self.node_id = "Node_X"
        self.net = AkonNetwork(on_message_callback=self.on_incoming)
        return Builder.load_string(KV_INTERFACE)

    def start_gateway(self, user_name):
        self.node_id = user_name.strip() or "Node_X"
        self.root.current = 'chat_screen'
        if self.net.start():
            print(f"[*] Mesh Gateway Active: {self.node_id}")

    def send_shout(self, text_input):
        msg = text_input.text
        if msg.strip():
            self.render_bubble(msg, self.node_id, is_me=True)
            if self.net.broadcast(self.node_id, msg):
                text_input.text = ""

    def render_bubble(self, text, sender, is_me=False):
        try:
            if self.chat_list:
                bubble = MessageBubble(
                    message=text, sender=sender,
                    time=datetime.datetime.now().strftime("%H:%M"),
                    is_me=is_me
                )
                self.chat_list.add_widget(bubble)
                if self.scroller:
                    Clock.schedule_once(lambda dt: setattr(self.scroller, 'scroll_y', 0))
        except Exception as e:
            print(f"[!] UI Render Error: {e}")

    def on_incoming(self, data, addr):
        try:
            if ":" in data:
                sender, content = data.split(":", 1)
                if sender != self.node_id:
                    Clock.schedule_once(lambda dt: self.render_bubble(content, sender, is_me=False))
        except:
            pass

if __name__ == "__main__":
    AkonGateway().run()