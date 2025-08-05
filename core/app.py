"""
Main application class for Ben's Accessible Menu System.
Handles app initialization, scanning, key bindings, and navigation.
"""

import time
import threading
import tkinter as tk
import pyautogui
from pynput.keyboard import Controller

from core.config import (
    wm, SPACEBAR_LONG_PRESS_TIME, BACKWARD_SCAN_DELAY, SELECTION_DEBOUNCE_TIME,
    ENTER_SELECTION_DELAY, FOCUS_DELAY, FORCE_FOCUS_DELAY
)
from core.audio import speak
from core.key_listener import KeySequenceListener
from data.loaders import load_links
from system.monitoring import (
    minimize_terminal, minimize_on_screen_keyboard, monitor_and_minimize,
    monitor_app_focus, monitor_start_menu
)


class App(tk.Tk):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        self.title("Accessible Menu")
        self.geometry("960x540")  # Default, will adjust to screen size
        self.attributes("-fullscreen", True)
        self.configure(bg="black")
        self.current_frame = None
        self.buttons = []  # Holds buttons for scanning
        self.current_button_index = 0  # Current scanning index
        self.selection_enabled = True  # Flag to manage debounce for selection
        self.keyboard = Controller()  # Initialize the keyboard controller
        self.organized_links = load_links("shows.xlsx")
        self.spacebar_pressed = False
        self.long_spacebar_pressed = False
        self.start_time = 0
        self.backward_time_delay = BACKWARD_SCAN_DELAY  # Delay in seconds when long holding space
       
        # Add Close and Minimize buttons
        self.create_window_controls()

        # Minimize terminal and keyboard
        minimize_terminal()
        minimize_on_screen_keyboard()
        
        # Start monitoring for Chrome in a separate thread
        threading.Thread(target=monitor_and_minimize, args=(self,), daemon=True).start()

        # Start monitoring for Chrome's state and application focus
        threading.Thread(target=monitor_app_focus, args=("Accessible Menu",), daemon=True).start()

        # Start monitoring the Start Menu
        threading.Thread(target=monitor_start_menu, daemon=True).start()

        # Delay key bindings to ensure focus
        self.after(FOCUS_DELAY, self.bind_keys_for_scanning)

        # Focus Application
        self.after(FORCE_FOCUS_DELAY, lambda: self.force_focus())
        self.after(9000, lambda: pyautogui.click(x=25, y=25))

        self.menu_stack = []

        # Import here to avoid circular imports
        from ui.main_menu import MainMenuPage
        # Initialize the main menu
        print("Initializing the main menu...")
        self.show_frame(MainMenuPage)

    def force_focus(self):
        """Force the application window to focus."""
        self.focus_force()
        self.lift()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))
        print("Forced focus via Tkinter methods.")

    def create_window_controls(self):
        """Adds Close and Minimize buttons to the top of the app window."""
        control_frame = tk.Frame(self, bg="gray")  # Change background color to make it visible
        control_frame.pack(side="top", fill="x")

        minimize_button = tk.Button(
            control_frame, text="Minimize", bg="light blue", fg="black",
            command=self.iconify, font=("Arial", 12)
        )
        minimize_button.pack(side="right", padx=5, pady=5)

        close_button = tk.Button(
            control_frame, text="Close", bg="red", fg="white",
            command=self.destroy, font=("Arial", 12)
        )
        close_button.pack(side="right", padx=5, pady=5)

    def bind_keys_for_scanning(self):
        """Bind keyboard events for scanning functionality."""
        # Unbind any previous key events (if needed).
        self.unbind("<KeyPress-space>")
        self.unbind("<KeyRelease-space>")
        self.unbind("<KeyRelease-Return>")
        
        # Bind the keys on the main app (or you could bind them to self.current_frame if you prefer).
        self.bind("<KeyPress-space>", self.track_spacebar_hold)
        self.bind("<KeyRelease-space>", self.reset_spacebar_hold)
        self.bind("<KeyRelease-Return>", self.select_button)
        print("Key bindings activated.")

        # Start key sequence listener
        self.sequencer = KeySequenceListener(self)

        # Start spacebar hold tracking in a separate thread
        threading.Thread(target=self.monitor_spacebar_hold, daemon=True).start()

    def monitor_spacebar_hold(self):
        """Monitor spacebar hold duration for backward scanning."""
        while True:
            if self.spacebar_pressed and (time.time() - self.start_time >= SPACEBAR_LONG_PRESS_TIME):
                self.long_spacebar_pressed = True
                self.scan_backward()
                time.sleep(self.backward_time_delay)

    def track_spacebar_hold(self, event):
        """Track when spacebar is pressed down."""
        if not self.spacebar_pressed and not self.long_spacebar_pressed:
            self.spacebar_pressed = True
            self.start_time = time.time()

    def reset_spacebar_hold(self, event):
        """Handle spacebar release for forward scanning."""
        if self.spacebar_pressed:
            self.spacebar_pressed = False
            if not self.long_spacebar_pressed:
                self.scan_forward()
            else:
                self.long_spacebar_pressed = False
                self.start_time = time.time()

    def show_frame(self, frame_factory):
        """Display a new frame/page."""
        if self.current_frame:
            # Save the function (or lambda) that creates the current frame.
            self.menu_stack.append(self.current_frame_factory)
            self.current_frame.destroy()
        self.current_frame = frame_factory(self)
        self.current_frame.pack(expand=True, fill="both")
        self.current_frame_factory = frame_factory  # Save the factory for this frame
        self.buttons = self.current_frame.buttons
        self.current_button_index = 0
        if self.buttons:
            self.highlight_button(0)

    def show_previous_menu(self):
        """Go back to the previous menu."""
        if self.menu_stack:
            self.current_frame.destroy()
            previous_factory = self.menu_stack.pop()
            self.current_frame = previous_factory(self)
            self.current_frame.pack(expand=True, fill="both")
            self.current_frame_factory = previous_factory
            self.buttons = self.current_frame.buttons
            self.current_button_index = 0
            if self.buttons:
                self.highlight_button(0)
        else:
            from ui.main_menu import MainMenuPage
            self.show_frame(MainMenuPage)

    def scan_forward(self, event=None):
        """Advance to the next button and highlight it upon spacebar release."""
        if not self.selection_enabled or not self.buttons:
            return
        self.selection_enabled = False  # Disable selection temporarily
        
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
        self.highlight_button(self.current_button_index)
           
        # Speak the button's text if the frame matches
        from ui.main_menu import MainMenuPage
        from ui.entertainment_menu import EntertainmentMenuPage
        from ui.settings_menu import SettingsMenuPage
        from ui.library_menu import LibraryMenu
        from ui.games_menu import GamesPage
        from ui.communication_menu import CommunicationPageMenu
        
        if isinstance(self.current_frame, (
            MainMenuPage, EntertainmentMenuPage, SettingsMenuPage,
            LibraryMenu, GamesPage, CommunicationPageMenu
        )):
            speak(self.buttons[self.current_button_index]["text"])

        # Re-enable selection after a short delay
        threading.Timer(SELECTION_DEBOUNCE_TIME, self.enable_selection).start()

    def scan_backward(self, event=None):
        """Move to the previous button and highlight it."""
        if not self.selection_enabled or not self.buttons:
            return

        self.selection_enabled = False  # Disable selection temporarily
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
        self.highlight_button(self.current_button_index)

        # Speak the button's text if the frame matches
        from ui.main_menu import MainMenuPage
        from ui.entertainment_menu import EntertainmentMenuPage
        from ui.settings_menu import SettingsMenuPage
        from ui.library_menu import LibraryMenu
        from ui.games_menu import GamesPage
        from ui.communication_menu import CommunicationPageMenu
        
        if isinstance(self.current_frame, (
            MainMenuPage, EntertainmentMenuPage, SettingsMenuPage,
            LibraryMenu, GamesPage, CommunicationPageMenu
        )):
            speak(self.buttons[self.current_button_index]["text"])

        # Re-enable selection after a short delay
        threading.Timer(SELECTION_DEBOUNCE_TIME, self.enable_selection).start()

    def enable_selection(self):
        """Re-enable scanning and selection after the delay."""
        self.selection_enabled = True

    def select_button(self, event=None):
        """Select the currently highlighted button upon Enter key release with debounce and delay."""
        if self.selection_enabled and self.buttons:
            self.selection_enabled = False  # Disable selection temporarily
            self.buttons[self.current_button_index].invoke()  # Invoke the button action

            # Add delay for both scanning and selection after Enter key
            threading.Timer(ENTER_SELECTION_DELAY, self.enable_selection).start()  # Re-enable selection after 2 seconds

            self.sequencer.current_index = 0
            self.sequencer.last_key_time = None

    def highlight_button(self, index):
        """Highlight the button at the given index."""
        for i, btn in enumerate(self.buttons):
            if i == index:
                btn.config(bg="yellow", fg="black")
            else:
                btn.config(bg="light blue", fg="black")
        self.update()  # Refresh appearance

        # Auto-scroll so that the highlighted button is visible.
        if hasattr(self, "scroll_canvas"):
            try:
                btn = self.buttons[index]
                # Get button's absolute Y position and canvas's Y position.
                btn_y = btn.winfo_rooty()
                canvas_y = self.scroll_canvas.winfo_rooty()
                canvas_height = self.scroll_canvas.winfo_height()
                # If the button is not fully in view, adjust the yview.
                if btn_y < canvas_y or (btn_y + btn.winfo_height()) > (canvas_y + canvas_height):
                    relative_y = (btn_y - canvas_y) / self.scroll_canvas.bbox("all")[3]
                    self.scroll_canvas.yview_moveto(relative_y)
            except Exception as e:
                print(f"Error auto-scrolling: {e}")