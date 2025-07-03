import os
import logging
import datetime
import cv2
import numpy as np
import mss
from PIL import Image
from typing import Optional, List, Tuple

class ScreenshotModel:
    """Model for handling screenshot capture functionality"""
    
    def __init__(self):
        self.logger = logging.getLogger("Dota2AutoAccept.ScreenshotModel")
        self.latest_screenshot_img = None
        self.latest_screenshot_time = None
    
    def get_available_monitors(self) -> List[Tuple[str, int]]:
        """Get list of available monitors"""
        monitor_options = []
        try:
            with mss.mss() as sct:
                # sct.monitors[0] is the full virtual screen, physical monitors start at index 1
                if len(sct.monitors) > 1:
                    for i, monitor in enumerate(sct.monitors[1:], start=1):
                        monitor_options.append(
                            (f"Monitor {i} ({monitor['width']}x{monitor['height']})", i)
                        )
                else:
                    self.logger.warning(
                        "No individual monitors detected by mss, only the combined virtual screen."
                    )
        except Exception as e:
            self.logger.error(f"Error getting monitor list: {e}")
        return monitor_options
    
    def capture_monitor_screenshot(self, _unused=None) -> Optional[Image.Image]:
        """Capture screenshot from the monitor where Dota 2 is running (auto-detect, even if minimized)"""
        monitor_index = self.auto_detect_dota_monitor()
        if monitor_index is None:
            self.logger.warning("Could not auto-detect Dota 2 monitor, defaulting to primary monitor.")
            monitor_index = 1
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                self.logger.warning("No distinct monitors found by mss to capture from!")
                return None
            if not isinstance(monitor_index, int) or not (0 < monitor_index < len(monitors)):
                self.logger.warning(
                    f"Invalid monitor index {monitor_index} specified. "
                    f"Available: 1 to {len(monitors)-1}. Screenshot not taken."
                )
                return None
            monitor = monitors[monitor_index]
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                self.latest_screenshot_time = datetime.datetime.now()
                self.latest_screenshot_img = img.copy()
                return img
            except Exception as e:
                self.logger.error(
                    f"An unexpected error occurred while capturing screenshot from "
                    f"Monitor {monitor_index}: {e}"
                )
                return None
    
    def save_monitor_screenshot(self, filename: str, target_monitor_index: int = None) -> bool:
        """Save screenshot from the monitor where Dota 2 is running to file"""
        if target_monitor_index is None:
            target_monitor_index = self.auto_detect_dota_monitor()
            if target_monitor_index is None:
                target_monitor_index = 1  # Default to primary monitor
        
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                self.logger.warning("No distinct monitors found by mss to capture from!")
                return False
            
            if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
                self.logger.warning(
                    f"Invalid monitor index {target_monitor_index} specified. "
                    f"Available: 1 to {len(monitors)-1}. Screenshot not taken."
                )
                return False
            
            monitor_to_capture = monitors[target_monitor_index]
            
            try:
                img = sct.grab(monitor_to_capture)
                # mss grabs in BGRA, convert to BGR for OpenCV compatibility
                img_np = np.array(img)
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(filename, img_bgr)
                self.logger.info(f"Screenshot of Monitor {target_monitor_index} saved to {filename}")
                return True
            except mss.exception.ScreenShotError as e:
                self.logger.error(
                    f"Error capturing screenshot from Monitor {target_monitor_index} using mss: {e}"
                )
                return False
            except Exception as e:
                self.logger.error(
                    f"An unexpected error occurred while capturing/saving screenshot "
                    f"from Monitor {target_monitor_index}: {e}"
                )
                return False

    def get_latest_screenshot(self):
        """Get the latest screenshot image and timestamp"""
        return self.latest_screenshot_img, self.latest_screenshot_time

    def auto_detect_dota_monitor(self) -> Optional[int]:
        """Auto-detect which monitor contains Dota 2 window, even if minimized (real-time detection)"""
        try:
            import pygetwindow as gw
            import psutil
            
            # First, prioritize visible and active Dota 2 windows (real-time detection)
            for window in gw.getAllWindows():
                title = window.title.lower()
                if (('dota 2' in title or 'dota2' in title or 'dota' in title) and 
                    len(window.title.strip()) > 0 and window.visible and not getattr(window, 'isMinimized', False)):
                    
                    # Get window position for active/visible windows
                    try:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        
                        # Check which monitor contains this window
                        with mss.mss() as sct:
                            monitors = sct.monitors[1:]  # Skip the combined monitor at index 0
                            for i, monitor in enumerate(monitors, start=1):
                                if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                    monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                    self.logger.info(f"Real-time detection: Active Dota 2 window '{window.title}' on Monitor {i}")
                                    return i
                    except Exception as e:
                        self.logger.warning(f"Error getting window position for '{window.title}': {e}")
                        continue
            
            # If no active/visible windows found, check for minimized ones
            dota_windows = []
            for window in gw.getAllWindows():
                title = window.title.lower()
                if (('dota 2' in title or 'dota2' in title or 'dota' in title) and 
                    len(window.title.strip()) > 0):
                    dota_windows.append(window)
                    self.logger.debug(f"Found Dota 2 window: '{window.title}' (Visible: {window.visible}, Minimized: {getattr(window, 'isMinimized', False)})")
            
            if dota_windows:
                # Use the first Dota 2 window found (even if minimized)
                dota_window = dota_windows[0]
                
                try:
                    # Get window position (even if minimized, some properties might be available)
                    window_center_x = dota_window.left + (dota_window.width // 2) if dota_window.width > 0 else None
                    window_center_y = dota_window.top + (dota_window.height // 2) if dota_window.height > 0 else None
                    
                    # If coordinates are valid, use them
                    if (window_center_x is not None and window_center_y is not None and
                        window_center_x > 0 and window_center_y > 0 and 
                        dota_window.width > 0 and dota_window.height > 0):
                        
                        # Check which monitor contains the window center
                        with mss.mss() as sct:
                            monitors = sct.monitors[1:]  # Skip the combined monitor at index 0
                            for i, monitor in enumerate(monitors, start=1):
                                if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                    monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                    self.logger.info(f"Auto-detected Dota 2 on Monitor {i} (from window coordinates)")
                                    return i
                    
                except Exception as e:
                    self.logger.warning(f"Error getting window position: {e}")
            
            # Fallback: try process-based detection
            return self._detect_by_process()
            
        except ImportError as e:
            self.logger.error(f"Required modules not available for auto-detection: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error during auto-detection: {e}")
            return None

    def _detect_by_process(self) -> Optional[int]:
        """Fallback detection using process information"""
        try:
            import psutil
            
            # Look for Dota 2 processes
            dota_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    proc_exe = proc.info['exe'].lower() if proc.info['exe'] else ''
                    
                    if ('dota2' in proc_name or 'dota 2' in proc_name or 
                        'dota2.exe' in proc_exe or 'dota' in proc_name):
                        dota_processes.append(proc)
                        self.logger.debug(f"Found Dota 2 process: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if dota_processes:
                # If we found processes but can't determine monitor, default to primary
                self.logger.info("Found Dota 2 process but couldn't determine monitor, defaulting to Monitor 1")
                return 1
            
            self.logger.warning("No Dota 2 processes found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error in process detection: {e}")
            return None

    def get_dota_process_monitor(self) -> Optional[int]:
        """Get monitor associated with Dota 2 process, prioritizing active windows"""
        return self.auto_detect_dota_monitor()
