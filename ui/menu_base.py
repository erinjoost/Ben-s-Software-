"""
Base menu framework for Ben's Accessible Menu System.
Provides common functionality for all menu pages including button management,
content opening, and URL handling.
"""

import time
import os
import sys
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import threading

import tkinter as tk
from core.audio import speak
from core.config import wm
from data.loaders import load_last_watched, save_last_watched
from browser.integration import (
    open_in_chrome, movies_in_chrome, open_and_click, open_pluto,
    open_spotify, open_plex_movies, open_plex, open_youtube
)
from system.monitoring import is_chrome_running


class MenuFrame(tk.Frame):
    """Base class for all menu pages with common functionality."""
    active_show = None  # Class-level variable to track the active show

    def __init__(self, parent, title):
        super().__init__(parent, bg="black")
        self.parent = parent
        self.title = title
        self.buttons = []  # Store buttons for scanning
        self.create_title()

    def create_title(self):
        """Create the title label for the menu."""
        label = tk.Label(self, text=self.title, font=("Arial", 36), bg="black", fg="white")
        label.pack(pady=20)

    def create_button_grid(self, buttons, columns=3):
        """Create a grid layout for buttons."""
        # Create a frame for the grid directly inside this MenuFrame.
        grid_frame = tk.Frame(self, bg="black")
        grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.buttons = []  # Reset the button list.
        rows = (len(buttons) + columns - 1) // columns  # Calculate number of rows.

        for i, (text, command, speak_text) in enumerate(buttons):
            row, col = divmod(i, columns)
            btn = tk.Button(
                grid_frame,
                text=text,
                font=("Arial Black", 36),
                bg="light blue",
                fg="black",
                activebackground="yellow",
                activeforeground="black",
                command=lambda c=command, s=speak_text: self.on_select(c, s),
                wraplength=700  # Allows text to wrap if needed.
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            self.buttons.append(btn)

        # Configure the grid rows and columns to expand evenly.
        for r in range(rows):
            grid_frame.rowconfigure(r, weight=1)
        for c in range(columns):
            grid_frame.columnconfigure(c, weight=1)

    def on_select(self, command, speak_text):
        """Handle button selection."""
        command()
        if speak_text:
            speak(speak_text)

    def save_current_url(self, show_name, expected_url):
        """
        Every 30 seconds, fetch the active URL and save it under `show_name` in last_watched.json.
        """
        base = "/".join(expected_url.split("/")[:4])
        print(f"[TRACKER] Started URL-tracker for: {show_name}")

        while MenuFrame.active_show == show_name:
            time.sleep(5)  # Wait for 30 seconds

            current_url = expected_url  # Here, you can use the expected URL directly
            print(f"[TRACK] fetched for {show_name}: {current_url}")

            # Check if the current URL matches the base URL and save it
            if current_url and current_url.startswith(base):
                data = load_last_watched()
                data[show_name] = current_url
                save_last_watched(data)
                print(f"[SAVED] {show_name} → {current_url}")
            else:
                print(f"[SKIP] No save for {show_name}, URL: {current_url}")

            if not is_chrome_running():
                print(f"[TRACKER] Chrome closed, stopping tracker for {show_name}")
                break

        print(f"[TRACKER] Exited URL-tracker for: {show_name}")

    def open_link(self, entry):
        """Open a link based on its type and platform."""
        title = entry["title"]
        url = entry["url"]
        content_type = entry.get("type", "movies").lower()

        print(f"[DEBUG] Requested: {title} - URL: {url} (Type: {content_type})")

        # 1) Tell the URL‐save extension/server which show key to use
        MenuFrame.active_show = title
        print(f"[DEBUG] Active show set → {MenuFrame.active_show}")

        # 2) For shows, overlay with last-watched URL if available
        if content_type == "shows":
            last = load_last_watched()
            if title in last:
                url = last[title]
                print(f"[DEBUG] Last-watched found for {title}: {url}")
            else:
                print(f"[DEBUG] No last-watched found for {title}, using default from spreadsheet")

        print(f"[DEBUG] Final URL for {title}: {url}")

        # 3) Dispatch by type/platform
        if content_type == "shows":
            if "plex.tv" in url:
                print(f"[DEBUG] Detected Plex Show → open_plex({title})")
                open_plex(url, title)
            elif "youtube.com" in url or "youtu.be" in url:
                print(f"[DEBUG] Detected YouTube Show → open_youtube({title})")
                open_youtube(url, title)
            elif "paramountplus.com/live-tv" in url:
                print(f"[DEBUG] Detected Paramount+ Live TV → open_and_click({title})")
                open_and_click(title, url)
            elif "pluto.tv" in url:
                print(f"[DEBUG] Detected Pluto.tv Show → open_pluto({title})")
                open_pluto(title, url)
            elif "amazon.com" in url:
                print(f"[DEBUG] Detected Amazon Show → open_and_click({title})")
                open_and_click(title, url)
            else:
                print(f"[DEBUG] Non-Plex Show → open_in_chrome({title})")
                open_in_chrome(title, url)

        elif content_type == "live":
            if "paramountplus.com/live-tv" in url:
                print(f"[DEBUG] Detected Paramount+ Live Stream → open_and_click({title})")
                open_and_click(title, url)
            elif "pluto.tv" in url:
                print(f"[DEBUG] Detected Pluto.tv Live Stream → open_pluto({title})")
                open_pluto(title, url)
            elif "youtube.com" in url or "youtu.be" in url:
                print(f"[DEBUG] Detected YouTube Live Stream → open_youtube({title})")
                open_youtube(url, title)
            elif "amazon.com" in url:
                print(f"[DEBUG] Detected Amazon Live → open_and_click({title})")
                open_and_click(title, url)
            else:
                print(f"[DEBUG] General Live Content → open_in_chrome({title})")
                open_in_chrome(title, url)

        elif content_type == "movies":
            if "plex.tv" in url:
                print(f"[DEBUG] Detected Plex Movie → open_plex_movies({title})")
                open_plex_movies(url, title)
            elif "amazon.com" in url:
                print(f"[DEBUG] Detected Amazon Movie → open_and_click({title})")
                open_and_click(title, url)
            else:
                print(f"[DEBUG] Other Movie Content → movies_in_chrome({title})")
                movies_in_chrome(title, url)

        elif content_type == "music":
            if "spotify.com" in url:
                print(f"[DEBUG] Detected Spotify → open_spotify({title})")
                open_spotify(url)
            else:
                print(f"[DEBUG] Other Music Source → open_in_chrome({title})")
                open_in_chrome(title, url)

        elif content_type == "audiobooks":
            if "plex.tv" in url:
                print(f"[DEBUG] Detected Plex Audiobook → open_plex_movies({title})")
                open_plex_movies(url, title)
            else:
                print(f"[DEBUG] Other Audiobook Source → movies_in_chrome({title})")
                movies_in_chrome(title, url)

        else:
            print(f"[DEBUG] Unknown content type '{content_type}' → movies_in_chrome({title})")
            movies_in_chrome(title, url)


# HTTP request handler to save URLs
class URLSaveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL from the request
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        url = qs.get("url", [None])[0]

        # Get the active show
        show = MenuFrame.active_show

        if show and url:
            # Read the existing data from last_watched.json
            data = load_last_watched()
            data[show] = url  # Update or add the show and URL
            save_last_watched(data)  # Save the updated data
            print(f"[URL-SAVED] {show} → {url}")

        # Send a response back to indicate success
        self.send_response(204)
        self.end_headers()


# Start the HTTP server
def start_url_server():
    server = HTTPServer(("127.0.0.1", 8765), URLSaveHandler)
    server.serve_forever()


# Start the server in a background thread
threading.Thread(target=start_url_server, daemon=True).start()