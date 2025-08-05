"""
Stub implementation of the WindowManager for unsupported platforms.
Provides no-op implementations to prevent crashes.
"""

from typing import Optional, List, Callable
from .window_manager import WindowManager, WindowHandle


class StubWindowManager(WindowManager):
    """Stub window manager implementation for unsupported platforms."""
    
    def __init__(self):
        print("Warning: Using stub window manager - window management not available on this platform")
    
    def find_window(self, class_name: Optional[str] = None, 
                   window_title: Optional[str] = None) -> WindowHandle:
        """Find a window by class name and/or title."""
        return WindowHandle(None)
    
    def get_foreground_window(self) -> WindowHandle:
        """Get the currently active/focused window."""
        return WindowHandle(None)
    
    def set_foreground_window(self, handle: WindowHandle) -> bool:
        """Bring a window to the foreground."""
        return False
    
    def show_window(self, handle: WindowHandle, show_state: int) -> bool:
        """Show/hide/minimize/maximize a window."""
        return False
    
    def get_window_text(self, handle: WindowHandle) -> str:
        """Get the title text of a window."""
        return ""
    
    def get_class_name(self, handle: WindowHandle) -> str:
        """Get the class name of a window."""
        return ""
    
    def is_window_visible(self, handle: WindowHandle) -> bool:
        """Check if a window is visible."""
        return False
    
    def enum_windows(self, callback: Callable[[WindowHandle], bool]) -> List[WindowHandle]:
        """Enumerate all windows, calling callback for each."""
        return []
    
    def send_message(self, handle: WindowHandle, msg: int, wparam: int, lparam: int) -> int:
        """Send a message to a window."""
        return 0
    
    def send_key(self, key_code: int, key_up: bool = True) -> None:
        """Send a key press (and optionally key release)."""
        pass
    
    def lock_workstation(self) -> bool:
        """Lock the workstation/screen."""
        return False
    
    def get_console_window(self) -> WindowHandle:
        """Get the console window handle."""
        return WindowHandle(None)
    
    def minimize_terminal(self) -> bool:
        """Minimize the terminal window."""
        return False
    
    def is_system_menu_open(self) -> bool:
        """Check if system menus are open."""
        return False
    
    def close_system_menus(self) -> None:
        """Close any open system menus."""
        pass
    
    def get_active_app_name(self) -> str:
        """Get the name of the currently active application."""
        return ""
    
    def activate_app(self, app_name: str) -> bool:
        """Activate an application by name."""
        return False
    
    def get_all_windows(self) -> List[WindowHandle]:
        """Get all visible windows."""
        return []