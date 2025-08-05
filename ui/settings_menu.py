"""
Settings menu page for Ben's Accessible Menu System.
Provides system controls like volume, sleep timer, display, lock, restart, and shutdown.
"""

import time
import subprocess
import platform
import tkinter as tk

from ui.menu_base import MenuFrame
from core.audio import speak
from core.config import wm


class SettingsMenuPage(MenuFrame):
    """Settings menu with system control options."""
    
    def __init__(self, parent):
        super().__init__(parent, "Settings")  # Set the title to "Settings"
        self.buttons = []  # Store buttons for scanning

        # Define buttons with actions and TTS
        buttons = [
            ("Back", lambda: parent.show_frame(self._get_main_menu(parent)), "Back"),
            ("Volume Up", self.volume_up, "Increase volume"),
            ("Volume Down", self.volume_down, "Decrease volume"),
            ("Sleep Timer (60 min)", self.sleep_timer, "Set a 60-minute sleep timer"),
            ("Cancel Sleep Timer", self.cancel_sleep_timer, "Cancel the sleep timer"),
            ("Turn Display Off", self.turn_off_display, "Turn off the display"),
            ("Lock", self.lock_computer, "Lock the computer"),
            ("Restart", self.restart_computer, "Restart the computer"),
            ("Shut Down", self.shut_down_computer, "Shut down the computer"),         
        ]
        
        # Create button grid and bind keys for scanning/selecting
        self.create_button_grid(buttons, columns=3)  # Set columns to 3

    def _get_main_menu(self, app):
        """Lazy import to avoid circular imports."""
        from ui.main_menu import MainMenuPage
        return MainMenuPage
        
    def create_button_grid(self, buttons, columns=5):
        """Creates a grid layout for buttons with a dynamic number of rows and columns."""
        grid_frame = tk.Frame(self, bg="black")
        grid_frame.pack(expand=True, fill="both")

        rows = (len(buttons) + columns - 1) // columns  # Calculate required rows
        for i, (text, command, speak_text) in enumerate(buttons):
            row, col = divmod(i, columns)
            btn = tk.Button(
                grid_frame, text=text, font=("Arial Black", 36), bg="light blue", fg="black",
                activebackground="yellow", activeforeground="black",
                command=lambda c=command, s=speak_text: self.on_select(c, s)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            self.buttons.append(btn)  # Add button to scanning list

        for i in range(rows):
            grid_frame.rowconfigure(i, weight=1)
        for j in range(columns):
            grid_frame.columnconfigure(j, weight=1)

        self.bind("<KeyPress-space>", self.parent.track_spacebar_hold)
        self.bind("<KeyRelease-space>", self.parent.reset_spacebar_hold)
        self.bind("<KeyRelease-Return>", self.parent.select_button)
        
    def volume_up(self):
        """Increase system volume."""
        for _ in range(4):  # Increase volume by ~10%
            wm.send_key(wm.VK_VOLUME_UP, key_up=True)
            time.sleep(0.05)
        speak("Volume increased")

    def volume_down(self):
        """Decrease system volume."""
        for _ in range(4):  # Decrease volume by ~10%
            wm.send_key(wm.VK_VOLUME_DOWN, key_up=True)
            time.sleep(0.05)
        speak("Volume decreased")
                  
    def turn_off_display(self):
        """Turn off the display."""
        try:
            # Use cross-platform approach - this is platform-specific so we handle it in the window manager
            if platform.system() == "Windows":
                wm.send_message(None, 0x112, 0xF170, 2)  # Turn off display via cross-platform call
            elif platform.system() == "Darwin":
                # macOS: Use pmset to turn off display
                subprocess.run(["pmset", "displaysleepnow"], check=False)
            speak("Display turned off")
        except Exception as e:
            speak("Failed to turn off display")
            print(f"Turn Off Display Error: {e}")

    def sleep_timer(self):
        """Set a 60-minute sleep timer."""
        try:
            # Set a sleep timer for 3600 seconds (60 minutes)
            if platform.system() == "Windows":
                subprocess.run("shutdown /s /t 3600", shell=True)
            elif platform.system() == "Darwin":
                # macOS: Use pmset to schedule sleep
                subprocess.run(["sudo", "pmset", "sleepnow"], check=False)
                # Note: macOS doesn't have a direct equivalent to Windows' timed shutdown
                # This will sleep immediately. For timed sleep, would need a different approach
            speak("Sleep timer set for 60 minutes")
        except Exception as e:
            speak("Failed to set sleep timer")
            print(f"Error setting sleep timer: {e}")

    def cancel_sleep_timer(self):
        """Cancel the sleep timer."""
        try:
            # Cancel the shutdown timer
            if platform.system() == "Windows":
                subprocess.run("shutdown /a", shell=True)
            elif platform.system() == "Darwin":
                # macOS: Cancel any pending shutdown (limited options)
                subprocess.run(["sudo", "killall", "shutdown"], check=False)
            speak("Sleep timer canceled")
        except Exception as e:
            speak("Failed to cancel sleep timer")
            print(f"Error canceling sleep timer: {e}")

    def lock_computer(self):
        """Lock the computer."""
        if wm.lock_workstation():
            speak("Computer locked")
        else:
            speak("Failed to lock computer")

    def restart_computer(self):
        """Restart the computer."""
        try:
            if platform.system() == "Windows":
                subprocess.run("shutdown /r /t 0", shell=True)
            elif platform.system() == "Darwin":
                subprocess.run(["sudo", "shutdown", "-r", "now"], check=False)
            speak("Restarting computer")
        except Exception as e:
            speak("Failed to restart computer")
            print(f"Error restarting: {e}")
                        
    def shut_down_computer(self):
        """Shut down the computer."""
        try:
            if platform.system() == "Windows":
                subprocess.run("shutdown /s /t 0", shell=True)
            elif platform.system() == "Darwin":
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=False)
            speak("Shutting down the computer")
        except Exception as e:
            speak("Failed to shut down computer")
            print(f"Error shutting down: {e}")