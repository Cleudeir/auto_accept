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
        
        # Clean up old screenshots on startup
        self.cleanup_old_screenshots()
    
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
        except:
            pass
        return monitor_options
    
    def capture_monitor_screenshot(self, _unused=None) -> Optional[Image.Image]:
        """Capture screenshot from the monitor where Dota 2 is running (auto-detect, even if minimized)"""
        monitor_index = self.auto_detect_dota_monitor()
        if monitor_index is None:
            monitor_index = 1
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                return None
            if not isinstance(monitor_index, int) or not (0 < monitor_index < len(monitors)):
                return None
            monitor = monitors[monitor_index]
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                self.latest_screenshot_time = datetime.datetime.now()
                self.latest_screenshot_img = img.copy()
                return img
            except:
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
                return False
            
            if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
                return False
            
            monitor_to_capture = monitors[target_monitor_index]
            
            try:
                img = sct.grab(monitor_to_capture)
                # mss grabs in BGRA, convert to BGR for OpenCV compatibility
                img_np = np.array(img)
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
                cv2.imwrite(filename, img_bgr)
                return True
            except:
                return False

    def get_latest_screenshot(self):
        """Get the latest screenshot image and timestamp"""
        return self.latest_screenshot_img, self.latest_screenshot_time

    def auto_detect_dota_monitor(self) -> Optional[int]:
        """Auto-detect which monitor contains Dota 2 window - minimal detection"""
        try:
            import pygetwindow as gw
            
            # Quick detection: only check visible and active Dota 2 windows
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
                                    return i
                    except:
                        continue
            
            # If no active Dota 2 window found, default to primary monitor
            return 1
            
        except:
            return 1  # Default to primary monitor

    def get_dota_process_monitor(self) -> Optional[int]:
        """Get monitor associated with Dota 2 process, prioritizing active windows"""
        return self.auto_detect_dota_monitor()

    def cleanup_old_screenshots(self, max_age_hours: int = 24):
        """Delete old screenshot files to free up space"""
        try:
            screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'screenshots')
            if not os.path.exists(screenshots_dir):
                return
            
            current_time = datetime.datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(screenshots_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(screenshots_dir, filename)
                    try:
                        # Get file modification time
                        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        age_hours = (current_time - file_time).total_seconds() / 3600
                        
                        if age_hours > max_age_hours:
                            os.remove(file_path)
                            deleted_count += 1
                    except:
                        pass
            
        except:
            pass
