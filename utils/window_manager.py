"""
Unified Window Management Abstraction Layer
Provides cross-platform window management functionality for Ben's accessibility software.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Callable, Any, Dict
import platform


class WindowHandle:
    """Abstract representation of a window handle across platforms."""
    
    def __init__(self, native_handle: Any, title: str = "", class_name: str = ""):
        self.native_handle = native_handle
        self.title = title
        self.class_name = class_name
    
    def __str__(self):
        return f"WindowHandle(title='{self.title}', class='{self.class_name}')"
    
    def __bool__(self):
        return self.native_handle is not None


class WindowManager(ABC):
    """Abstract base class for cross-platform window management."""
    
    # Window show states (matching Windows constants)
    SW_HIDE = 0
    SW_SHOWNORMAL = 1
    SW_SHOWMINIMIZED = 2
    SW_SHOWMAXIMIZED = 3
    SW_SHOWNOACTIVATE = 4
    SW_SHOW = 5
    SW_MINIMIZE = 6
    SW_SHOWMINNOACTIVE = 7
    SW_SHOWNA = 8
    SW_RESTORE = 9
    SW_SHOWDEFAULT = 10
    
    # Key codes
    VK_ESCAPE = 0x1B
    VK_VOLUME_UP = 0xAF
    VK_VOLUME_DOWN = 0xAE
    
    @abstractmethod
    def find_window(self, class_name: Optional[str] = None, 
                   window_title: Optional[str] = None) -> WindowHandle:
        """Find a window by class name and/or title."""
        pass
    
    @abstractmethod
    def get_foreground_window(self) -> WindowHandle:
        """Get the currently active/focused window."""
        pass
    
    @abstractmethod
    def set_foreground_window(self, handle: WindowHandle) -> bool:
        """Bring a window to the foreground."""
        pass
    
    @abstractmethod
    def show_window(self, handle: WindowHandle, show_state: int) -> bool:
        """Show/hide/minimize/maximize a window."""
        pass
    
    @abstractmethod
    def get_window_text(self, handle: WindowHandle) -> str:
        """Get the title text of a window."""
        pass
    
    @abstractmethod
    def get_class_name(self, handle: WindowHandle) -> str:
        """Get the class name of a window."""
        pass
    
    @abstractmethod
    def is_window_visible(self, handle: WindowHandle) -> bool:
        """Check if a window is visible."""
        pass
    
    @abstractmethod
    def enum_windows(self, callback: Callable[[WindowHandle], bool]) -> List[WindowHandle]:
        """Enumerate all windows, calling callback for each."""
        pass
    
    @abstractmethod
    def send_message(self, handle: WindowHandle, msg: int, wparam: int, lparam: int) -> int:
        """Send a message to a window."""
        pass
    
    @abstractmethod
    def send_key(self, key_code: int, key_up: bool = True) -> None:
        """Send a key press (and optionally key release)."""
        pass
    
    @abstractmethod
    def lock_workstation(self) -> bool:
        """Lock the workstation/screen."""
        pass
    
    @abstractmethod
    def get_console_window(self) -> WindowHandle:
        """Get the console window handle."""
        pass
    
    @abstractmethod
    def minimize_terminal(self) -> bool:
        """Minimize the terminal window."""
        pass
    
    @abstractmethod
    def is_system_menu_open(self) -> bool:
        """Check if system menus (Start menu, Spotlight, etc.) are open."""
        pass
    
    @abstractmethod
    def close_system_menus(self) -> None:
        """Close any open system menus."""
        pass
    
    @abstractmethod
    def get_active_app_name(self) -> str:
        """Get the name of the currently active application."""
        pass
    
    @abstractmethod
    def activate_app(self, app_name: str) -> bool:
        """Activate an application by name."""
        pass
    
    @abstractmethod
    def get_all_windows(self) -> List[WindowHandle]:
        """Get all visible windows."""
        pass


def create_window_manager() -> WindowManager:
    """Factory function to create the appropriate window manager for the current platform."""
    system = platform.system()
    
    if system == "Windows":
        from .window_manager_windows import WindowsWindowManager
        return WindowsWindowManager()
    elif system == "Darwin":
        from .window_manager_macos import MacOSWindowManager
        return MacOSWindowManager()
    else:
        from .window_manager_stub import StubWindowManager
        return StubWindowManager()


# Global instance - singleton pattern
_window_manager: Optional[WindowManager] = None


def get_window_manager() -> WindowManager:
    """Get the global window manager instance."""
    global _window_manager
    if _window_manager is None:
        _window_manager = create_window_manager()
    return _window_manager