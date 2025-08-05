"""
Browser integration for Ben's Accessible Menu.
Handles Chrome launching, URL management, and platform-specific browser interactions.
"""

import os
import time
import subprocess
import pyautogui
from pynput.keyboard import Controller
from core.config import wm, CHROME_PATH, SPOTIFY_PLAY_IMAGE, CHROME_LOAD_DELAY, SPOTIFY_LOAD_DELAY
from data.loaders import load_last_watched, save_last_watched
from system.monitoring import is_chrome_running


def close_chrome_cleanly():
    """Close Chrome browser cleanly using Alt+F4."""
    try:
        # Import locally to avoid circular imports
        from system.monitoring import get_active_window_name
        name, _ = get_active_window_name()
        if "Chrome" in name:
            print("Chrome is active. Closing it.")
            pyautogui.hotkey("alt", "f4")  # Close Chrome window
        else:
            print("Chrome is not the active window.")
    except Exception as e:
        print(f"Error closing Chrome: {e}")


def open_in_chrome(show_name, default_url, persistent=True):
    """Open URL in Chrome with optional last-watched persistence."""
    # Load and override with whatever's in last_watched.json
    url_to_open = default_url
    if persistent:
        last = load_last_watched()
        if show_name in last:
            url_to_open = last[show_name]
            print(f"[LOAD] Resuming {show_name} from saved URL → {url_to_open}")
        else:
            print(f"[LOAD] No saved record for {show_name}, using default.")

    args = [
        CHROME_PATH,
        "--start-fullscreen",
        url_to_open
    ]

    try:
        subprocess.Popen(args, shell=False)
        print(f"[LAUNCH] Chrome → {url_to_open}")
    except Exception as e:
        print(f"[ERROR] launching Chrome: {e}")


def movies_in_chrome(show_name, default_url):
    """
    Opens the given movie URL in Chrome in fullscreen mode without
    using persistent last-watched data.
    """
    try:
        subprocess.run(
            ["start", "chrome", "--remote-debugging-port=9222", "--start-fullscreen", default_url],
            shell=True
        )
        print(f"Opened movie URL for {show_name}: {default_url}")
    except Exception as e:
        print(f"Error opening movie URL for {show_name}: {e}")


