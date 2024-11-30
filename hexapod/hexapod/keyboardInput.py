import pynput

class KeyboardInput:
    def __init__(self):
        self.listener = None

    def keyListener(self, callback):
        def on_press(key):
            try:
                callback(key.char)
            except AttributeError:
                callback(key)
        self.listener = pynput.keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
