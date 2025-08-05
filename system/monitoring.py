"""
System monitoring utilities for Ben's Accessible Menu.
Handles window focus, Chrome monitoring, and system state management.
"""

import time
import psutil
import pyautogui
from core.config import wm
from utils.cross_platform import (
    minimize_terminal_cross_platform, minimize_on_screen_keyboard_cross_platform,
    bring_application_to_focus_cross_platform, is_system_menu_open_cross_platform,
    monitor_start_menu_cross_platform
)


def monitor_app_focus(app_title="Accessible Menu"):
    """Continuously monitor Chrome's state and ensure the application is maximized and focused."""
    while True:
        try:
            # Check if Chrome is running
            if not is_chrome_running():
                print("Chrome is not running. Ensuring application is maximized and in focus.")
                
                app_window = wm.find_window(None, app_title)
                if app_window:
                    # Restore and maximize the application window
                    wm.show_window(app_window, wm.SW_RESTORE)  # Ensure it's not minimized
                    wm.show_window(app_window, wm.SW_MAXIMIZE)  # Maximize the window
                    wm.set_foreground_window(app_window)  # Bring it to the foreground
                    print("Application is maximized and in focus.")
                else:
                    print(f"Application window with title '{app_title}' not found.")
            else:
                print("Chrome is running. Application can remain minimized or in the background.")
        except Exception as e:
            print(f"Error in monitor_app_focus: {e}")
        
        time.sleep(2)  # Adjust the monitoring frequency as needed


def minimize_terminal():
    """Cross-platform terminal minimization."""
    minimize_terminal_cross_platform()


def monitor_and_minimize(app):
    """Continuously monitor for Chrome activity and minimize the Tkinter app if restored."""
    while True:
        try:
            active_window, _ = get_active_window_name()

            # Check if Chrome is the active window
            if "Chrome" in active_window or "Google Chrome" in active_window:
                print("Chrome detected. Minimizing the app.")
                app.iconify()  # Minimize the Tkinter window

            # Check if the app is restored and Chrome is still open
            if app.state() == "normal" and ("Chrome" in active_window or "Google Chrome" in active_window):
                print("App restored while Chrome is open. Minimizing again.")
                app.iconify()

        except Exception as e:
            print(f"Error in monitor_and_minimize: {e}")
        time.sleep(1)  # Adjust frequency of checks if needed


def is_chrome_running():
    """Check if any Chrome process is running."""
    for process in psutil.process_iter(['name']):
        if process.info['name'] and 'chrome' in process.info['name'].lower():
            return True
    return False


def minimize_on_screen_keyboard():
    """Minimizes the on-screen keyboard if it's active."""
    minimize_on_screen_keyboard_cross_platform()


def get_active_window_name():
    """Get the active window name and process ID."""
    active_window = wm.get_foreground_window()
    if active_window:
        name = wm.get_window_text(active_window)
        # For cross-platform compatibility, return a dummy PID since we can't easily get it
        pid = 0  # Could enhance this later with platform-specific process detection
        return name, pid
    return "", 0


def close_chrome_cleanly():
    """Close Chrome browser cleanly using Alt+F4."""
    try:
        name, _ = get_active_window_name()
        if "Chrome" in name:
            print("Chrome is active. Closing it.")
            pyautogui.hotkey("alt", "f4")  # Close Chrome window
        else:
            print("Chrome is not the active window.")
    except Exception as e:
        print(f"Error closing Chrome: {e}")


def bring_application_to_focus():
    """Cross-platform function to bring application to focus."""
    bring_application_to_focus_cross_platform()


def is_start_menu_open():
    """Check if the Start Menu is currently open and focused."""
    return is_system_menu_open_cross_platform()


def monitor_start_menu():
    """Continuously check and close the Start Menu if it is open."""
    monitor_start_menu_cross_platform()