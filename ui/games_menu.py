"""
Games menu page for Ben's Accessible Menu System.
Auto-discovers games from the games directory and provides launch functionality.
"""

import os
import sys
import subprocess
import tkinter as tk
from functools import partial

from ui.menu_base import MenuFrame
from core.audio import speak
from core.config import GAMES_DIR


class GamesPage(MenuFrame):
    """Games menu that auto‑populates from Python scripts inside ./games."""

    def __init__(self, parent):
        super().__init__(parent, "Games")
        self.parent = parent

        # Build button list dynamically: Back + discovered games
        buttons = [
            ("Back", lambda: parent.show_frame(self._get_entertainment_menu(parent)), "Back")
        ]
        buttons.extend(self._discover_games())

        self.create_button_grid(buttons)

    def _get_entertainment_menu(self, app):
        """Lazy import to avoid circular imports."""
        from ui.entertainment_menu import EntertainmentMenuPage
        return EntertainmentMenuPage

    # ───────────────────────── helpers ──────────────────────────
    def _discover_games(self):
        """Return a list of (label, command, speak_text) tuples for each game script."""
        games = []

        if not os.path.isdir(GAMES_DIR):
            print(f"[GamesPage] Folder not found: {GAMES_DIR}")
            return games

        for file in sorted(os.listdir(GAMES_DIR)):
            # Only include Python scripts; skip dunders and non‑py files
            if not file.endswith(".py") or file.startswith("__"):
                continue

            script_path = os.path.join(GAMES_DIR, file)
            title = self._filename_to_title(file)
            cmd = partial(self.open_game, script_path, title)
            games.append((title, cmd, title))

        return games

    @staticmethod
    def _filename_to_title(filename):
        """Convert "tic_tac_toe.py" → "Tic Tac Toe"."""
        base = os.path.splitext(filename)[0]
        return base.replace("_", " ").title()

    # ───────────────────────── UI helpers ───────────────────────
    def create_button_grid(self, buttons, columns=3):
        """Create button grid layout."""
        grid = tk.Frame(self, bg="black")
        grid.pack(expand=True, fill="both")

        self.buttons = []
        rows = (len(buttons) + columns - 1) // columns

        for i, (text, command, speak_text) in enumerate(buttons):
            r, c = divmod(i, columns)
            btn = tk.Button(
                grid,
                text=text,
                font=("Arial Black", 36),
                bg="light blue",
                fg="black",
                activebackground="yellow",
                activeforeground="black",
                command=lambda c=command, s=speak_text: self.on_select(c, s),
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
            self.buttons.append(btn)

        for r in range(rows):
            grid.rowconfigure(r, weight=1)
        for c in range(columns):
            grid.columnconfigure(c, weight=1)

    # ───────────────────────── actions ──────────────────────────
    def open_game(self, script_path, title):
        """Launch a game script."""
        try:
            print(f"[GamesPage] Launching: {title} → {script_path}")
            subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
            self.parent.destroy()  # Close main app so game runs fullscreen
        except Exception as e:
            print(f"[GamesPage] Failed to open {title}: {e}")
            speak("Unable to launch the selected game.")