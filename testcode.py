from kivy.app import App
from kivy.uix.button import Button
import serial
import time

ser = serial.Serial('COM8', 9600)
time.sleep(2)  # wait for Arduino reset

class MyApp(App):
    def build(self):
        btn = Button(text="Blink LED")
        btn.bind(on_press=self.send_signal)
        return btn

    def send_signal(self, instance):
        print("Button clicked!")
        ser.write(b'1')


MyApp().run()