"""
Main menu page for Ben's Accessible Menu System.
Provides access to Emergency, Settings, Communication, and Entertainment.
"""

import time
import threading
import tkinter as tk

from ui.menu_base import MenuFrame
from core.audio import speak
from core.config import wm


class MainMenuPage(MenuFrame):
    """Main menu with Emergency, Settings, Communication, and Entertainment options."""
    
    def __init__(self, parent):
        super().__init__(parent, "Main Menu")
        self.buttons = []  # Store buttons for scanning
        self.current_button_index = 0  # Initialize scanning index
        self.selection_enabled = True  # Flag to manage debounce for selection

        # Create the grid layout for 4 large buttons
        grid_frame = tk.Frame(self, bg="black")
        grid_frame.pack(expand=True, fill="both")

        # Define buttons with their commands and labels
        buttons = [
            ("Emergency", self.emergency_alert, "Emergency Alert"),
            ("Settings", lambda: parent.show_frame(self._get_settings_page(parent)), "Settings Menu"),
            ("Communication", lambda: parent.show_frame(self._get_communication_page(parent)), "Communication Menu"),
            ("Entertainment", lambda: parent.show_frame(self._get_entertainment_page(parent)), "Entertainment Menu"),
        ]

        for i, (text, command, speak_text) in enumerate(buttons):
            row, col = divmod(i, 2)  # Calculate row and column for 2x2 layout
            btn = tk.Button(
                grid_frame,
                text=text,
                font=("Arial Black", 36),
                bg="light blue",
                fg="black",
                activebackground="yellow",
                activeforeground="black",
                command=lambda c=command, s=speak_text: self.on_select(c, s),
                wraplength=850,  # Wrap text for better display
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)  # Adjust padding for spacing
            self.buttons.append(btn)  # Add button to scanning list

        # Configure grid to distribute space equally
        for i in range(2):  # Two rows
            grid_frame.rowconfigure(i, weight=1)
        for j in range(2):  # Two columns
            grid_frame.columnconfigure(j, weight=1)

        # Highlight the first button for scanning
        if self.buttons:
            self.highlight_button(0)

    def _get_settings_page(self, app):
        """Lazy import to avoid circular imports."""
        from ui.settings_menu import SettingsMenuPage
        return SettingsMenuPage

    def _get_communication_page(self, app):
        """Lazy import to avoid circular imports."""
        from ui.communication_menu import CommunicationPageMenu
        return CommunicationPageMenu

    def _get_entertainment_page(self, app):
        """Lazy import to avoid circular imports."""
        from ui.entertainment_menu import EntertainmentMenuPage
        return EntertainmentMenuPage

    def scan_forward(self, event=None):
        """Move to the next button and highlight it."""
        if self.selection_enabled and self.buttons:
            self.selection_enabled = False  # Disable selection temporarily to debounce
            self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
            self.highlight_button(self.current_button_index)
            threading.Timer(0.5, self.enable_selection).start()  # Re-enable selection after a delay

    def highlight_button(self, index):
        """Highlight the current button and reset others."""
        for i, button in enumerate(self.buttons):
            if i == index:
                button.config(bg="yellow", fg="black")  # Highlight current button
            else:
                button.config(bg="light blue", fg="black")  # Reset others
        self.update()

    def enable_selection(self):
        """Re-enable selection after a delay."""
        self.selection_enabled = True

    def on_select(self, command, speak_text):
        """Handle button selection logic."""
        command()
        if speak_text:
            speak(speak_text)

    def emergency_alert(self):
        """Trigger emergency alert."""
        # Use the window manager to send volume up keys
        wm.send_key(wm.VK_VOLUME_UP)  # Initial volume up
        for _ in range(50):  # Max volume
            wm.send_key(wm.VK_VOLUME_UP, key_up=True)
            time.sleep(0.05)

        def alert_loop():
            end_time = time.time() + 15
            while time.time() < end_time:
                speak("Help, help, help, help, help")
                time.sleep(2)

        threading.Thread(target=alert_loop, daemon=True).start()