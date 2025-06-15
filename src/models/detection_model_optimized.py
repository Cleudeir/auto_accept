import os
import logging
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image
from typing import Tuple, Optional

class DetectionModel:
    """Model for handling image detection and comparison logic - OPTIMIZED VERSION"""
    
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
    
    def compare_images_opencv(self, img1_gray, img2_gray) -> float:
        """Compare two grayscale images using OpenCV template matching instead of SSIM"""
        try:
            # Ensure images are the same size
            if img1_gray.shape != img2_gray.shape:
                img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
            
            # Use normalized cross-correlation for comparison
            result = cv2.matchTemplate(img1_gray, img2_gray, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            # Alternative: Use Mean Squared Error (lower is better, convert to similarity score)
            mse = np.mean((img1_gray.astype(float) - img2_gray.astype(float)) ** 2)
            similarity = 1.0 / (1.0 + mse / 10000.0)  # Normalize MSE to similarity score
            
            # Return the maximum of both methods
            return max(max_val, similarity)
            
        except Exception as e:
            self.logger.error(f"Error in OpenCV comparison: {e}")
            return 0.0
    
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
            
            return self.compare_images_opencv(img1_gray, img2_gray)
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
            
            # Use OpenCV comparison instead of SSIM
            return self.compare_images_opencv(img_gray, ref_gray)
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
                    ad_stop = True
                    self.logger.info(f"AD detected with score: {score:.3f}")
                elif name == "dota" and score >= 0.7:
                    match_found = True
                    self.logger.info(f"Match found - {name} with score: {score:.3f}")
                elif name == "print" and score >= 0.7:
                    match_found = True
                    self.logger.info(f"Match found - {name} with score: {score:.3f}")
                elif name == "read_check" and score >= 0.6:
                    match_found = True
                    self.logger.info(f"Match found - {name} with score: {score:.3f}")
                elif name == "long_time" and score >= 0.6:
                    self.logger.info(f"Long time detected with score: {score:.3f}")
        
        # Return match found and scores
        result = {
            "scores": scores,
            "ad_detected": ad_stop,
            "match_found": match_found and not ad_stop
        }
        
        return match_found and not ad_stop, result

    # Keep all other methods the same...
    def click_accept_button(self, img: Image.Image, monitor_info: dict) -> bool:
        """
        Click the accept button if found in the image
        monitor_info contains: x, y, width, height of the monitor
        """
        try:
            # Convert PIL Image to numpy array for OpenCV
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Create accept button template programmatically
            accept_button = self._create_accept_button_template()
            
            # Try to find the accept button using template matching
            result = cv2.matchTemplate(img_bgr, accept_button, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            # If confidence is high enough, click the button
            if max_val > 0.7:  # 70% confidence threshold
                # Calculate actual screen coordinates
                button_x = monitor_info['x'] + max_loc[0] + accept_button.shape[1] // 2
                button_y = monitor_info['y'] + max_loc[1] + accept_button.shape[0] // 2
                
                self.logger.info(f"Accept button found at ({button_x}, {button_y}) with confidence {max_val:.3f}")
                
                # Click the button
                pyautogui.click(button_x, button_y)
                return True
            else:
                self.logger.debug(f"Accept button not found (max confidence: {max_val:.3f})")
                return False
                
        except Exception as e:
            self.logger.error(f"Error clicking accept button: {e}")
            return False
    
    def _create_accept_button_template(self):
        """Create a template for the accept button"""
        # Create a simple green button template
        # This is a placeholder - you might want to use an actual button image
        template = np.zeros((50, 120, 3), dtype=np.uint8)
        template[:, :] = [0, 255, 0]  # Green color
        return template
    
    def get_monitor_at_coordinates(self, x: int, y: int) -> Optional[dict]:
        """Get monitor information for the given coordinates"""
        try:
            if self.screenshot_model:
                monitors = self.screenshot_model.get_monitors()
                for monitor in monitors:
                    if (monitor['x'] <= x <= monitor['x'] + monitor['width'] and
                        monitor['y'] <= y <= monitor['y'] + monitor['height']):
                        return monitor
            return None
        except Exception as e:
            self.logger.error(f"Error getting monitor at coordinates: {e}")
            return None
    
    def auto_click_accept(self, detection_result: dict) -> bool:
        """
        Automatically click accept button based on detection result
        """
        try:
            if not detection_result.get("match_found", False):
                return False
            
            # Take a fresh screenshot to get the accept button
            if self.screenshot_model:
                monitors = self.screenshot_model.get_monitors()
                for monitor in monitors:
                    screenshot = self.screenshot_model.capture_monitor(monitor)
                    if screenshot:
                        if self.click_accept_button(screenshot, monitor):
                            return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error in auto click accept: {e}")
            return False
    
    def find_dota_window(self) -> Optional[gw.Win32Window]:
        """Find the Dota 2 window"""
        try:
            windows = gw.getWindowsWithTitle("Dota 2")
            if windows:
                return windows[0]
            return None
        except Exception as e:
            self.logger.error(f"Error finding Dota window: {e}")
            return None
    
    def get_dota_window_info(self) -> Optional[dict]:
        """Get Dota 2 window information"""
        try:
            dota_window = self.find_dota_window()
            if dota_window:
                return {
                    "x": dota_window.left,
                    "y": dota_window.top,
                    "width": dota_window.width,
                    "height": dota_window.height,
                    "title": dota_window.title
                }
            return None
        except Exception as e:
            self.logger.error(f"Error getting Dota window info: {e}")
            return None
