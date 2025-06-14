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
    
    def __init__(self):
        self.logger = logging.getLogger("Dota2AutoAccept.DetectionModel")
        self.reference_images = self._load_reference_images()
    
    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        references = {
            "dota": os.path.join("bin", "dota.png"),
            "print": os.path.join("bin", "print.png"),
            "read_check": os.path.join("bin", "read-check.jpg"),
            "long_time": os.path.join("bin", "long-time.png")
        }
        
        # Verify all reference images exist
        for name, path in references.items():
            if not os.path.exists(path):
                self.logger.warning(f"Reference image not found: {path}")
        # Also check for button images
        button_images = [
            os.path.join("bin", "dota.png"),
            os.path.join("bin", "long-time.png"),
            os.path.join("bin", "ready_button.png"),
            os.path.join("bin", "no_button.png"),
        ]
        for btn_path in button_images:
            if not os.path.exists(btn_path):
                self.logger.warning(f"Reference image not found: {btn_path}")
            else:
                self.logger.info(f"Reference image found: {btn_path}")
        
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
        
        # Compare with each reference image
        for name, ref_path in self.reference_images.items():
            if os.path.exists(ref_path):
                score = self.compare_image_with_reference(img, ref_path)
                scores[name] = score
                  # Check for matches based on thresholds
                if name in ["dota", "print"] and score > 0.8:
                    match_found = True
                elif name == "read_check" and score > 0.8:
                    # Special case for read-check (different action)
                    match_found = True
                elif name == "long_time" and score > 0.8:
                    # Special case for long matchmaking wait dialog
                    match_found = True
            else:
                scores[name] = 0.0
        
        return match_found, scores
    
    def focus_dota2_window(self) -> bool:
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
    
    def detect_ok_button_position(self, screenshot: Optional[np.ndarray] = None) -> Optional[Tuple[int, int]]:
        """Detect the position of any button (OK, ACCEPT, READY, NO) using template matching. Returns (x, y) center or None."""
        button_templates = [
            os.path.join("bin", "ok_button.png"),
            os.path.join("bin", "accept_button.png"),
            os.path.join("bin", "ready_button.png"),
            os.path.join("bin", "no_button.png"),
        ]
        if screenshot is None:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        threshold = 0.8
        for path in button_templates:
            if not os.path.exists(path):
                continue
            template = cv2.imread(path)
            if template is None:
                continue
            res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                tH, tW = template.shape[:2]
                center_x = max_loc[0] + tW // 2
                center_y = max_loc[1] + tH // 2
                return (center_x, center_y)
        self.logger.info("No button detected (OK, ACCEPT, READY, NO)")
        return None

    def click_ok_button(self):
        """Detect and click the OK button, or fallback to pressing Enter."""
        try:
            self.focus_dota2_window()
            import time
            time.sleep(0.5)
            pos = self.detect_ok_button_position()
            if pos:
                pyautogui.click(pos[0], pos[1])
                self.logger.info(f"Clicked OK button at {pos}")
            else:
                pyautogui.press("enter")
                time.sleep(0.5)
                pyautogui.press("enter")
                self.logger.info("OK button confirmed by pressing Enter (fallback)")
        except Exception as e:
            self.logger.error(f"Error confirming OK button: {e}")

    def send_enter_key(self):
        """Send Enter key press"""
        try:
            pyautogui.press("enter")
            self.logger.info("Enter key pressed")
        except Exception as e:
            self.logger.error(f"Error pressing Enter key: {e}")
    
    def process_detection_result(self, scores: dict) -> str:
        """Process detection results and return action taken"""
        action = "none"
        
        # Check for long matchmaking wait dialog first
        if scores.get("long_time", 0) > 0.8:
            self.click_any_button()
            action = "long_time_dialog_detected"
        # Check for read-check pattern (different action)
        elif scores.get("read_check", 0) > 0.8:
            self.click_ok_button()
            action = "read_check_detected"
        # Check for main match patterns
        elif scores.get("dota", 0) > 0.8 or scores.get("print", 0) > 0.8:
            self.focus_dota2_window()
            self.click_ok_button()
            action = "match_detected"
        
        return action

    def detect_buttons_position(self, screenshot: Optional[np.ndarray] = None) -> Optional[Tuple[str, Tuple[int, int]]]:
        """Detect the position and label of the first found button (ACCEPT, OK, READY, NO) using template matching."""
        button_templates = {
            "ACCEPT": os.path.join("bin", "dota.png"),          
            "ACCEPT": os.path.join("bin", "dota2-plus.jpeg"),
            "OK": os.path.join("bin", "long-time.png"),
            "READY": os.path.join("bin", "ready_button.png"),
            "NO": os.path.join("bin", "watch-game.png"),
        }
        if screenshot is None:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        threshold = 0.8
        for label, path in button_templates.items():
            if not os.path.exists(path):
                continue
            template = cv2.imread(path)
            if template is None:
                continue
            res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                tH, tW = template.shape[:2]
                center_x = max_loc[0] + tW // 2
                center_y = max_loc[1] + tH // 2
                return (label, (center_x, center_y))
        return None

    def click_any_button(self):
        """Detect and click any button (OK, ACCEPT, READY, NO) using template matching or OCR. Fallback to pressing Enter if not found."""
        try:
            self.focus_dota2_window()
            import time
            time.sleep(0.5)
            # Try template matching first
            pos = self.detect_ok_button_position()
            if pos:
                pyautogui.click(pos[0], pos[1])
                self.logger.info(f"Clicked button at {pos} (template match)")
                return
            # Try OCR if template matching fails
            result = self.find_string_in_image(["OK", "ACCEPT", "READY", "NO"])
            if result:
                _, (x, y) = result
                pyautogui.click(x, y)
                self.logger.info(f"Clicked button at ({x}, {y}) (OCR)")
                return
            # Fallback
            pyautogui.press("enter")
            time.sleep(0.5)
            pyautogui.press("enter")
            self.logger.info("No button detected, pressed Enter as fallback")
        except Exception as e:
            self.logger.error(f"Error clicking any button: {e}")

    def find_string_in_image(self, search_strings, screenshot: Optional[np.ndarray] = None) -> Optional[Tuple[str, Tuple[int, int]]]:
        """Find the given string(s) in a screenshot using OCR. Returns (string, (x, y) center) if found."""
        try:
            import pytesseract
        except ImportError:
            self.logger.error("pytesseract is required for OCR. Please install it with 'pip install pytesseract'.")
            return None
        if screenshot is None:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            for search in search_strings:
                if search.lower() in text.lower():
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    self.logger.info(f"Found '{search}' at ({x}, {y}) in image.")
                    return (search, (x, y))
        self.logger.info(f"None of the strings {search_strings} found in image.")
        return None

    def move_mouse_and_click(self, x: int, y: int, duration: float = 0.5):
        """Move the mouse to (x, y) slowly and click."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(x, y)
            self.logger.info(f"Moved mouse to ({x}, {y}) over {duration}s and clicked.")
        except Exception as e:
            self.logger.error(f"Error moving mouse and clicking: {e}")
