"""
Communication menu pages for Ben's Accessible Menu System.
Provides access to communication phrases and keyboard functionality.
"""

import os
import sys
import subprocess
import tkinter as tk

from ui.menu_base import MenuFrame
from core.audio import speak
from data.loaders import load_communication_phrases


class CommunicationPageMenu(MenuFrame):
    """Main communication menu with categories and keyboard access."""
    
    def __init__(self, parent):
        super().__init__(parent, "Communication")
        self.phrases_by_category = load_communication_phrases()
        self.categories = sorted(self.phrases_by_category.keys())
        self.page = 0
        self.page_size = 14  # back + keyboard + up to 14 categories = 16 buttons max
        self.load_buttons()

    def load_buttons(self):
        """Load buttons for the current page."""
        start = self.page * self.page_size
        end = start + self.page_size
        current_cats = self.categories[start:end]

        buttons = [
            ("Back", lambda: self.parent.show_frame(self._get_main_menu(self.parent)), "Back"),
            ("Keyboard", self.open_keyboard_app, "Keyboard")
        ]
        for cat in current_cats:
            buttons.append((cat, lambda c=cat: self.parent.show_frame(lambda p: CommunicationCategoryMenu(p, c, self.phrases_by_category[c])), cat))

        if end < len(self.categories):
            buttons.append(("Next", self.next_page, "Next Page"))

        self.create_button_grid(buttons, columns=4)

    def _get_main_menu(self, app):
        """Lazy import to avoid circular imports."""
        from ui.main_menu import MainMenuPage
        return MainMenuPage

    def next_page(self):
        """Go to the next page of categories."""
        self.page += 1
        self.load_buttons()

    def open_keyboard_app(self):
        """Open the keyboard application."""
        try:
            script_name = "keyboard.py"
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "keyboard", script_name)
            subprocess.Popen([sys.executable, script_path])
            self.master.destroy()
        except Exception as e:
            print(f"Failed to open keyboard: {e}") 


class CommunicationCategoryMenu(MenuFrame):
    """Menu for a specific communication category with phrases."""
    
    def __init__(self, parent, category_name, phrase_list):
        super().__init__(parent, category_name)
        buttons = [
            ("Back", lambda: parent.show_frame(CommunicationPageMenu), "Back")
        ]
        for label, speak_text in phrase_list:
            buttons.append((label, lambda t=speak_text: speak(t), speak_text))
        self.create_button_grid(buttons, columns=3)