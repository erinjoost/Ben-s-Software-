"""
Entertainment menu page for Ben's Accessible Menu System.
Provides access to Movies, Shows, Audio, Live Streams, and Games.
"""

import tkinter as tk
from ui.menu_base import MenuFrame


class EntertainmentMenuPage(MenuFrame):
    """Entertainment menu with media and games options."""
    
    def __init__(self, parent):
        super().__init__(parent, "Entertainment")
        self.buttons = []
        self.current_button_index = 0
        self.selection_enabled = True

        buttons = [
            ("Back", lambda: parent.show_frame(self._get_main_menu(parent)), "Back to Main Menu"),
            ("Movies", lambda: self.parent.show_frame(lambda p: self._get_library_menu(p, self.parent.organized_links.get("movies", {}), "genre", parent_key="movies")), "Movies"),
            ("Shows", lambda: self.parent.show_frame(lambda p: self._get_library_menu(p, self.parent.organized_links.get("shows", {}), "genre", parent_key="shows")), "Shows"),
            ("Audio", lambda: self.parent.show_frame(lambda p: self._get_library_menu(p, self._get_audio_data(), "genre", parent_key="audio")), "Audio"),
            ("Live Streams", lambda: self.parent.show_frame(lambda p: self._get_library_menu(p, self.parent.organized_links.get("live", {}), "genre", parent_key="live")), "Live Streams"),
            ("Games", lambda: parent.show_frame(self._get_games_page(parent)), "Games"),
        ]

        self.create_button_grid(buttons, columns=2)

    def _get_main_menu(self, app):
        """Lazy import to avoid circular imports."""
        from ui.main_menu import MainMenuPage
        return MainMenuPage

    def _get_library_menu(self, parent, data, level, parent_key):
        """Lazy import to avoid circular imports."""
        from ui.library_menu import LibraryMenu
        return LibraryMenu(parent, data, level, parent_key)

    def _get_games_page(self, app):
        """Lazy import to avoid circular imports."""
        from ui.games_menu import GamesPage
        return GamesPage

    def _get_audio_data(self):
        """Merge music, audiobooks, and podcast types into a unified 'audio' group."""
        data = {}
        for k in ("music", "audiobooks", "podcast"):
            entries = self.parent.organized_links.get(k, {})
            for genre, items in entries.items():
                data.setdefault(genre, []).extend(items)
        return data

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

    def on_select(self, command, speak_text):
        """Handle button selection with scanning."""
        command()
        if speak_text:
            from core.audio import speak
            speak(speak_text)

    def coming_soon(self):
        """Notify that this feature is coming soon."""
        from core.audio import speak
        speak("This feature is coming soon")