import os
import logging
import cv2
import numpy as np
import pyautogui
import platform
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from typing import Tuple, Optional, Dict, List
from models.window_model import WindowModel
import psutil

# Windows-specific imports with platform check
if platform.system() == "Windows":
    try:
        import pygetwindow as gw
        import win32gui
        import win32process
    except Exception:
        gw = None
        win32gui = None
        win32process = None
else:
    # Stubs for non-Windows platforms
    gw = None
    win32gui = None
    win32process = None


class DetectionModel:
    """Model for handling image detection and comparison logic"""

    def __init__(self, screenshot_model=None, score_threshold: float = 0.7, config_model=None):
        self.reference_images = self._load_reference_images()
        self.screenshot_model = screenshot_model
        self.ocr_cache = {}
        self.config_model = config_model
        # Use threshold from config if available, otherwise use the passed parameter
        if config_model and hasattr(config_model, 'detection_threshold'):
            self.score_threshold = config_model.detection_threshold
        else:
            self.score_threshold = score_threshold
        self.window_model = WindowModel(config_model)  # Enhanced window management
        self.dota2_monitor = None  # Track which monitor Dota 2 is on
        self.monitor_screenshots = {}  # Cache for monitor screenshots

    def set_score_threshold(self, threshold: float):
        """Set the threshold for highest_score detection"""
        self.score_threshold = threshold
        # Also update the config model if available
        if self.config_model:
            self.config_model.detection_threshold = threshold

    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"
        )
        references = {
            "dota": os.path.join(base_path, "dota.png"),
            "dota2_plus": os.path.join(base_path, "dota2_plus.jpeg"),
            "read_check": os.path.join(base_path, "read_check.jpg"),
            "ad": os.path.join(base_path, "AD.png"),
        }
        for name, path in references.items():
            if not os.path.exists(path):
                print(f"⚠️ Reference image not found: {path}")
        return references

    def compare_images_file(self, img1_path: str, img2_path: str) -> float:
        """Compare two image files and return similarity score"""
        try:
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)

            if img1 is None or img2 is None:
                print(f"❌ Failed to load images: {img1_path}, {img2_path}")
                return 0.0

            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            if img1_gray.shape != img2_gray.shape:
                img2_gray = cv2.resize(
                    img2_gray, (img1_gray.shape[1], img1_gray.shape[0])
                )

            score, _ = ssim(img1_gray, img2_gray, full=True)
            return score
        except Exception as e:
            print(f"❌ Error comparing images: {e}")
            return 0.0

    def compare_image_with_reference(self, img: Image.Image, ref_path: str) -> float:
        try:
            # Load reference image using PIL to avoid OpenCV color space issues
            ref_pil = Image.open(
                ref_path
            )  # Ensure both images have the same size - resize reference to match input image
            if ref_pil.size != img.size:
                ref_pil = ref_pil.resize(img.size, Image.Resampling.LANCZOS)

            # Equalize image channels - convert both to RGB to ensure same number of channels
            if img.mode != "RGB":
                img = img.convert("RGB")
            if ref_pil.mode != "RGB":
                ref_pil = ref_pil.convert("RGB")

            # Convert PIL Images to numpy arrays (raw data)
            img_np = np.array(img)
            ref_np = np.array(ref_pil)

            # Verify both arrays have the same shape (should be guaranteed now)
            if img_np.shape != ref_np.shape:
                print(f"⚠️ Image shapes don't match after equalization: {img_np.shape} vs {ref_np.shape}")
                return 0.0

            # Compute SSIM on raw color images without any color space conversion
            score, _ = ssim(img_np, ref_np, full=True, channel_axis=2)

            return score
        except Exception as e:
            print(f"❌ Error comparing image with reference: {e}")
            return 0.0

    def detect_match_in_image(self, img: Image.Image) -> str:
        """
        Detect reference patterns in the given image
        Returns the name of the reference image with the highest score
        """
        scores = {}
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                score = self.compare_image_with_reference(img, ref_path)
                scores[name] = score
            else:
                scores[name] = 0.0
        if scores:
            highest_score_name = max(scores, key=scores.get)
            highest_score = scores[highest_score_name]
            if highest_score >= self.score_threshold:
                return highest_score_name
        return "none"

    def detect_match_in_image_with_score(
        self, img: Image.Image
    ) -> Tuple[str, float]:
        """
        Detect reference patterns in the given image
        Returns (name, score) of the reference image with the highest score
        """
        scores = {}
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                score = self.compare_image_with_reference(img, ref_path)
                scores[name] = score
            else:
                scores[name] = 0.0
        if scores:
            highest_score_name = max(scores, key=scores.get)
            highest_score = scores[highest_score_name]
            if highest_score >= self.score_threshold:             
                return highest_score_name, highest_score
            else:
                return "none", highest_score
        return "none", 0.0

    def send_enter_key(self):
        """Send Enter key press"""
        try:
            pyautogui.press("enter")
        except Exception as e:
            print(f"❌ Error pressing Enter key: {e}")

    def process_detection_result(self, highest_match: str) -> str:
        """Process detection results and return action taken using enhanced window focusing"""
        action = "none"
        print(f"🔍 Processing detection result: {highest_match}")
        
        # Check if auto-focus is enabled
        should_focus = (self.config_model.auto_focus_on_detection 
                       if self.config_model else True)
        
        if should_focus:
            # Always try to focus Dota 2 window when any detection occurs
            print("🎯 Attempting to focus Dota 2 window...")
            focus_success = self.focus_dota2_window_enhanced()
            if focus_success:
                print("✅ Successfully focused Dota 2 window")
            else:
                print("❌ Failed to focus Dota 2 window, but continuing with action")
        
        if highest_match == "read_check":
            print("📖 Read-check pattern detected - confirming with Enter")
            pyautogui.press("enter")           
            action = "read_check_detected"
        elif highest_match in ["dota", "dota2_plus"]:
            print(f"🎉 Match detected ({highest_match}) - accepting with Enter")
            pyautogui.press("enter")          
            action = "match_detected"
        elif highest_match == "ad":
            print("📺 Advertisement detected - window focused")
            action = "ad_detected"
        
        print(f"✅ Action completed: {action}")
        return action

    def focus_dota2_window_enhanced(self) -> bool:
        """Enhanced Dota 2 window focusing with multiple strategies"""
        return self.window_model.focus_dota2_window_enhanced()

    def focus_dota2_window(self):
        """Legacy method - now uses enhanced focusing as fallback"""
        try:
            # Try enhanced method first
            if self.focus_dota2_window_enhanced():
                return
            
            # Fallback to original simple method
            dota_window = gw.getWindowsWithTitle("Dota 2")[0]
            if dota_window.isMinimized:
                dota_window.restore()
            dota_window.activate()
            print("✅ Focused Dota 2 window (legacy method)")
        except Exception as e:
            print(f"❌ Could not focus Dota 2 window: {e}")

    def get_dota2_window_debug_info(self) -> dict:
        """Get debugging information about Dota 2 windows"""
        return {
            'processes': self.window_model.get_dota2_processes(),
            'windows': self.window_model.get_dota2_windows(),
            'all_related': self.window_model.list_all_dota2_related_windows()
        }

    def find_dota2_monitor(self) -> Optional[int]:
        """
        Find which monitor Dota 2 is running on
        Returns monitor number (0-based) or None if not found
        """
        try:
            # Get all monitors
            monitors = pyautogui.getAllMonitors()
            
            # Try to find Dota 2 window
            dota_windows = gw.getWindowsWithTitle("Dota 2")
            if not dota_windows:
                return None
            
            dota_window = dota_windows[0]
            
            # Determine which monitor contains the Dota 2 window
            window_center_x = dota_window.left + dota_window.width // 2
            window_center_y = dota_window.top + dota_window.height // 2
            
            for i, monitor in enumerate(monitors):
                if (monitor.left <= window_center_x < monitor.left + monitor.width and
                    monitor.top <= window_center_y < monitor.top + monitor.height):
                    self.dota2_monitor = i
                    return i
            
            self.dota2_monitor = 0
            return 0
            
        except Exception as e:
            return None

    def is_dota2_running(self) -> bool:
        """
        Check if Dota 2 process is running
        Returns True if Dota 2 is running, False otherwise
        """
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if 'dota2' in process.info['name'].lower():
                    return True
            return False
        except Exception as e:
            return False

    def capture_monitor_screenshot(self, monitor_number: Optional[int] = None) -> Optional[Image.Image]:
        """
        Capture screenshot from specific monitor
        If monitor_number is None, uses the monitor where Dota 2 is running
        """
        try:
            if monitor_number is None:
                monitor_number = self.find_dota2_monitor()
                if monitor_number is None:
                    return None
            
            monitors = pyautogui.getAllMonitors()
            if monitor_number >= len(monitors):
                return None
            
            monitor = monitors[monitor_number]
            
            # Capture screenshot from specific monitor
            screenshot = pyautogui.screenshot(region=(monitor.left, monitor.top, monitor.width, monitor.height))
            
            # Cache the screenshot
            self.monitor_screenshots[monitor_number] = screenshot
            
            return screenshot
            
        except Exception as e:
            return None

    def get_dota2_monitor_info(self) -> Dict:
        """
        Get comprehensive information about Dota 2 monitoring
        """
        info = {
            'is_running': self.is_dota2_running(),
            'monitor_number': self.find_dota2_monitor(),
            'available_monitors': len(pyautogui.getAllMonitors()),
            'monitors': [],
            'window_info': None
        }
        
        # Add monitor details
        for i, monitor in enumerate(pyautogui.getAllMonitors()):
            info['monitors'].append({
                'number': i,
                'left': monitor.left,
                'top': monitor.top,
                'width': monitor.width,
                'height': monitor.height,
                'is_dota2_monitor': i == info['monitor_number']
            })
        
        # Add window info if Dota 2 is found
        try:
            dota_windows = gw.getWindowsWithTitle("Dota 2")
            if dota_windows:
                window = dota_windows[0]
                info['window_info'] = {
                    'title': window.title,
                    'left': window.left,
                    'top': window.top,
                    'width': window.width,
                    'height': window.height,
                    'is_minimized': window.isMinimized,
                    'is_maximized': window.isMaximized
                }
        except:
            pass
        
        return info

    def print_dota2_monitor_status(self):
        """
        Print detailed status about Dota 2 monitoring
        """
        print("\n" + "="*50)
        print("🔍 DOTA 2 MONITOR STATUS")
        print("="*50)
        
        info = self.get_dota2_monitor_info()
        
        print(f"🎮 Dota 2 Running: {'✅ YES' if info['is_running'] else '❌ NO'}")
        print(f"🖥️ Available Monitors: {info['available_monitors']}")
        
        if info['monitor_number'] is not None:
            print(f"📍 Dota 2 Monitor: Monitor {info['monitor_number']}")
        else:
            print("📍 Dota 2 Monitor: ❌ Not detected")
        
        print("\n📊 Monitor Details:")
        for monitor in info['monitors']:
            status = "🎮 (Dota 2)" if monitor['is_dota2_monitor'] else ""
            print(f"   Monitor {monitor['number']}: {monitor['width']}x{monitor['height']} "
                  f"at ({monitor['left']}, {monitor['top']}) {status}")
        
        if info['window_info']:
            print(f"\n🪟 Window Info:")
            print(f"   Title: {info['window_info']['title']}")
            print(f"   Position: ({info['window_info']['left']}, {info['window_info']['top']})")
            print(f"   Size: {info['window_info']['width']}x{info['window_info']['height']}")
            print(f"   Minimized: {info['window_info']['is_minimized']}")
            print(f"   Maximized: {info['window_info']['is_maximized']}")
        
        print("="*50 + "\n")

