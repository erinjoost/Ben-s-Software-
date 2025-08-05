"""
macOS implementation of the WindowManager using AppleScript and pyobjc.
"""

import subprocess
import time
from typing import Optional, List, Callable
from .window_manager import WindowManager, WindowHandle


class MacOSWindowManager(WindowManager):
    """macOS-specific window manager implementation using AppleScript and pyobjc."""
    
    def __init__(self):
        self._app_cache = {}  # Cache for app name lookups
        
        # Try to import pyobjc for native Cocoa access
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self._pyautogui_available = True
        except ImportError:
            self._pyautogui_available = False
            print("Warning: pyautogui not available for macOS window management")
    
    def _run_applescript(self, script: str, timeout: int = 5) -> str:
        """Run an AppleScript and return the output."""
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Suppress common AppleScript errors that don't affect functionality
                error_msg = result.stderr.strip()
                if "Invalid index" not in error_msg and "Can't get item" not in error_msg:
                    print(f"AppleScript error: {error_msg}")
                return ""
        except subprocess.TimeoutExpired:
            print(f"AppleScript timeout after {timeout}s")
            return ""
        except Exception as e:
            print(f"AppleScript execution error: {e}")
            return ""
    
    def find_window(self, class_name: Optional[str] = None, 
                   window_title: Optional[str] = None) -> WindowHandle:
        """Find a window by class name and/or title (approximated on macOS)."""
        # On macOS, we approximate by finding apps with similar names
        if window_title:
            # Try to find an app with this title or containing this title
            script = f'''
            tell application "System Events"
                set appList to {{}}
                repeat with proc in application processes
                    if visible of proc is true then
                        set appName to name of proc
                        if appName contains "{window_title}" then
                            return appName
                        end if
                    end if
                end repeat
                return ""
            end tell
            '''
            app_name = self._run_applescript(script)
            if app_name:
                return WindowHandle(app_name, window_title, class_name or "")
        
        return WindowHandle(None)
    
    def get_foreground_window(self) -> WindowHandle:
        """Get the currently active/focused window."""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        app_name = self._run_applescript(script)
        if app_name:
            return WindowHandle(app_name, app_name, "")
        return WindowHandle(None)
    
    def set_foreground_window(self, handle: WindowHandle) -> bool:
        """Bring a window to the foreground."""
        if not handle or not handle.native_handle:
            return False
        
        app_name = handle.native_handle
        script = f'''
        tell application "{app_name}"
            activate
            set frontmost to true
        end tell
        '''
        result = self._run_applescript(script)
        return result != ""
    
    def show_window(self, handle: WindowHandle, show_state: int) -> bool:
        """Show/hide/minimize/maximize a window."""
        if not handle or not handle.native_handle:
            return False
        
        app_name = handle.native_handle
        
        if show_state == self.SW_MINIMIZE:
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set miniaturized of front window to true
                end tell
            end tell
            '''
        elif show_state == self.SW_MAXIMIZE:
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set miniaturized of front window to false
                    set zoomed of front window to true
                end tell
            end tell
            '''
        elif show_state == self.SW_RESTORE:
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set miniaturized of front window to false
                    set zoomed of front window to false
                end tell
            end tell
            '''
        else:
            return False
        
        result = self._run_applescript(script)
        return result != ""
    
    def get_window_text(self, handle: WindowHandle) -> str:
        """Get the title text of a window."""
        if not handle:
            return ""
        return handle.title or handle.native_handle or ""
    
    def get_class_name(self, handle: WindowHandle) -> str:
        """Get the class name of a window."""
        if not handle:
            return ""
        return handle.class_name or ""
    
    def is_window_visible(self, handle: WindowHandle) -> bool:
        """Check if a window is visible."""
        if not handle or not handle.native_handle:
            return False
        
        app_name = handle.native_handle
        script = f'''
        tell application "System Events"
            if exists (application process "{app_name}") then
                return visible of application process "{app_name}"
            else
                return false
            end if
        end tell
        '''
        result = self._run_applescript(script)
        return result.lower() == "true"
    
    def enum_windows(self, callback: Callable[[WindowHandle], bool]) -> List[WindowHandle]:
        """Enumerate all windows, calling callback for each."""
        script = '''
        tell application "System Events"
            set appList to {}
            try
                repeat with proc in application processes
                    try
                        if visible of proc is true then
                            set end of appList to name of proc
                        end if
                    on error
                        -- Skip problematic processes
                    end try
                end repeat
            on error
                -- If enumeration fails, return empty list
            end try
            return appList
        end tell
        '''
        result = self._run_applescript(script)
        windows = []
        
        if result:
            apps = [app.strip() for app in result.split(', ')]
            for app in apps:
                if app:  # Skip empty entries
                    handle = WindowHandle(app, app, "")
                    windows.append(handle)
                    if not callback(handle):
                        break
        
        return windows
    
    def send_message(self, handle: WindowHandle, msg: int, wparam: int, lparam: int) -> int:
        """Send a message to a window (limited on macOS)."""
        # Most Windows messages don't have direct macOS equivalents
        # We can implement specific cases as needed
        if msg == 0x0010:  # WM_CLOSE
            if handle and handle.native_handle:
                script = f'''
                tell application "{handle.native_handle}"
                    quit
                end tell
                '''
                self._run_applescript(script)
                return 1
        return 0
    
    def send_key(self, key_code: int, key_up: bool = True) -> None:
        """Send a key press (and optionally key release)."""
        if self._pyautogui_available:
            if key_code == self.VK_ESCAPE:
                self.pyautogui.press('escape')
            elif key_code == self.VK_VOLUME_UP:
                self.pyautogui.press('volumeup')
            elif key_code == self.VK_VOLUME_DOWN:
                self.pyautogui.press('volumedown')
        else:
            # Fallback using AppleScript for common keys
            key_name = ""
            if key_code == self.VK_ESCAPE:
                key_name = "escape"
            elif key_code == self.VK_VOLUME_UP:
                key_name = "volume up"
            elif key_code == self.VK_VOLUME_DOWN:
                key_name = "volume down"
            
            if key_name:
                script = f'''
                tell application "System Events"
                    key code 53  -- ESC key code
                end tell
                ''' if key_code == self.VK_ESCAPE else f'''
                tell application "System Events"
                    key code {key_code}
                end tell
                '''
                self._run_applescript(script)
    
    def lock_workstation(self) -> bool:
        """Lock the workstation/screen."""
        script = '''
        tell application "System Events"
            do shell script "pmset displaysleepnow"
        end tell
        '''
        result = self._run_applescript(script)
        return result != ""
    
    def get_console_window(self) -> WindowHandle:
        """Get the console window handle (Terminal on macOS)."""
        terminal = self.find_window(None, "Terminal")
        if not terminal:
            # Try to find any terminal-like app
            for app_name in ["Terminal", "iTerm2", "Hyper", "Alacritty"]:
                terminal = self.find_window(None, app_name)
                if terminal:
                    break
        return terminal or WindowHandle(None)
    
    def minimize_terminal(self) -> bool:
        """Minimize the terminal window."""
        script = '''
        tell application "Terminal"
            if exists front window then
                set miniaturized of front window to true
                return "success"
            else
                return "no window"
            end if
        end tell
        '''
        result = self._run_applescript(script)
        return "success" in result
    
    def is_system_menu_open(self) -> bool:
        """Check if system menus (Spotlight, Notification Center, etc.) are open."""
        script = '''
        tell application "System Events"
            try
                if (count of application processes) > 0 then
                    set frontApp to name of first application process whose frontmost is true
                    if frontApp is in {"Spotlight", "NotificationCenter", "Dock", "SystemUIServer", "ControlCenter"} then
                        return "true"
                    else
                        return "false"
                    end if
                else
                    return "false"
                end if
            on error
                return "false"
            end try
        end tell
        '''
        result = self._run_applescript(script)
        return result.lower() == "true"
    
    def close_system_menus(self) -> None:
        """Close any open system menus."""
        # Send ESC key to close menus
        self.send_key(self.VK_ESCAPE)
    
    def get_active_app_name(self) -> str:
        """Get the name of the currently active application."""
        fg_window = self.get_foreground_window()
        return fg_window.title if fg_window else ""
    
    def activate_app(self, app_name: str) -> bool:
        """Activate an application by name."""
        script = f'''
        tell application "{app_name}"
            activate
        end tell
        '''
        result = self._run_applescript(script)
        return result != ""
    
    def get_all_windows(self) -> List[WindowHandle]:
        """Get all visible windows."""
        def collect_all(handle: WindowHandle) -> bool:
            return True  # Collect all
        
        return self.enum_windows(collect_all)