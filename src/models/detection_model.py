import os
import logging
import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from typing import Tuple, Optional
import time


class DetectionModel:
    """Model for handling image detection and comparison logic"""

    def __init__(self, screenshot_model=None, score_threshold: float = 0.7):
        self.logger = logging.getLogger("Dota2AutoAccept.DetectionModel")
        self.reference_images = self._load_reference_images()
        self.screenshot_model = screenshot_model
        self.ocr_cache = {}
        self.score_threshold = score_threshold

    def set_score_threshold(self, threshold: float):
        """Set the threshold for highest_score detection"""
        self.score_threshold = threshold

    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"
        )
        references = {
            "dota": os.path.join(base_path, "dota.png"),
            "dota2_plus": os.path.join(base_path, "dota2_plus.jpeg"),
            "read_check": os.path.join(base_path, "read_check.jpg"),
            "long_time": os.path.join(base_path, "long_time.png"),
            "watch-game": os.path.join(base_path, "watch-game.png"),
            "ad": os.path.join(base_path, "AD.png"),
        }
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

            if img1_gray.shape != img2_gray.shape:
                img2_gray = cv2.resize(
                    img2_gray, (img1_gray.shape[1], img1_gray.shape[0])
                )

            score, _ = ssim(img1_gray, img2_gray, full=True)
            return score
        except Exception as e:
            self.logger.error(f"Error comparing images: {e}")
            return 0.0

    def compare_image_with_reference(self, img: Image.Image, ref_path: str) -> float:
        try:
            # Load reference image using PIL to avoid OpenCV color space issues
            ref_pil = Image.open(
                ref_path
            )  # Ensure both images have the same size - resize reference to match input image
            if ref_pil.size != img.size:
                self.logger.debug(
                    f"Resizing reference image from {ref_pil.size} to {img.size}"
                )
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
            self.logger.debug(
                f"Image shapes don't match after equalization: {img_np.shape} vs {ref_np.shape}"
            )
            if img_np.shape != ref_np.shape:
                self.logger.warning(
                    f"Image shapes don't match after equalization: {img_np.shape} vs {ref_np.shape}"
                )
                return 0.0

            # Compute SSIM on raw color images without any color space conversion
            score, _ = ssim(img_np, ref_np, full=True, channel_axis=2)

            return score
        except Exception as e:
            self.logger.error(f"Error comparing image with reference: {e}")
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
            print(f"Scores: {scores}")
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
            print(f"Scores: {scores}")
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
            self.logger.info("Enter key pressed")
        except Exception as e:
            self.logger.error(f"Error pressing Enter key: {e}")

    def process_detection_result(self, highest_match: str) -> str:
        """Process detection results and return action taken using only OCR and Enter key"""
        action = "none"
        print(f"Processing detection result: {highest_match}")
        # Only focus Dota 2 window when an action is about to be performed
        if highest_match == "watch-game":
            print(f"Watch game dialog detected")
            self.focus_dota2_window()
            print(f"Pressing ESC key")
            pyautogui.press("esc")
            time.sleep(1)
            pyautogui.press("esc")
            action = "watch_game_dialog_detected"
        elif highest_match == "long_time":
            print(f"Long matchmaking wait dialog detected")
            self.focus_dota2_window()
            print(f"Pressing ESC key")
            pyautogui.press("esc")
            time.sleep(1)
            pyautogui.press("esc")
            action = "long_time_dialog_detected"
        elif highest_match == "read_check":
            print(f"Read-check pattern detected")
            self.focus_dota2_window()
            print(f"Pressing Enter key")
            pyautogui.press("enter")
            time.sleep(1)
            pyautogui.press("enter")
            action = "read_check_detected"
        elif highest_match in ["dota", "dota2_plus"]:
            print(f"Match detected with highest match: {highest_match}")
            self.focus_dota2_window()
            print(f"Pressing Enter key")
            pyautogui.press("enter")
            time.sleep(1)
            pyautogui.press("enter")
            action = "match_detected"
        elif highest_match == "ad":
            print(f"Advertisement detected")
            self.focus_dota2_window()
            action = "ad_detected"
        return action

    def focus_dota2_window(self):
        """Simple: Focus the first Dota 2 window found using pygetwindow only."""
        try:
            dota_window = gw.getWindowsWithTitle("Dota 2")[0]
            if dota_window.isMinimized:
                dota_window.restore()
            dota_window.activate()
            self.logger.info("Focused Dota 2 window (pygetwindow, simple)")
        except Exception as e:
            self.logger.error(f"Could not focus Dota 2 window: {e}")

