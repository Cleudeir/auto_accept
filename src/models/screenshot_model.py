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
    
    def capture_monitor_screenshot(self, _unused=None, show_debug=False) -> Optional[Image.Image]:
        """Capture screenshot from the monitor where Dota 2 is running"""
        if show_debug:
            print("📸 Starting screenshot capture...")
        monitor_index = self.auto_detect_dota_monitor(show_debug=show_debug)
        if monitor_index is None:
            if show_debug:
                print("⚠️  Auto-detection failed, using Monitor 1")
            monitor_index = 1
        
        if show_debug:
            print(f"📺 Using Monitor {monitor_index} for screenshot")
        
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                if show_debug:
                    print("❌ No distinct monitors found!")
                return None
            if not isinstance(monitor_index, int) or not (0 < monitor_index < len(monitors)):
                if show_debug:
                    print(f"❌ Invalid monitor index: {monitor_index}")
                return None
            
            monitor = monitors[monitor_index]
            if show_debug:
                print(f"📐 Capturing from Monitor {monitor_index}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                self.latest_screenshot_time = datetime.datetime.now()
                self.latest_screenshot_img = img.copy()
                if show_debug:
                    print(f"✅ Screenshot captured successfully from Monitor {monitor_index}")
                return img
            except Exception as e:
                if show_debug:
                    print(f"❌ Error capturing screenshot: {e}")
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

    def auto_detect_dota_monitor(self, show_debug=False) -> Optional[int]:
        """Auto-detect which monitor contains Dota 2 - improved with debug output"""
        try:
            import pygetwindow as gw
            
            if show_debug:
                print("🔍 Starting Dota 2 monitor detection...")
            
            # Get all available monitors first
            with mss.mss() as sct:
                monitors = sct.monitors[1:]  # Skip the combined monitor at index 0
                if show_debug:
                    print(f"📺 Available monitors: {len(monitors)}")
                    for i, monitor in enumerate(monitors, start=1):
                        print(f"   Monitor {i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
            # Get all windows and filter for Dota 2
            all_windows = gw.getAllWindows()
            if show_debug:
                print(f"🪟 Total windows found: {len(all_windows)}")
            
            dota_windows = []
            for window in all_windows:
                title = window.title.lower()
                if ('dota 2' in title or 'dota2' in title or 'dota' in title) and len(window.title.strip()) > 0:
                    dota_windows.append(window)
                    if show_debug:
                        print(f"🎮 Found Dota window: '{window.title}' - Visible: {window.visible}, Size: {window.width}x{window.height}")
            
            if not dota_windows:
                if show_debug:
                    print("❌ No Dota 2 windows found")
                    print("🔧 Defaulting to Monitor 1")
                return 1
            
            # Check visible windows first
            for window in dota_windows:
                if window.visible and not getattr(window, 'isMinimized', False):
                    try:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        if show_debug:
                            print(f"🎯 Checking visible window '{window.title}' at center ({window_center_x}, {window_center_y})")
                        
                        # Check which monitor contains this window
                        for i, monitor in enumerate(monitors, start=1):
                            if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                if show_debug:
                                    print(f"✅ Dota 2 detected on Monitor {i}")
                                    print(f"📋 Window: '{window.title}'")
                                    print(f"📐 Position: ({window.left}, {window.top}) Size: {window.width}x{window.height}")
                                    print(f"📺 Monitor: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
                                return i
                    except Exception as e:
                        if show_debug:
                            print(f"❌ Error checking window '{window.title}': {e}")
                        continue
            
            # If no visible windows found, check minimized ones
            if show_debug:
                print("🔍 No visible Dota windows found, checking minimized windows...")
            for window in dota_windows:
                try:
                    # Even minimized windows might have valid coordinates
                    if window.width > 0 and window.height > 0:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        if show_debug:
                            print(f"🎯 Checking minimized window '{window.title}' at center ({window_center_x}, {window_center_y})")
                        
                        for i, monitor in enumerate(monitors, start=1):
                            if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                if show_debug:
                                    print(f"✅ Dota 2 detected on Monitor {i} (minimized)")
                                    print(f"📋 Window: '{window.title}'")
                                    print(f"📐 Position: ({window.left}, {window.top}) Size: {window.width}x{window.height}")
                                    print(f"📺 Monitor: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
                                return i
                except Exception as e:
                    if show_debug:
                        print(f"❌ Error checking minimized window '{window.title}': {e}")
                    continue
            
            # Default to primary monitor
            if show_debug:
                print("🔧 No valid Dota 2 window position found, defaulting to Monitor 1")
            return 1
            
        except Exception as e:
            if show_debug:
                print(f"❌ Error during Dota 2 detection: {e}")
                print("🔧 Defaulting to Monitor 1")
            return 1

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
