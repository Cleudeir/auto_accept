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
    
    def capture_monitor_screenshot(self, target_monitor_index: int) -> Optional[Image.Image]:
        """Capture screenshot from specified monitor and return PIL Image"""
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                self.logger.warning("No distinct monitors found by mss to capture from!")
                return None
            
            if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
                self.logger.warning(
                    f"Invalid monitor index {target_monitor_index} specified. "
                    f"Available: 1 to {len(monitors)-1}. Screenshot not taken."
                )
                return None
            
            monitor = monitors[target_monitor_index]
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                self.latest_screenshot_time = datetime.datetime.now()
                self.latest_screenshot_img = img.copy()
                return img
            except Exception as e:
                self.logger.error(
                    f"An unexpected error occurred while capturing screenshot from "
                    f"Monitor {target_monitor_index}: {e}"
                )
                return None
    
    def save_monitor_screenshot(self, filename: str, target_monitor_index: int) -> bool:
        """Save screenshot from specified monitor to file"""
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
    
    def get_latest_screenshot(self) -> Tuple[Optional[Image.Image], Optional[datetime.datetime]]:
        """Get the latest screenshot and its timestamp"""
        return self.latest_screenshot_img, self.latest_screenshot_time
    
    def cleanup_old_screenshots(self, folder: str, keep_count: int):
        """Keep only the last N screenshot files in a folder"""
        try:
            files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png")]
            files.sort(key=os.path.getmtime, reverse=True)
            for f in files[keep_count:]:
                os.remove(f)
                self.logger.info(f"Removed old screenshot: {f}")
        except Exception as e:
            self.logger.error(f"Error cleaning up old screenshots: {e}")