def open_and_click(show_name, default_url, x_offset=0, y_offset=0):
    """Open the given URL, click on the specified position, and ensure fullscreen mode."""
    # Use the same logic as open_in_chrome to open the URL
    movies_in_chrome(show_name, default_url)
    time.sleep(5)  # Wait for the browser to open and load

    # Bring the browser window to the foreground
    current_window = wm.get_foreground_window()
    if current_window:
        wm.show_window(current_window, wm.SW_RESTORE)
        wm.set_foreground_window(current_window)
    print("Brought Chrome to the foreground.")

    # Calculate click position with offsets
    screen_width, screen_height = pyautogui.size()
    click_x = (screen_width // 2) + x_offset
    click_y = (screen_height // 2) + y_offset

    # Perform the click
    pyautogui.click(click_x, click_y)
    print(f"Clicked at position: ({click_x}, {click_y})")

    # Allow time for interaction
    time.sleep(2)


def open_pluto(show_name, pluto_url):
    """Open Pluto TV link in Chrome, ensure focus, unmute, and fullscreen."""
    
    # Open the URL in Chrome
    open_in_chrome(show_name, pluto_url)
    time.sleep(CHROME_LOAD_DELAY)  # Wait for page and video player to load

    # Bring Chrome to the foreground
    current_window = wm.get_foreground_window()
    if current_window:
        wm.show_window(current_window, wm.SW_RESTORE)
        wm.set_foreground_window(current_window)
    print("Brought Chrome to the foreground.")

    # Wait for the video player to load
    time.sleep(6)

    # Use pynput.Controller instead of keyboard module
    keyboard = Controller()

    # Simulate 'm' keypress to mute/unmute
    print("Sending 'm' keypress to unmute the video...")
    keyboard.press('m')
    time.sleep(0.1)
    keyboard.release('m')

    # Wait briefly before fullscreening
    time.sleep(2)

    # Simulate 'f' keypress to fullscreen
    print("Sending 'f' keypress to fullscreen the video...")
    keyboard.press('f')
    time.sleep(0.1)
    keyboard.release('f')

    print("Pluto.TV interaction complete.")


def open_spotify(playlist_url):
    """
    Opens the Spotify playlist URL in Chrome, waits for the page to load,
    then tries to locate the Play button via image recognition.
    If the image is not found on the first try, waits a few seconds and tries again.
    If still not found, it falls back to predetermined coordinates.
    Finally, it sends Alt+S to shuffle.
    """
    # Define the path to Chrome.
    chrome_path = CHROME_PATH
    if not os.path.exists(chrome_path):
        os.startfile(playlist_url)
    else:
        args = [
            chrome_path,
            "--autoplay-policy=no-user-gesture-required",
            "--start-fullscreen",
            playlist_url
        ]
        subprocess.Popen(args)
    
    # Wait for the page to load.
    print("[DEBUG] Waiting for Chrome/Spotify page to load...")
    time.sleep(SPOTIFY_LOAD_DELAY)
    
    # Define the absolute path to your reference image.
    play_image_path = SPOTIFY_PLAY_IMAGE
    if not os.path.exists(play_image_path):
        print(f"[DEBUG] Reference image not found: {play_image_path}")
        location = None
    else:
        print(f"[DEBUG] Searching for play button using image: {play_image_path}")
        try:
            location = pyautogui.locateCenterOnScreen(play_image_path, confidence=0.8)
        except Exception as e:
            print(f"[ERROR] Exception during first image search: {e}")
            location = None
    
    # If not found, try to bring Chrome to the foreground and try again.
    if location is None:
        print("[DEBUG] Play button not found. Attempting to bring Chrome to foreground and waiting a bit...")
        # Attempt to find a window with "Chrome" in its title.
        chrome_window = wm.find_window(None, "Spotify")  # Adjust this if needed.
        if chrome_window:
            wm.show_window(chrome_window, wm.SW_RESTORE)
            wm.set_foreground_window(chrome_window)
        else:
            print("[DEBUG] Could not find a Chrome window titled 'Spotify'.")
        time.sleep(3)
        try:
            location = pyautogui.locateCenterOnScreen(play_image_path, confidence=0.8)
        except Exception as e:
            print(f"[ERROR] Exception during second image search: {e}")
            location = None

    # If the play button is found, click it; otherwise, use fallback coordinates.
    if location is not None:
        print(f"[DEBUG] Play button found at: {location}")
        pyautogui.click(location)
    else:
        print("[DEBUG] Play button still not found. Using fallback coordinates (752, 665).")
        pyautogui.click((752, 665))
    
    # Wait before sending the hotkey.
    time.sleep(2)
    pyautogui.hotkey('alt', 's')
    print("[DEBUG] Sent Alt+S to shuffle.")


def open_plex_movies(plex_url, show_name):
    """
    Opens the Plex URL in Chrome and then sends keyboard commands:
    1. Press 'x'
    2. Press 'return'
    3. Wait 2 seconds
    4. Press 'p'
    """
    # Open Plex using your common method.
    movies_in_chrome(show_name, plex_url)
    
    # Wait for the Plex page to load fully.
    time.sleep(CHROME_LOAD_DELAY)  # Adjust as necessary for your system.
    
    # Send the keyboard commands.
    pyautogui.press('x')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('p')
    print("Sent keys: x, enter, then after 2 seconds, p.")


def open_plex(plex_url, show_name):
    """
    Opens the Plex URL in Chrome and then sends keyboard commands:
    1. Press 'x'
    2. Press 'return'
    3. Wait 2 seconds
    4. Press 'p'
    """
    # Open Plex using your common method.
    open_in_chrome(show_name, plex_url)
    
    # Wait for the Plex page to load fully.
    time.sleep(CHROME_LOAD_DELAY)  # Adjust as necessary for your system.
    
    # Send the keyboard commands.
    pyautogui.press('x')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('p')
    print("Sent keys: x, enter, then after 2 seconds, p.")     


def open_youtube(youtube_url, show_name):
    """Open YouTube URL and press 'f' for fullscreen."""
    # Open youtube using your common method.
    movies_in_chrome(show_name, youtube_url)
    # Wait for the Youtube page to load fully.
    time.sleep(5)  # Adjust as necessary for your system.
    # Send the keyboard commands.
    pyautogui.press('f')
    print("Sent keys: f")


def click_at(x, y, hold_time=0.1, double_click=False):
    """Cross-platform click function using pyautogui."""
    # Move the cursor to the given coordinates and click
    try:
        pyautogui.moveTo(x, y)
        time.sleep(0.1)  # Give the cursor time to move.
        
        if double_click:
            pyautogui.doubleClick(x, y, duration=hold_time)
        else:
            pyautogui.click(x, y, duration=hold_time)
    except Exception as e:
        print(f"Error clicking at ({x}, {y}): {e}")
        # Fallback to win32api if available
        try:
            from core.config import win32api
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)
            win32api.mouse_event(0x0002, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(hold_time)
            win32api.mouse_event(0x0004, 0, 0)  # MOUSEEVENTF_LEFTUP
            
            if double_click:
                time.sleep(0.1)
                win32api.mouse_event(0x0002, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                time.sleep(hold_time)
                win32api.mouse_event(0x0004, 0, 0)  # MOUSEEVENTF_LEFTUP
        except:
            print("Both pyautogui and win32api failed for clicking")