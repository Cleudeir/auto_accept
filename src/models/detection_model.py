import os
import logging
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from typing import Tuple, Optional

class DetectionModel:
    """Model for handling image detection and comparison logic"""
    
    def __init__(self, screenshot_model=None):
        self.logger = logging.getLogger("Dota2AutoAccept.DetectionModel")
        self.reference_images = self._load_reference_images()
        self.screenshot_model = screenshot_model  # Optional, for monitor-aware screenshots
        self.ocr_cache = {}  # Cache OCR results per monitor
    
    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        references = {
            "dota": os.path.join("bin", "dota.png"),
            "print": os.path.join("bin", "print.png"),
            "read_check": os.path.join("bin", "read_check.jpg"),
            "long_time": os.path.join("bin", "long_time.png"),
            "ad": os.path.join("bin", "AD.png")
        }
        # Only log reference images, no button images
        for name, path in references.items():
            if not os.path.exists(path):
                self.logger.warning(f"Reference image not found: {path}")
        return references
    
    def compare_images_file(self, img1_path: str, img2_path: str) -> float:
        """Compare two image files and return similarity score"""
        try:
            img1 = cv2.imread(img1_path)
            img2 = cv2.imread(img2_path)
            
            if img1 is None or img2 is None:
                self.logger.error(f"Failed to load images: {img1_path}, {img2_path}")
                return 0.0
            
            img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Resize to the same size
            if img1_gray.shape != img2_gray.shape:
                img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
            
            score, _ = ssim(img1_gray, img2_gray, full=True)
            return score
        except Exception as e:
            self.logger.error(f"Error comparing images: {e}")
            return 0.0
    
    def compare_image_with_reference(self, img: Image.Image, ref_path: str) -> float:
        """Compare a PIL Image with a reference image file"""
        try:
            # Convert PIL Image to numpy array for OpenCV
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Load reference image
            ref_img = cv2.imread(ref_path)
            
            if ref_img is None:
                self.logger.error(f"Failed to load reference image: {ref_path}")
                return 0.0
            
            # Resize reference to match captured image
            ref_img = cv2.resize(ref_img, (img_bgr.shape[1], img_bgr.shape[0]))
            
            # Convert both to grayscale for comparison
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
            
            # Compute SSIM between the two images
            score, _ = ssim(img_gray, ref_gray, full=True)
            return score
        except Exception as e:
            self.logger.error(f"Error comparing image with reference: {e}")
            return 0.0
    
    def detect_match_in_image(self, img: Image.Image) -> Tuple[bool, dict]:
        """
        Detect if any reference patterns match in the given image
        Returns (match_found, similarity_scores)
        """
        scores = {}
        match_found = False
        ad_stop = False
        # Compare with each reference image
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                score = self.compare_image_with_reference(img, ref_path)
                scores[name] = score
                # Check for matches based on thresholds
                if name == "ad" and score >= 0.6:
                    print(f"AD.png detected with similarity (score={score:.2f})")
                    ad_stop = True
                if name in ["dota", "print"] and score > 0.8:
                    print(f"{name.capitalize()} pattern detected with score {score:.2f}")   
                    match_found = True
                elif name == "read_check" and score > 0.8:
                    print(f"Read-check pattern detected with score {score:.2f}")
                    # Special case for read-check (different action)
                    match_found = True
                elif name == "long_time" and score > 0.8:
                    print(f"Long matchmaking wait dialog detected with score {score:.2f}")
                    # Special case for long matchmaking wait dialog
                    match_found = True
            else:                scores[name] = 0.0
        # Return ad_stop flag in scores for controller to act on
        scores["ad_stop"] = ad_stop
        return match_found, scores
    
    def focus_dota2_window(self):
        """Focus the Dota 2 window if it exists"""
        try:
            dota_windows = gw.getWindowsWithTitle("Dota 2")
            if dota_windows:
                dota_window = dota_windows[0]
                if dota_window.isMinimized:
                    dota_window.restore()
                dota_window.activate()
                self.logger.info("Successfully focused Dota 2 window")
                return True
            else:
                self.logger.warning("Could not find Dota 2 window to focus")
                return False
        except Exception as e:
            self.logger.error(f"Error focusing Dota 2 window: {e}")
            return False


    def send_enter_key(self):
        """Send Enter key press"""
        try:
            pyautogui.press("enter")
            self.logger.info("Enter key pressed")
        except Exception as e:
            self.logger.error(f"Error pressing Enter key: {e}")
    
    def process_detection_result(self, scores: dict) -> str:
        """Process detection results and return action taken using only OCR and Enter key"""
        action = "none"
        # Check for long matchmaking wait dialog first
        if scores.get("long_time", 0) > 0.8:
            print(f"Long matchmaking wait dialog detected with score {scores['long_time']:.2f}")
            print(f"Pressing ESC key")
            pyautogui.press("esc")
           
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "long_time_dialog_detected"
        # Check for read-check pattern (different action)
        elif scores.get("read_check", 0) > 0.9:
            print(f"Preessing Enter key")
            pyautogui.press("enter")
            print(f"Read-check pattern detected with score {scores['read_check']:.2f}")
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "read_check_detected"
        # Check for main match patterns
        elif scores.get("dota", 0) > 0.9 or scores.get("print", 0) > 0.9:
            print(f"Match detected with scores: Dota={scores.get('dota', 0):.2f}, Print={scores.get('print', 0):.2f}")
            self.focus_dota2_window()
            print(f"Preessing Enter key")
            pyautogui.press("enter")
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "match_detected"
        return action

    def send_enter_key_if_text_found(self, search_strings):
        
       
        print(f"Searching for text: {search_strings}")
        result = self.find_string_in_image(search_strings)
        if result:
            self.logger.info(f"Text '{result[0]}' found, pressed Enter.")
        else:
            self.logger.info(f"No relevant text found, pressed Enter as fallback.")

    def find_string_in_image(self, search_strings, monitor_index: Optional[int] = None) -> Optional[Tuple[str, Tuple[int, int], bool]]:
        """Find the given string(s) in a screenshot from the selected monitor using EasyOCR. Returns (string, (x, y) center, is_button) if found and clicks the position. Always uses ScreenshotModel for the monitor."""
        import easyocr
        import json
        # Fallback: if screenshot_model is not set, try to import and instantiate it
        if self.screenshot_model is None:
            try:
                from models.screenshot_model import ScreenshotModel
                self.screenshot_model = ScreenshotModel()
            except Exception as e:
                self.logger.error(f"Could not initialize ScreenshotModel: {e}")
                return None
        # If monitor_index is not set, read from config.json
        if monitor_index is None:
            try:
                config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                monitor_index = config.get('selected_monitor_capture_setting', 1)
            except Exception as e:
                self.logger.error(f"Could not read monitor index from config.json: {e}")
                monitor_index = 1
        img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
        if img is None:
            self.logger.warning(f"Could not capture screenshot from monitor {monitor_index}")
            return None
        screenshot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(img_rgb)
        # Get monitor offset for absolute coordinates
        x_offset, y_offset = 0, 0
        try:
            with self.screenshot_model._get_mss() as sct:
                monitors = sct.monitors
                if 0 < monitor_index < len(monitors):
                    mon = monitors[monitor_index]
                    x_offset, y_offset = mon['left'], mon['top']
        except Exception:
            pass
        found_strings = []
        button_like = [s.lower() for s in search_strings]
        for (bbox, text, conf) in results:
            found_strings.append(text)
            for search in search_strings:
                if search.lower() in text.lower():
                    x = int((bbox[0][0] + bbox[2][0]) / 2) + x_offset
                    y = int((bbox[0][1] + bbox[2][1]) / 2) + y_offset
                    is_button = text.strip().lower() in button_like
                    self.logger.info(f"Found '{text}' at ({x}, {y}) in image with EasyOCR. Button-like: {is_button}.")
                    if is_button:
                        self.move_mouse_and_click(x, y)
                        self.logger.info(f"Clicked on button-like text '{text}' at ({x}, {y})")
                        print(f"Button found: {text}")
                        # Save position in config
                        try:
                            self.save_string_position_to_config(text.strip(), [x, y])
                        except Exception as e:
                            self.logger.error(f"Failed to save string position to config: {e}")
                        return (text, (x, y), True)
        print(f"OCR found strings: {found_strings}")
        self.logger.info(f"None of the button-like strings {search_strings} found in image (EasyOCR).")
        return None

    def move_mouse_and_click(self, x: int, y: int, duration: float = 0.5):
        """Move the mouse to (x, y) slowly and click."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(x, y)
            
            
            
            print(f"Clicked at ({x}, {y})")
            self.logger.info(f"Moved mouse to ({x}, {y}) over {duration}s and clicked.")
        except Exception as e:
            self.logger.error(f"Error moving mouse and clicking: {e}")

    def cache_ocr_for_monitor(self, monitor_index: int):
        """Perform OCR for the given monitor and cache the result."""
        import easyocr
        if self.screenshot_model is None:
            try:
                from models.screenshot_model import ScreenshotModel
                self.screenshot_model = ScreenshotModel()
            except Exception as e:
                self.logger.error(f"Could not initialize ScreenshotModel: {e}")
                return None
        img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
        if img is None:
            self.logger.warning(f"Could not capture screenshot from monitor {monitor_index}")
            return None
        screenshot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        reader = easyocr.Reader(['en'], gpu=True)
        results = reader.readtext(img_rgb)
        self.ocr_cache[monitor_index] = results
        return results

    def save_found_positions_to_config(self, found_positions, config_path=None):
        """Save found string positions to config.json under 'ocr_found_positions'."""
        import json
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        # Read existing config
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}
        config['ocr_found_positions'] = found_positions
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        self.logger.info(f"Saved OCR found positions to {config_path}")

    def save_string_position_to_config(self, string, position, monitor_index=None, config_path=None):
        """Save or update the position and monitor of a found string in config.json under 'ocr_found_positions'.
        If monitor_index is None, use the current selected_monitor_capture_setting from config."""
        import json
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        # Read existing config
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}
        if 'ocr_found_positions' not in config:
            config['ocr_found_positions'] = {}
        # If monitor_index is None, use selected_monitor_capture_setting
        if monitor_index is None:
            monitor_index = config.get('selected_monitor_capture_setting', 1)
        config['ocr_found_positions'][string] = {
            'position': position,
            'monitor_index': monitor_index
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        self.logger.info(f"Saved position and monitor for string '{string}' to {config_path}")

    def get_cached_ocr(self, monitor_index: int):
        """Get cached OCR results for a monitor, or perform OCR if not cached."""
        if monitor_index in self.ocr_cache:
            return self.ocr_cache[monitor_index]
        return self.cache_ocr_for_monitor(monitor_index)

    def get_position_from_config(self, string, config_path=None):
        """Retrieve the position and monitor index for a string from config.json."""
        import json
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            entry = config.get('ocr_found_positions', {}).get(string)
            if entry:
                return entry['position'], entry.get('monitor_index')
        except Exception:
            pass
        return None, None
# Patch ScreenshotModel to add _get_mss if not present
try:
    from models.screenshot_model import ScreenshotModel
    if not hasattr(ScreenshotModel, '_get_mss'):
        import mss
        def _get_mss(self):
            return mss.mss()
        ScreenshotModel._get_mss = _get_mss
except Exception:
    pass
