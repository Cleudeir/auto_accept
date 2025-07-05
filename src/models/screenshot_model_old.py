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
        print("📸 Starting screenshot capture...")
        monitor_index = self.auto_detect_dota_monitor()
        if monitor_index is None:
            print("⚠️  Auto-detection failed, using Monitor 1")
            monitor_index = 1
        
        print(f"📺 Using Monitor {monitor_index} for screenshot")
        
        with mss.mss() as sct:
            monitors = sct.monitors
            if not monitors or len(monitors) <= 1:
                print("❌ No distinct monitors found!")
                return None
            if not isinstance(monitor_index, int) or not (0 < monitor_index < len(monitors)):
                print(f"❌ Invalid monitor index: {monitor_index}")
                return None
            
            monitor = monitors[monitor_index]
            print(f"📐 Capturing from Monitor {monitor_index}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
            try:
                sct_img = sct.grab(monitor)
                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                self.latest_screenshot_time = datetime.datetime.now()
                self.latest_screenshot_img = img.copy()
                print(f"✅ Screenshot captured successfully from Monitor {monitor_index}")
                return img
            except Exception as e:
                print(f"❌ Error capturing screenshot: {e}")
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
        """Auto-detect which monitor contains Dota 2 - improved with debug output"""
        try:
            import pygetwindow as gw
            
            print("🔍 Starting Dota 2 monitor detection...")
            
            # Get all available monitors first
            with mss.mss() as sct:
                monitors = sct.monitors[1:]  # Skip the combined monitor at index 0
                print(f"📺 Available monitors: {len(monitors)}")
                for i, monitor in enumerate(monitors, start=1):
                    print(f"   Monitor {i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
            
            # Get all windows and filter for Dota 2
            all_windows = gw.getAllWindows()
            print(f"🪟 Total windows found: {len(all_windows)}")
            
            dota_windows = []
            for window in all_windows:
                title = window.title.lower()
                if ('dota 2' in title or 'dota2' in title or 'dota' in title) and len(window.title.strip()) > 0:
                    dota_windows.append(window)
                    print(f"🎮 Found Dota window: '{window.title}' - Visible: {window.visible}, Size: {window.width}x{window.height}")
            
            if not dota_windows:
                print("❌ No Dota 2 windows found")
                print("🔧 Defaulting to Monitor 1")
                return 1
            
            # Check visible windows first
            for window in dota_windows:
                if window.visible and not getattr(window, 'isMinimized', False):
                    try:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        print(f"🎯 Checking visible window '{window.title}' at center ({window_center_x}, {window_center_y})")
                        
                        # Check which monitor contains this window
                        for i, monitor in enumerate(monitors, start=1):
                            if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                print(f"✅ Dota 2 detected on Monitor {i}")
                                print(f"📋 Window: '{window.title}'")
                                print(f"📐 Position: ({window.left}, {window.top}) Size: {window.width}x{window.height}")
                                print(f"📺 Monitor: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
                                return i
                    except Exception as e:
                        print(f"❌ Error checking window '{window.title}': {e}")
                        continue
            
            # If no visible windows found, check minimized ones
            print("🔍 No visible Dota windows found, checking minimized windows...")
            for window in dota_windows:
                try:
                    # Even minimized windows might have valid coordinates
                    if window.width > 0 and window.height > 0:
                        window_center_x = window.left + (window.width // 2)
                        window_center_y = window.top + (window.height // 2)
                        print(f"🎯 Checking minimized window '{window.title}' at center ({window_center_x}, {window_center_y})")
                        
                        for i, monitor in enumerate(monitors, start=1):
                            if (monitor['left'] <= window_center_x <= monitor['left'] + monitor['width'] and
                                monitor['top'] <= window_center_y <= monitor['top'] + monitor['height']):
                                print(f"✅ Dota 2 detected on Monitor {i} (minimized)")
                                print(f"📋 Window: '{window.title}'")
                                print(f"📐 Position: ({window.left}, {window.top}) Size: {window.width}x{window.height}")
                                print(f"📺 Monitor: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
                                return i
                except Exception as e:
                    print(f"❌ Error checking minimized window '{window.title}': {e}")
                    continue
            
            # Default to primary monitor
            print("🔧 No valid Dota 2 window position found, defaulting to Monitor 1")
            return 1
            
        except Exception as e:
            print(f"❌ Error during Dota 2 detection: {e}")
            print("🔧 Defaulting to Monitor 1")
            return 1

    def get_dota_process_monitor(self) -> Optional[int]:
        """Get monitor associated with Dota 2 process"""
        return self.auto_detect_dota_monitor()
