"""
Library menu page for Ben's Accessible Menu System.
Handles browsing and selecting content from organized media libraries.
"""

import tkinter as tk
from tkinter.font import Font
from collections import defaultdict

from ui.menu_base import MenuFrame
from core.audio import speak


class LibraryMenu(MenuFrame):
    """Library menu for browsing organized content by genre and title."""
    
    def __init__(self, parent, data, level, parent_key=None):
        """
        data:
          - For level "genre": a dict mapping genre → list of entries.
          - For level "final": a list of entries (each with a "title" key).
        level:
          - "genre" for the first level (choose a genre)
          - "final" for the final step (choose a show)
        parent_key:
          - For "genre": (optional) a type (e.g. "movies")
          - For "final": the chosen genre name
        """
        self.data = data
        self.level = level
        self.parent_key = parent_key
        self.page = 0            # current page index
        self.page_size = 7       # show 7 selection buttons per page

        # Set the window title based on the level.
        if self.level == "genre":
            title = f"Select Genre{(' (' + parent_key.capitalize() + ')') if parent_key else ''}"
        elif self.level == "final":
            title = f"Select Show ({parent_key})"
        else:
            title = "Library"
        super().__init__(parent, title)

        # Use a container frame for our grid.
        self.container = tk.Frame(self, bg="black")
        self.container.pack(expand=True, fill="both")
        self.reload_buttons()

    def adjust_font_size(self, button, max_width=250, min_font_size=18):
        """Adjust button font size to fit within specified width."""
        button.update_idletasks()  # Update widget geometry
        text = button.cget("text")
        # Use the persistent font family and weight
        font_family = "Arial Black"
        font_size = 32

        while font_size >= min_font_size:
            test_font = Font(family=font_family, size=font_size)
            if test_font.measure(text) <= max_width:
                break
            font_size -= 2

        # Update the persistent font or create a new one with the same family and desired size.
        new_font = Font(family=font_family, size=font_size)
        button.config(font=new_font)

    def adjust_all_buttons(self):
        """Call adjust_font_size on each button in the current menu."""
        for btn in self.buttons:
            self.adjust_font_size(btn, max_width=250, min_font_size=18)

    def reload_buttons(self):
        """Reload buttons for the current page."""
        # Clear the container.
        for widget in self.container.winfo_children():
            widget.destroy()

        button_list = []

        # Determine the Back button command.
        # If we're not on the first page, the Back button will go to the previous page;
        # otherwise, it returns to the previous (Entertainment) menu.
        if self.page > 0:
            back_command = self.previous_page
        else:
            back_command = lambda: self.parent.show_previous_menu()

        back_btn = tk.Button(
            self.container,
            text="Back",
            font=("Arial Black", 36),
            bg="light blue",
            fg="black",
            command=back_command,
            wraplength=700,  # Allow wrapping into two lines if needed
            justify="center"
        )
        button_list.append(back_btn)

        # Build the keys list based on the current level.
        if self.level == "genre":
            keys = sorted(self.data.keys())
        elif self.level == "final":
            keys = sorted(entry["title"] for entry in self.data)
        else:
            keys = []

        # Determine the slice for the current page.
        start = self.page * self.page_size
        end = start + self.page_size
        page_keys = keys[start:end]

        for key in page_keys:
            btn = tk.Button(
                self.container,
                text=key,
                font=("Arial Black", 36),
                bg="light blue",
                fg="black",
                command=lambda k=key: self.on_select(k),
                wraplength=700,  # Allow wrapping to use two lines
                justify="center"
            )
            button_list.append(btn)

        # If there are more keys beyond this page, add a Next button.
        if end < len(keys):
            next_btn = tk.Button(
                self.container,
                text="Next",
                font=("Arial Black", 36),
                bg="light blue",
                fg="black",
                command=self.next_page,
                wraplength=700,
                justify="center"
            )
            button_list.append(next_btn)

        # Arrange all buttons in a grid (using 3 columns).
        num_cols = 3
        num_buttons = len(button_list)
        num_rows = (num_buttons + num_cols - 1) // num_cols

        for idx, btn in enumerate(button_list):
            row = idx // num_cols
            col = idx % num_cols
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

        for r in range(num_rows):
            self.container.grid_rowconfigure(r, weight=1)
        for c in range(num_cols):
            self.container.grid_columnconfigure(c, weight=1)

        # Save the new button list for scanning.
        self.buttons = button_list

        # Update the parent's scanning state (after a short delay to allow the UI to update).
        self.after(50, self.update_scanning)
        # After a short delay, adjust the font sizes on all buttons.
        self.after(100, self.adjust_all_buttons)

    def update_scanning(self):
        """Update parent scanning state."""
        self.parent.buttons = self.buttons
        self.parent.current_button_index = 0
        self.parent.highlight_button(0)

    def next_page(self):
        """Advance to the next page and reload the buttons."""
        self.page += 1
        self.reload_buttons()

    def previous_page(self):
        """Go back one page and reload the buttons (if not on the first page)."""
        if self.page > 0:
            self.page -= 1
            self.reload_buttons()
        else:
            self.parent.show_previous_menu()

    def on_select(self, key):
        """
        Dispatch the selection based on the current level:
          - For "genre": directly show a final menu listing all shows in that genre.
          - For "final": locate the matching entry and open its URL.
        """
        if self.level == "genre":
            # Instead of grouping entries by their first letter, directly show the list of shows.
            new_data = self.data[key]  # This is a list of entries for the selected genre.
            self.parent.show_frame(lambda p: LibraryMenu(p, new_data, "final", parent_key=key))
        elif self.level == "final":
            # Find the entry with a matching title and open its link.
            for entry in self.data:
                if entry["title"] == key:
                    self.open_link(entry)
                    break