"""
Key sequence listener for Ben's Accessible Menu.
Handles the triple-enter sequence to close Chrome and return focus.
"""

import time
import threading
from pynput import keyboard
from browser.integration import close_chrome_cleanly
from system.monitoring import bring_application_to_focus


class KeySequenceListener:
    def __init__(self, app):
        self.app = app
        self.sequence = ["enter", "enter", "enter"]  # Define the key sequence
        self.current_index = 0
        self.last_key_time = None
        self.timeout = 8  # Timeout for completing the sequence (seconds)
        self.held_keys = set()  # Track keys that are currently held
        self.recently_pressed = set()  # To debounce key presses
        self.start_listener()

    def start_listener(self):
        def on_press(key):
            try:
                key_name = (
                    key.char.lower() if hasattr(key, 'char') and key.char else str(key).split('.')[-1].lower()
                )
                if key_name in self.recently_pressed:  # Ignore key if already recently pressed
                    return

                self.recently_pressed.add(key_name)
                self.check_key(key_name)
            except AttributeError:
                pass

        def on_release(key):
            try:
                key_name = (
                    key.char.lower() if hasattr(key, 'char') and key.char else str(key).split('.')[-1].lower()
                )
                self.recently_pressed.discard(key_name)  # Allow key to be pressed again
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()

    def check_key(self, key_name):
        # Handle timeout for the sequence
        if self.last_key_time and time.time() - self.last_key_time > self.timeout:
            print("Sequence timeout. Resetting index.")
            self.current_index = 0  # Reset sequence on timeout

        self.last_key_time = time.time()

        # Check the current key against the sequence
        if key_name == self.sequence[self.current_index]:
            print(f"Matched {key_name} at index {self.current_index}")
            self.current_index += 1  # Move to the next key in the sequence
            if self.current_index == len(self.sequence):  # Full sequence detected
                self.handle_sequence()
                self.current_index = 0  # Reset sequence index
        else:
            print(f"Key mismatch or invalid input. Resetting sequence.")
            self.current_index = 0  # Reset on invalid input

    def handle_sequence(self):
        print("Key sequence detected. Closing Chrome and focusing application.")
        threading.Thread(target=self.perform_actions, daemon=True).start()

    def perform_actions(self):
        close_chrome_cleanly()

        # Introduce a delay before resuming scanning/selecting
        print("Adding delay before resuming scanning/selecting...")
        time.sleep(2)  # Delay in seconds; adjust as needed

        bring_application_to_focus()