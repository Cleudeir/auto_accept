import datetime
import mss
from PIL import Image
from typing import Optional, List, Tuple

class ScreenshotModel:
    """Model for handling screenshot capture functionality"""
    
    def __init__(self):
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
        except:
            pass
        return monitor_options
    
    def capture_monitor_screenshot(self, _unused=None) -> Optional[Image.Image]:
        """Capture screenshot from the monitor where Dota 2 is running"""
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
                target_monitor_index = 1
        
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                return False
            
            if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
                return False
            
            monitor_to_capture = monitors[target_monitor_index]
            
            try:
                img = sct.grab(monitor_to_capture)
                # Convert to PIL Image and save
                pil_img = Image.frombytes('RGB', img.size, img.rgb)
                pil_img.save(filename)
                return True
            except:
                return False

    def get_latest_screenshot(self):
        """Get the latest screenshot image and timestamp"""
        return self.latest_screenshot_img, self.latest_screenshot_time

    def auto_detect_dota_monitor(self) -> Optional[int]:
        """Auto-detect which monitor contains Dota 2 - simplified version"""
        try:
            import pygetwindow as gw
            
            # Simple window detection
            for window in gw.getAllWindows():
                title = window.title.lower()
                if (('dota 2' in title or 'dota2' in title or 'dota' in title) and 
                    len(window.title.strip()) > 0 and window.visible):
                    
                    try:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        
                        with mss.mss() as sct:
                            monitors = sct.monitors[1:]  # Skip the combined monitor at index 0
                            for i, monitor in enumerate(monitors, start=1):
                                if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                    monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                    return i
                    except:
                        continue
            
            # Default to primary monitor
            return 1
            
        except:
            return 1

    def get_dota_process_monitor(self) -> Optional[int]:
        """Get monitor associated with Dota 2 process"""
        return self.auto_detect_dota_monitor()
