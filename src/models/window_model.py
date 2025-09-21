import logging
import time
import platform
import psutil
from typing import Optional, List, Tuple

# Windows-specific imports with platform check
if platform.system() == "Windows":
    import ctypes
    import ctypes.wintypes
    import pygetwindow as gw
    import win32gui
    import win32con
    import win32process
else:
    # Linux alternatives - define stubs so module can be imported on non-Windows
    ctypes = None
    gw = None
    win32gui = None
    win32con = None
    win32process = None


class WindowModel:
    """Enhanced model for handling window management and focusing"""

    def __init__(self, config_model=None):
        self.logger = logging.getLogger("Dota2AutoAccept.WindowModel")
        self.config_model = config_model
        
        # Windows API constants
        self.SW_RESTORE = 9
        self.SW_MAXIMIZE = 3
        self.SW_SHOW = 5
        self.HWND_TOP = 0
        self.SWP_SHOWWINDOW = 0x0040
        self.SWP_NOSIZE = 0x0001
        self.SWP_NOMOVE = 0x0002

    def get_dota2_processes(self) -> List[dict]:
        """Get all Dota 2 related processes"""
        dota_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    name = proc.info['name'].lower()
                    if any(keyword in name for keyword in ['dota', 'dota2']):
                        dota_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'exe': proc.info['exe']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Error getting Dota 2 processes: {e}")
        
        return dota_processes

    def get_dota2_windows(self) -> List[dict]:
        """Get all Dota 2 windows with detailed information"""
        windows = []

        # If not on Windows, return empty list as we cannot enumerate windows
        if platform.system() != "Windows":
            self.logger.debug("get_dota2_windows: non-Windows platform detected, returning empty list")
            return windows
        
        def enum_window_callback(hwnd, windows_list):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text and any(keyword.lower() in window_text.lower() 
                                         for keyword in ['Dota 2', 'dota']):
                        # Get process info
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            process = psutil.Process(pid)
                            process_name = process.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            process_name = "Unknown"
                        
                        # Get window state
                        placement = win32gui.GetWindowPlacement(hwnd)
                        is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
                        
                        windows_list.append({
                            'hwnd': hwnd,
                            'title': window_text,
                            'pid': pid,
                            'process_name': process_name,
                            'is_minimized': is_minimized,
                            'is_visible': win32gui.IsWindowVisible(hwnd)
                        })
            except Exception as e:
                self.logger.debug(f"Error processing window {hwnd}: {e}")
        
        try:
            win32gui.EnumWindows(enum_window_callback, windows)
        except Exception as e:
            self.logger.error(f"Error enumerating windows: {e}")
        
        return windows

    def force_focus_window(self, hwnd: int) -> bool:
        """Force focus on a window using aggressive Windows API methods"""
        # On non-Windows platforms, we cannot force focus using Win32 APIs
        if platform.system() != "Windows":
            self.logger.warning("force_focus_window: non-Windows platform detected, skipping aggressive focus")
            return False

        try:
            # Get delay from config or use default
            delay = (self.config_model.focus_delay_ms / 1000.0) if self.config_model else 0.1
            
            self.logger.info(f"Starting aggressive window focus for HWND: {hwnd}")
            
            # Step 1: Ensure window is visible and not minimized
            if win32gui.IsIconic(hwnd):
                self.logger.info("Window is minimized, restoring...")
                win32gui.ShowWindow(hwnd, self.SW_RESTORE)
                time.sleep(delay * 2)
            
            # Step 2: Make window visible and active
            win32gui.ShowWindow(hwnd, self.SW_SHOW)
            time.sleep(delay)
            
            # Step 3: Bring window to top Z-order
            win32gui.BringWindowToTop(hwnd)
            time.sleep(delay)
            
            # Step 4: Set window position to topmost temporarily
            win32gui.SetWindowPos(
                hwnd, -1, 0, 0, 0, 0,  # -1 = HWND_TOPMOST
                self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW
            )
            time.sleep(delay)
            
            # Step 5: Aggressive foreground window setting
            current_foreground = win32gui.GetForegroundWindow()
            if current_foreground != hwnd:
                try:
                    # Get current thread ID
                    current_thread = ctypes.windll.kernel32.GetCurrentThreadId()
                    # Get target window thread ID
                    target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]
                    
                    if current_thread != target_thread:
                        # Attach to target window's input queue
                        ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, True)
                        time.sleep(delay / 2)
                    
                    # Try multiple foreground methods
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(delay / 2)
                    
                    # Alternative method using user32.dll directly
                    ctypes.windll.user32.SetForegroundWindow(hwnd)
                    time.sleep(delay / 2)
                    
                    # Force window activation
                    ctypes.windll.user32.SetActiveWindow(hwnd)
                    time.sleep(delay / 2)
                    
                    if current_thread != target_thread:
                        # Detach from input queue
                        ctypes.windll.user32.AttachThreadInput(current_thread, target_thread, False)
                        
                except Exception as e:
                    self.logger.warning(f"Advanced foreground setting failed: {e}")
            
            # Step 6: Send Alt+Tab effect to ensure focus
            try:
                # Simulate Alt key press to trigger window switching mechanism
                ctypes.windll.user32.keybd_event(0x12, 0, 0, 0)  # Alt down
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(0x12, 0, 2, 0)  # Alt up
                time.sleep(delay)
            except Exception as e:
                self.logger.warning(f"Alt+Tab simulation failed: {e}")
            
            # Step 7: Remove topmost flag and set to normal top
            win32gui.SetWindowPos(
                hwnd, self.HWND_TOP, 0, 0, 0, 0,
                self.SWP_NOMOVE | self.SWP_NOSIZE | self.SWP_SHOWWINDOW
            )
            time.sleep(delay)
            
            # Step 8: Final activation attempt
            try:
                # Use SwitchToThisWindow as last resort
                ctypes.windll.user32.SwitchToThisWindow(hwnd, True)
                time.sleep(delay)
            except Exception as e:
                self.logger.warning(f"SwitchToThisWindow failed: {e}")
            
            # Step 9: Verify the window is now focused
            current_foreground = win32gui.GetForegroundWindow()
            success = current_foreground == hwnd
            
            if success:
                self.logger.info(f"✅ Successfully focused window {hwnd}")
            else:
                self.logger.warning(f"❌ Window {hwnd} focus verification failed. Current foreground: {current_foreground}")
                # Additional verification - check if our window is at least visible and on top
                try:
                    window_rect = win32gui.GetWindowRect(hwnd)
                    is_visible = win32gui.IsWindowVisible(hwnd)
                    self.logger.info(f"Window state - Visible: {is_visible}, Rect: {window_rect}")
                except Exception as e:
                    self.logger.warning(f"Could not get window state: {e}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error forcing focus on window {hwnd}: {e}")
            return False

    def focus_dota2_window_enhanced(self) -> bool:
        """Enhanced strategy to focus Dota 2 window with aggressive methods"""
        success = False
        max_attempts = self.config_model.focus_retry_attempts if self.config_model else 3
        
        self.logger.info(f"🎯 Starting enhanced Dota 2 window focus (max {max_attempts} attempts)")
        
        for attempt in range(max_attempts):
            if attempt > 0:
                self.logger.info(f"🔄 Window focus attempt {attempt + 1}/{max_attempts}")
                time.sleep(1.0)  # Longer wait between attempts
            
            # Strategy 1: Windows API with improved window selection
            try:
                # If not Windows, skip aggressive focusing but still try to detect processes
                if platform.system() != "Windows":
                    self.logger.info("Non-Windows platform detected - skipping window focusing and returning process info only")
                    dota_processes = self.get_dota2_processes()
                    # If a Dota process exists, consider this a 'soft success' to allow rest of app to proceed
                    if dota_processes:
                        self.logger.info(f"Found {len(dota_processes)} Dota 2 processes (no window operations on Linux)")
                        return True
                    return False

                dota_windows = self.get_dota2_windows()
                self.logger.info(f"Found {len(dota_windows)} Dota 2 windows")
                
                if dota_windows:
                    # Sort windows by priority:
                    # 1. Non-minimized main Dota 2 windows first
                    # 2. Visible windows
                    # 3. Any Dota 2 window
                    def window_priority(window):
                        priority = 0
                        # Prefer non-minimized windows
                        if not window['is_minimized']:
                            priority += 100
                        # Prefer visible windows
                        if window['is_visible']:
                            priority += 50
                        # Prefer main Dota 2 window over other Dota apps
                        if window['title'] == "Dota 2":
                            priority += 25
                        # Prefer windows with actual Dota 2 process
                        if "dota2.exe" in window['process_name'].lower():
                            priority += 10
                        return priority
                    
                    sorted_windows = sorted(dota_windows, key=window_priority, reverse=True)
                    
                    # Try each window in priority order
                    for i, window in enumerate(sorted_windows):
                        self.logger.info(f"🎮 Attempting to focus window {i+1}/{len(sorted_windows)}: "
                                       f"{window['title']} (PID: {window['pid']}, "
                                       f"Minimized: {window['is_minimized']}, Process: {window['process_name']})")
                        
                        if self.force_focus_window(window['hwnd']):
                            success = True
                            self.logger.info(f"✅ Successfully focused Dota 2 window: {window['title']}")
                            break
                        else:
                            self.logger.warning(f"❌ Failed to focus window: {window['title']}")
                            
                    if success:
                        break
                else:
                    self.logger.warning("No Dota 2 windows found using Windows API")
                    
            except Exception as e:
                self.logger.error(f"Windows API window focusing failed: {e}")
            
            # Strategy 2: Enhanced pygetwindow with multiple window types
            if not success:
                try:
                    self.logger.info("🔄 Attempting enhanced pygetwindow method")
                    
                    # Try different window title variations
                    title_variations = ["Dota 2", "dota 2", "DOTA 2", "Dota2"]
                    
                    for title in title_variations:
                        dota_windows = gw.getWindowsWithTitle(title)
                        if dota_windows:
                            self.logger.info(f"Found {len(dota_windows)} windows with title '{title}'")
                            
                            for window in dota_windows:
                                try:
                                    self.logger.info(f"🎮 Focusing window: {window.title}")
                                    
                                    # Multiple restore attempts
                                    if window.isMinimized:
                                        self.logger.info("Window is minimized, restoring...")
                                        window.restore()
                                        time.sleep(0.5)
                                    
                                    # Maximize if needed for better visibility
                                    if hasattr(window, 'maximize'):
                                        try:
                                            window.maximize()
                                            time.sleep(0.3)
                                        except:
                                            pass
                                    
                                    # Multiple activation attempts
                                    for activate_attempt in range(3):
                                        window.activate()
                                        time.sleep(0.2)
                                        
                                        # Check if successful
                                        try:
                                            active_window = gw.getActiveWindow()
                                            if active_window and active_window.title == window.title:
                                                success = True
                                                self.logger.info(f"✅ Successfully activated window via pygetwindow")
                                                break
                                        except:
                                            pass
                                    
                                    if success:
                                        break
                                        
                                except Exception as e:
                                    self.logger.warning(f"Failed to focus window {window.title}: {e}")
                            
                            if success:
                                break
                        
                    if not success:
                        self.logger.warning("No Dota 2 windows found using pygetwindow")
                        
                except Exception as e:
                    self.logger.error(f"Enhanced pygetwindow focusing failed: {e}")
            
            # Strategy 3: Process-based with enhanced window detection
            if not success:
                try:
                    self.logger.info("🔄 Attempting enhanced process-based window focusing")
                    dota_processes = self.get_dota2_processes()
                    
                    for proc_info in dota_processes:
                        pid = proc_info['pid']
                        self.logger.info(f"🎮 Checking process: {proc_info['name']} (PID: {pid})")
                        
                        def enum_proc_windows(hwnd, results):
                            try:
                                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                                if window_pid == pid:
                                    window_title = win32gui.GetWindowText(hwnd)
                                    is_visible = win32gui.IsWindowVisible(hwnd)
                                    
                                    # Focus any visible window for this process
                                    if is_visible and window_title:
                                        self.logger.info(f"🎮 Found window for process: '{window_title}'")
                                        if self.force_focus_window(hwnd):
                                            results.append(True)
                                            return False  # Stop enumeration
                            except Exception as e:
                                self.logger.debug(f"Error processing window: {e}")
                            return True
                        
                        result = []
                        win32gui.EnumWindows(enum_proc_windows, result)
                        if result:
                            success = True
                            self.logger.info(f"✅ Successfully focused window for process PID: {pid}")
                            break
                            
                except Exception as e:
                    self.logger.error(f"Process-based focusing failed: {e}")
            
            # If we succeeded, break out of retry loop
            if success:
                break
            else:
                self.logger.warning(f"❌ Focus attempt {attempt + 1} failed, retrying...")
        
        if not success:
            self.logger.error("❌ All Dota 2 window focusing strategies failed after all attempts")
        else:
            self.logger.info("🎉 Dota 2 window focusing completed successfully!")
        
        return success

    def get_window_info(self, hwnd: int) -> dict:
        """Get detailed information about a window"""
        try:
            info = {
                'hwnd': hwnd,
                'title': win32gui.GetWindowText(hwnd),
                'class_name': win32gui.GetClassName(hwnd),
                'is_visible': win32gui.IsWindowVisible(hwnd),
                'is_enabled': win32gui.IsWindowEnabled(hwnd),
                'rect': win32gui.GetWindowRect(hwnd),
                'placement': win32gui.GetWindowPlacement(hwnd)
            }
            
            # Get process information
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                info.update({
                    'pid': pid,
                    'process_name': process.name(),
                    'process_exe': process.exe()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                info.update({
                    'pid': None,
                    'process_name': 'Unknown',
                    'process_exe': 'Unknown'
                })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting window info for {hwnd}: {e}")
            return {}

    def list_all_dota2_related_windows(self) -> List[dict]:
        """List all Dota 2 related windows for debugging"""
        all_windows = []
        
        def enum_all_windows(hwnd, windows_list):
            try:
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    
                    # Check if it's Dota 2 related
                    if title and any(keyword.lower() in title.lower() 
                                   for keyword in ['dota', 'steam', 'valve']):
                        window_info = self.get_window_info(hwnd)
                        windows_list.append(window_info)
            except Exception:
                pass
            return True
        
        try:
            win32gui.EnumWindows(enum_all_windows, all_windows)
        except Exception as e:
            self.logger.error(f"Error listing all windows: {e}")
        
        return all_windows
