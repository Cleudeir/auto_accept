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
from utils import get_resource_path

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

    def __init__(
        self, screenshot_model=None, score_threshold: float = 0.7, config_model=None
    ):
        self.reference_images = self._load_reference_images()
        self.screenshot_model = screenshot_model
        self.ocr_cache = {}
        self.config_model = config_model
        # Use threshold from config if available, otherwise use the passed parameter
        if config_model and hasattr(config_model, "detection_threshold"):
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

    # Types that represent the match-accept dialog (center of screen)
    _CENTER_CROP_TYPES = {"dota", "dota2_plus"}
    # Percentage of image to keep from center (width%, height%)
    _CENTER_CROP_W = 0.42
    _CENTER_CROP_H = 0.45

    def _crop_center(self, img: Image.Image, w_pct: float = None, h_pct: float = None) -> Image.Image:
        """Crop and return only the center region of an image.

        The match-accept dialog (YOUR GAME IS READY / ACEITAR) is always
        centred on screen.  Comparing only this region avoids false positives
        from friend-request popups or lobby invites that appear at the edges.
        """
        if w_pct is None:
            w_pct = self._CENTER_CROP_W
        if h_pct is None:
            h_pct = self._CENTER_CROP_H

        w, h = img.size
        new_w = int(w * w_pct)
        new_h = int(h * h_pct)
        left = (w - new_w) // 2
        top = (h - new_h) // 2
        return img.crop((left, top, left + new_w, top + new_h))

    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        base_path = get_resource_path("bin")
        references = {
            "dota": os.path.join(base_path, "dota.png"),
            "dota2_plus": os.path.join(base_path, "dota_plus.png"),
            "read_check": os.path.join(base_path, "read_check.jpg"),
            "ad": os.path.join(base_path, "AD.png"),
            "10min": os.path.join(base_path, "10min.png"),
            "long_wait": os.path.join(base_path, "long_wait.png"),
        }
        for name, path in references.items():
            if not os.path.exists(path):
                pass
        return references

    def compare_images_file(self, img1_path: str, img2_path: str) -> float:
        """Compare two image files and return similarity score"""
        try:
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)

            if img1 is None or img2 is None:
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
            return 0.0

    def compare_image_with_reference(self, img: Image.Image, ref_path: str, center_crop: bool = False) -> float:
        try:
            # When center_crop is True, compare only the central region of
            # both images.  This is used for match-accept detection to avoid
            # confusing it with friend requests or other edge popups.
            if center_crop:
                img = self._crop_center(img)

            # Load reference image using PIL to avoid OpenCV color space issues
            ref_pil = Image.open(ref_path)
            if center_crop:
                ref_pil = self._crop_center(ref_pil)

            # Ensure both images have the same size - resize reference to match input image
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
                return 0.0

            # Compute SSIM on raw color images without any color space conversion
            score, _ = ssim(img_np, ref_np, full=True, channel_axis=2)

            return score
        except Exception as e:
            return 0.0

    def detect_match_in_image(self, img: Image.Image) -> str:
        """
        Detect reference patterns in the given image
        Returns the name of the reference image with the highest score
        """
        scores = {}
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                use_center = name in self._CENTER_CROP_TYPES
                score = self.compare_image_with_reference(img, ref_path, center_crop=use_center)
                scores[name] = score
            else:
                scores[name] = 0.0
        if scores:
            highest_score_name = max(scores, key=scores.get)
            highest_score = scores[highest_score_name]
            if highest_score >= self.score_threshold:
                return highest_score_name
        return "none"

    def detect_match_in_image_with_score(self, img: Image.Image) -> Tuple[str, float]:
        """
        Detect reference patterns in the given image.
        Returns (name, score) of the reference image with the highest score.

        For match-accept types (dota, dota2_plus) only the centre region of
        the screenshot is compared, so that friend-request popups or lobby
        invites at the edges do not cause false positives.
        """
        scores = {}
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                use_center = name in self._CENTER_CROP_TYPES
                score = self.compare_image_with_reference(img, ref_path, center_crop=use_center)
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
            pass

    def process_detection_result(self, highest_match: str) -> str:
        """Process detection results and return action taken"""
        action = "none"

        # Check if auto-focus is enabled
        should_focus = (
            self.config_model.auto_focus_on_detection if self.config_model else True
        )
        # When enabled: briefly focus Dota 2 to perform the action (via standard
        # pyautogui input), then give focus back to the app the user was using.
        # No PostMessage / message injection is used.
        brief_focus = (
            self.config_model.brief_focus_then_restore if self.config_model else True
        )
        prev_focus_hwnd = None

        if should_focus:
            if brief_focus:
                # Remember the app the user was using so focus can be restored
                prev_focus_hwnd = self.window_model.get_foreground_window()
            focus_success = self.focus_dota2_window_enhanced()

        if highest_match == "read_check":
            pyautogui.press("enter")
            action = "read_check_detected"
        elif highest_match in ["dota", "dota2_plus"]:
            pyautogui.press("enter")
            action = "match_detected"
        elif highest_match == "ad":
            action = "ad_detected"
        elif highest_match == "10min":
            screen_w, screen_h = pyautogui.size()
            ok_x = int(screen_w * 0.5)
            ok_y = int(screen_h * 0.555)
            pyautogui.click(ok_x, ok_y)
            action = "10min_ok_clicked"
        elif highest_match == "long_wait":
            screen_w, screen_h = pyautogui.size()
            ok_x = int(screen_w * 0.5)
            ok_y = int(screen_h * 0.555)
            pyautogui.click(ok_x, ok_y)
            action = "long_wait_ok_clicked"

        # Give focus back to the app the user was using
        if brief_focus and prev_focus_hwnd:
            restored = self.window_model.restore_focus_to_window(prev_focus_hwnd)

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
        except Exception as e:
            pass

    def get_dota2_window_debug_info(self) -> dict:
        """Get debugging information about Dota 2 windows"""
        return {
            "processes": self.window_model.get_dota2_processes(),
            "windows": self.window_model.get_dota2_windows(),
            "all_related": self.window_model.list_all_dota2_related_windows(),
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
                if (
                    monitor.left <= window_center_x < monitor.left + monitor.width
                    and monitor.top <= window_center_y < monitor.top + monitor.height
                ):
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
            for process in psutil.process_iter(["pid", "name"]):
                if "dota2" in process.info["name"].lower():
                    return True
            return False
        except Exception as e:
            return False

    def capture_monitor_screenshot(
        self, monitor_number: Optional[int] = None
    ) -> Optional[Image.Image]:
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
            screenshot = pyautogui.screenshot(
                region=(monitor.left, monitor.top, monitor.width, monitor.height)
            )

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
            "is_running": self.is_dota2_running(),
            "monitor_number": self.find_dota2_monitor(),
            "available_monitors": len(pyautogui.getAllMonitors()),
            "monitors": [],
            "window_info": None,
        }

        # Add monitor details
        for i, monitor in enumerate(pyautogui.getAllMonitors()):
            info["monitors"].append(
                {
                    "number": i,
                    "left": monitor.left,
                    "top": monitor.top,
                    "width": monitor.width,
                    "height": monitor.height,
                    "is_dota2_monitor": i == info["monitor_number"],
                }
            )

        # Add window info if Dota 2 is found
        try:
            dota_windows = gw.getWindowsWithTitle("Dota 2")
            if dota_windows:
                window = dota_windows[0]
                info["window_info"] = {
                    "title": window.title,
                    "left": window.left,
                    "top": window.top,
                    "width": window.width,
                    "height": window.height,
                    "is_minimized": window.isMinimized,
                    "is_maximized": window.isMaximized,
                }
        except:
            pass

        return info

    def print_dota2_monitor_status(self):
        """
        Print detailed status about Dota 2 monitoring
        """
        pass
