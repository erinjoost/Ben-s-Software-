"""
Windows implementation of the WindowManager using win32gui APIs.
"""

from typing import Optional, List, Callable
from .window_manager import WindowManager, WindowHandle


class WindowsWindowManager(WindowManager):
    """Windows-specific window manager implementation using win32gui."""
    
    def __init__(self):
        try:
            import win32gui
            import win32con
            import win32api
            import ctypes
            self.win32gui = win32gui
            self.win32con = win32con
            self.win32api = win32api
            self.ctypes = ctypes
            self._available = True
        except ImportError as e:
            print(f"Warning: Windows APIs not available: {e}")
            self._available = False
    
    def find_window(self, class_name: Optional[str] = None, 
                   window_title: Optional[str] = None) -> WindowHandle:
        """Find a window by class name and/or title."""
        if not self._available:
            return WindowHandle(None)
        
        try:
            hwnd = self.win32gui.FindWindow(class_name, window_title)
            if hwnd:
                title = self.get_window_text(WindowHandle(hwnd)) if not window_title else window_title
                cls = self.get_class_name(WindowHandle(hwnd)) if not class_name else class_name
                return WindowHandle(hwnd, title, cls)
            return WindowHandle(None)
        except Exception as e:
            print(f"Error finding window: {e}")
            return WindowHandle(None)
    
    def get_foreground_window(self) -> WindowHandle:
        """Get the currently active/focused window."""
        if not self._available:
            return WindowHandle(None)
        
        try:
            hwnd = self.win32gui.GetForegroundWindow()
            if hwnd:
                title = self.get_window_text(WindowHandle(hwnd))
                cls = self.get_class_name(WindowHandle(hwnd))
                return WindowHandle(hwnd, title, cls)
            return WindowHandle(None)
        except Exception as e:
            print(f"Error getting foreground window: {e}")
            return WindowHandle(None)
    
    def set_foreground_window(self, handle: WindowHandle) -> bool:
        """Bring a window to the foreground."""
        if not self._available or not handle:
            return False
        
        try:
            return self.win32gui.SetForegroundWindow(handle.native_handle)
        except Exception as e:
            print(f"Error setting foreground window: {e}")
            return False
    
    def show_window(self, handle: WindowHandle, show_state: int) -> bool:
        """Show/hide/minimize/maximize a window."""
        if not self._available or not handle:
            return False
        
        try:
            return self.win32gui.ShowWindow(handle.native_handle, show_state)
        except Exception as e:
            print(f"Error showing window: {e}")
            return False
    
    def get_window_text(self, handle: WindowHandle) -> str:
        """Get the title text of a window."""
        if not self._available or not handle:
            return ""
        
        try:
            return self.win32gui.GetWindowText(handle.native_handle)
        except Exception as e:
            print(f"Error getting window text: {e}")
            return ""
    
    def get_class_name(self, handle: WindowHandle) -> str:
        """Get the class name of a window."""
        if not self._available or not handle:
            return ""
        
        try:
            return self.win32gui.GetClassName(handle.native_handle)
        except Exception as e:
            print(f"Error getting class name: {e}")
            return ""
    
    def is_window_visible(self, handle: WindowHandle) -> bool:
        """Check if a window is visible."""
        if not self._available or not handle:
            return False
        
        try:
            return self.win32gui.IsWindowVisible(handle.native_handle)
        except Exception as e:
            print(f"Error checking window visibility: {e}")
            return False
    
    def enum_windows(self, callback: Callable[[WindowHandle], bool]) -> List[WindowHandle]:
        """Enumerate all windows, calling callback for each."""
        if not self._available:
            return []
        
        windows = []
        
        def win32_callback(hwnd, _):
            handle = WindowHandle(hwnd, 
                                self.get_window_text(WindowHandle(hwnd)),
                                self.get_class_name(WindowHandle(hwnd)))
            windows.append(handle)
            return callback(handle)
        
        try:
            self.win32gui.EnumWindows(win32_callback, None)
            return windows
        except Exception as e:
            print(f"Error enumerating windows: {e}")
            return []
    
    def send_message(self, handle: WindowHandle, msg: int, wparam: int, lparam: int) -> int:
        """Send a message to a window."""
        if not self._available or not handle:
            return 0
        
        try:
            return self.win32gui.SendMessage(handle.native_handle, msg, wparam, lparam)
        except Exception as e:
            print(f"Error sending message: {e}")
            return 0
    
    def send_key(self, key_code: int, key_up: bool = True) -> None:
        """Send a key press (and optionally key release)."""
        if not self._available:
            return
        
        try:
            # Key down
            self.ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
            if key_up:
                # Key up
                self.ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)
        except Exception as e:
            print(f"Error sending key: {e}")
    
    def lock_workstation(self) -> bool:
        """Lock the workstation/screen."""
        if not self._available:
            return False
        
        try:
            return self.ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            print(f"Error locking workstation: {e}")
            return False
    
    def get_console_window(self) -> WindowHandle:
        """Get the console window handle."""
        if not self._available:
            return WindowHandle(None)
        
        try:
            hwnd = self.ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                return WindowHandle(hwnd, "Console", "ConsoleWindowClass")
            return WindowHandle(None)
        except Exception as e:
            print(f"Error getting console window: {e}")
            return WindowHandle(None)
    
    def minimize_terminal(self) -> bool:
        """Minimize the terminal window."""
        console = self.get_console_window()
        if console:
            return self.show_window(console, self.SW_MINIMIZE)
        return False
    
    def is_system_menu_open(self) -> bool:
        """Check if system menus (Start menu, etc.) are open."""
        if not self._available:
            return False
        
        try:
            fg_window = self.get_foreground_window()
            if fg_window:
                class_name = fg_window.class_name
                return class_name in ["Shell_TrayWnd", "Windows.UI.Core.CoreWindow", "DV2ControlHost"]
            return False
        except Exception as e:
            print(f"Error checking system menu: {e}")
            return False
    
    def close_system_menus(self) -> None:
        """Close any open system menus."""
        if not self._available:
            return
        
        try:
            # Send ESC key to close menus
            self.send_key(self.VK_ESCAPE)
            
            # Also try to close Start menu specifically
            start_menu = self.find_window("DV2ControlHost", None)
            if start_menu:
                self.send_message(start_menu, 0x0010, 0, 0)  # WM_CLOSE
        except Exception as e:
            print(f"Error closing system menus: {e}")
    
    def get_active_app_name(self) -> str:
        """Get the name of the currently active application."""
        fg_window = self.get_foreground_window()
        return fg_window.title if fg_window else ""
    
    def activate_app(self, app_name: str) -> bool:
        """Activate an application by name."""
        window = self.find_window(None, app_name)
        if window:
            self.show_window(window, self.SW_RESTORE)
            return self.set_foreground_window(window)
        return False
    
    def get_all_windows(self) -> List[WindowHandle]:
        """Get all visible windows."""
        def collect_visible(handle: WindowHandle) -> bool:
            return True  # Collect all, filter below
        
        all_windows = self.enum_windows(collect_visible)
        return [w for w in all_windows if self.is_window_visible(w) and w.title]