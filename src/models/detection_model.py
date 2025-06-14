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
            else:
                scores[name] = 0.0
        # Return ad_stop flag in scores for controller to act on
        scores["ad_stop"] = ad_stop
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
            self.send_enter_key_if_text_found(["OK", "READY", "NO", "ACCEPT"])
            action = "long_time_dialog_detected"
        # Check for read-check pattern (different action)
        elif scores.get("read_check", 0) > 0.8:
            print(f"Read-check pattern detected with score {scores['read_check']:.2f}")
            self.send_enter_key_if_text_found(["OK", "READY", "NO", "ACCEPT"])
            action = "read_check_detected"
        # Check for main match patterns
        elif scores.get("dota", 0) > 0.8 or scores.get("print", 0) > 0.8:
            print(f"Match detected with scores: Dota={scores.get('dota', 0):.2f}, Print={scores.get('print', 0):.2f}")
            self.focus_dota2_window()
            self.send_enter_key_if_text_found(["OK", "READY", "NO", "ACCEPT"])
            action = "match_detected"
        return action

    def send_enter_key_if_text_found(self, search_strings):
        """Use OCR to find text and press Enter if found, otherwise always press Enter as fallback."""
        result = self.find_string_in_image(search_strings)
        pyautogui.press("enter")
        if result:
            self.logger.info(f"Text '{result[0]}' found, pressed Enter.")
        else:
            self.logger.info(f"No relevant text found, pressed Enter as fallback.")

    def find_string_in_image(self, search_strings, screenshot: Optional[np.ndarray] = None) -> Optional[Tuple[str, Tuple[int, int]]]:
        """Find the given string(s) in a screenshot using EasyOCR. Returns (string, (x, y) center) if found and clicks the position."""
        import easyocr
        if screenshot is None:
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        # Convert screenshot to RGB for EasyOCR
        img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(img_rgb)
        for (bbox, text, conf) in results:
            for search in search_strings:
                if search.lower() in text.lower():
                    # bbox: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                    x = int((bbox[0][0] + bbox[2][0]) / 2)
                    y = int((bbox[0][1] + bbox[2][1]) / 2)
                    self.logger.info(f"Found '{search}' at ({x}, {y}) in image with EasyOCR. Clicking...")
                    self.move_mouse_and_click(x, y)
                    return (search, (x, y))
        self.logger.info(f"None of the strings {search_strings} found in image (EasyOCR).")
        return None

    def move_mouse_and_click(self, x: int, y: int, duration: float = 0.5):
        """Move the mouse to (x, y) slowly and click."""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            pyautogui.click(x, y)
            self.logger.info(f"Moved mouse to ({x}, {y}) over {duration}s and clicked.")
        except Exception as e:
            self.logger.error(f"Error moving mouse and clicking: {e}")
