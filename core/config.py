"""
Configuration and constants for Ben's Accessible Menu System.
Contains all imports, constants, and basic configuration.
"""

# Standard library imports
import tkinter as tk
import threading
import time
import subprocess
import platform
import queue
import json
import os
import logging
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from functools import partial
from collections import defaultdict

# Third-party imports
from pyttsx3 import init
import pyautogui
import ctypes  # For cross-platform focus handling via abstraction
from pynput import keyboard
from pynput.keyboard import Controller
import requests
import psutil
import pandas as pd
from tkinter.font import Font

# Local imports - cross-platform window management
from utils.cross_platform import (
    wm,  # WindowManager instance for cross-platform window operations
    monitor_focus_cross_platform, force_focus_cross_platform,
    monitor_start_menu_cross_platform, send_escape_key_cross_platform,
    minimize_terminal_cross_platform, minimize_on_screen_keyboard_cross_platform,
    bring_application_to_focus_cross_platform, is_system_menu_open_cross_platform,
    log_window_titles_cross_platform
)

# For compatibility with existing win32api calls
try:
    import win32api
    import win32process
except ImportError:
    # Create stubs for win32api functionality
    class Win32ApiStub:
        @staticmethod
        def SetCursorPos(pos):
            try:
                pyautogui.moveTo(pos[0], pos[1])
            except:
                pass
        
        @staticmethod
        def mouse_event(flags, x, y):
            try:
                if flags == 0x0002:  # MOUSEEVENTF_LEFTDOWN
                    pyautogui.mouseDown()
                elif flags == 0x0004:  # MOUSEEVENTF_LEFTUP
                    pyautogui.mouseUp()
            except:
                pass
    
    class Win32ProcessStub:
        @staticmethod
        def GetWindowThreadProcessId(hwnd):
            return 0, 0
    
    win32api = Win32ApiStub()
    win32process = Win32ProcessStub()

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Application constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LAST_WATCHED_FILE = os.path.join(DATA_DIR, "last_watched.json")
GAMES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "games")

# Default application settings
DEFAULT_GEOMETRY = "960x540"
DEFAULT_FONT = ("Arial Black", 36)
BUTTON_COLORS = {
    "normal": {"bg": "light blue", "fg": "black"},
    "highlighted": {"bg": "yellow", "fg": "black"},
    "active": {"bg": "yellow", "fg": "black"}
}

# Timing constants
SPACEBAR_LONG_PRESS_TIME = 3.5  # seconds
BACKWARD_SCAN_DELAY = 2  # seconds
SELECTION_DEBOUNCE_TIME = 0.5  # seconds
ENTER_SELECTION_DELAY = 2  # seconds
FOCUS_DELAY = 3000  # milliseconds
FORCE_FOCUS_DELAY = 7000  # milliseconds
CHROME_LOAD_DELAY = 7  # seconds
SPOTIFY_LOAD_DELAY = 12  # seconds

# Browser paths (platform-specific)
if platform.system() == "Windows":
    CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
elif platform.system() == "Darwin":
    CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else:
    CHROME_PATH = "google-chrome"  # Linux default

# Image paths
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
SPOTIFY_PLAY_IMAGE = os.path.join(IMAGES_DIR, "spotifyplay.png")