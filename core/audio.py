"""
Audio and Text-to-Speech system for Ben's Accessible Menu.
Handles speech synthesis with queue management and thread safety.
"""

import threading
import queue
from pyttsx3 import init

# Initialize Text-to-Speech
engine = init()
speak_queue = queue.Queue()

def speak(text):
    """Add text to the speech queue, clearing any pending speech."""
    if speak_queue.qsize() >= 1:
        with speak_queue.mutex:
            speak_queue.queue.clear()
    speak_queue.put(text)

def play_speak_queue():
    """Background thread function to process the speech queue."""
    while True:
        text = speak_queue.get()
        if text is None:
            speak_queue.task_done()
            break
        engine.say(text)
        engine.runAndWait()
        speak_queue.task_done()

# Start the speech thread
speak_thread = threading.Thread(target=play_speak_queue, daemon=True)
speak_thread.start()

def stop_speech():
    """Stop the speech engine and clear the queue."""
    speak_queue.put(None)