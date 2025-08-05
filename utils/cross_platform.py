"""
Cross-platform convenience module for Ben's accessibility software.
Provides easy-to-use helper functions and the unified WindowManager.
"""

import platform
from .window_manager import get_window_manager, WindowManager, WindowHandle

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

# Get the unified window manager - ready to use
wm = get_window_manager()


def monitor_focus_cross_platform(self):
    """Cross-platform focus monitoring function."""
    while True:
        import time
        time.sleep(0.5)
        try:
            current_window = wm.get_foreground_window()
            if current_window and current_window.native_handle != self.winfo_id():
                force_focus_cross_platform(self)
        except Exception as e:
            print(f"Focus monitoring error: {e}")


def force_focus_cross_platform(self):
    """Cross-platform force focus function."""
    try:
        self.iconify()
        self.deiconify()
        # Try to use the window manager to set foreground
        window_handle = WindowHandle(self.winfo_id())
        wm.set_foreground_window(window_handle)
        self.focus_force()
    except Exception as e:
        print(f"Force focus error: {e}")


def monitor_start_menu_cross_platform():
    """Cross-platform start menu monitoring function."""
    while True:
        import time
        time.sleep(1)
        try:
            if wm.is_system_menu_open():
                wm.close_system_menus()
        except Exception:
            pass


def send_escape_key_cross_platform():
    """Cross-platform escape key sending function."""
    wm.send_key(wm.VK_ESCAPE)


def return_to_main_app_cross_platform():
    """Cross-platform function to return to main application."""
    import subprocess
    import sys
    import os
    
    try:
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to get to the main directory
        parent_dir = os.path.dirname(current_dir)
        comm_path = os.path.join(parent_dir, "comm-v10.py")
        
        if os.path.exists(comm_path):
            subprocess.Popen([sys.executable, comm_path])
        else:
            print(f"Could not find main application at {comm_path}")
    except Exception as e:
        print(f"Error returning to main app: {e}")


# ==== ADVANCED CROSS-PLATFORM FUNCTIONS ====

def send_esc_key_cross_platform():
    """Send the ESC key to close system menus."""
    try:
        wm.send_key(wm.VK_ESCAPE)
        print("ESC key sent to close system menus.")
    except Exception as e:
        print(f"Error sending ESC key: {e}")


def bring_application_to_focus_cross_platform():
    """Bring the application back into focus."""
    try:
        # Try to find and activate the main application window
        app_window = wm.find_window(None, "Accessible Menu")
        if app_window:
            wm.show_window(app_window, wm.SW_RESTORE)
            wm.set_foreground_window(app_window)
            print("Application brought to focus.")
        else:
            print("No GUI window found.")
    except Exception as e:
        print(f"Error focusing application: {e}")


def is_system_menu_open_cross_platform():
    """Check if system menus are currently open and focused."""
    return wm.is_system_menu_open()


def monitor_system_menu_cross_platform():
    """Continuously check and close system menus if they are open."""
    import time
    
    while True:
        try:
            # Check if system menus are active (less frequently to reduce errors)
            if wm.is_system_menu_open():
                print("System menu detected. Closing it now.")
                wm.close_system_menus()
            # Removed verbose logging to reduce noise
        except Exception as e:
            # Only log significant errors, ignore AppleScript index errors
            if "Invalid index" not in str(e) and "Can't get item" not in str(e):
                print(f"Error in monitor_system_menu: {e}")
        
        time.sleep(2.0)  # Increased interval to reduce system load


def log_window_titles_cross_platform():
    """List all available window titles for debugging."""
    try:
        windows = wm.get_all_windows()
        print("Available windows:")
        for window in windows:
            print(f"Window: {window.title} (Class: {window.class_name})")
    except Exception as e:
        print(f"Error enumerating windows: {e}")


def minimize_on_screen_keyboard_cross_platform():
    """Minimizes the on-screen keyboard if it's active."""
    import time
    try:
        retries = 5
        for attempt in range(retries):
            # Try to find and minimize the on-screen keyboard
            if IS_WINDOWS:
                keyboard_window = wm.find_window("IPTip_Main_Window", None)
            else:
                # For other platforms, look for common accessibility keyboard names
                keyboard_window = wm.find_window(None, "Accessibility Keyboard")
            
            if keyboard_window:
                wm.show_window(keyboard_window, wm.SW_MINIMIZE)
                print(f"On-screen keyboard minimized on attempt {attempt + 1}.")
                return
            time.sleep(1)  # Wait before retrying
        print("On-screen keyboard not found after retries.")
    except Exception as e:
        print(f"Error minimizing on-screen keyboard: {e}")


def minimize_terminal_cross_platform():
    """Minimize the terminal window."""
    try:
        if wm.minimize_terminal():
            print("Terminal minimized.")
        else:
            print("Could not minimize terminal.")
    except Exception as e:
        print(f"Error minimizing terminal: {e}")


def is_dev_mode():
    """
    Check if dev mode is enabled via environment variable.
    In dev mode, applications will not open in fullscreen.
    
    Set DEV_MODE=1 or DEV_MODE=true to enable dev mode.
    """
    import os
    dev_mode = os.environ.get('DEV_MODE', '').lower()
    return dev_mode in ('1', 'true', 'yes', 'on')


def set_fullscreen_if_not_dev_mode(window):
    """
    Set window to fullscreen unless dev mode is enabled.
    
    Args:
        window: Tkinter window object
    """
    if not is_dev_mode():
        window.attributes("-fullscreen", True)
        print("Fullscreen mode enabled.")
    else:
        # In dev mode, set a reasonable window size instead
        window.geometry("1200x800")
        print("Dev mode: Window opened in windowed mode (1200x800).")