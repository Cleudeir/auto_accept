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
        self.screenshot_model = screenshot_model
        self.ocr_cache = {}

    def _load_reference_images(self) -> dict:
        """Load reference images for detection"""
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin"
        )
        references = {
            "dota": os.path.join(base_path, "dota.png"),
            "dota2_plus": os.path.join(base_path, "dota2_plus.png"),
            "read_check": os.path.join(base_path, "read_check.jpg"),
            "long_time": os.path.join(base_path, "long_time.png"),
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
                scores[name] = (
                    0.0  # Return the name with the highest score only if it's >= 0.8
                )
        if scores:
            print(f"Scores: {scores}")
            highest_score_name = max(scores, key=scores.get)
            highest_score = scores[highest_score_name]
            if highest_score >= 0.8:
                return highest_score_name
        return "none"

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

    def process_detection_result(self, highest_match: str) -> str:
        """Process detection results and return action taken using only OCR and Enter key"""
        action = "none"

        if highest_match == "long_time":
            print(f"Long matchmaking wait dialog detected")
            print(f"Pressing ESC key")
            pyautogui.press("esc")
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "long_time_dialog_detected"

        elif highest_match == "read_check":
            print(f"Pressing Enter key")
            pyautogui.press("enter")
            print(f"Read-check pattern detected")
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "read_check_detected"

        elif highest_match in ["dota", "dota2_plus"]:
            print(f"Match detected with highest match: {highest_match}")
            self.focus_dota2_window()
            print(f"Pressing Enter key")
            pyautogui.press("enter")
            self.send_enter_key_if_text_found(["OK", "READY", "ACCEPT"])
            action = "match_detected"

        elif highest_match == "ad":
            print(f"Advertisement detected")
            action = "ad_detected"

        return action

    def send_enter_key_if_text_found(self, search_strings):

        print(f"Searching for text: {search_strings}")
        result = self.find_string_in_image(search_strings)
        if result:
            self.logger.info(f"Text '{result[0]}' found, pressed Enter.")
        else:
            self.logger.info(f"No relevant text found, pressed Enter as fallback.")

    def find_string_in_image(
        self, search_strings, monitor_index: Optional[int] = None
    ) -> Optional[Tuple[str, Tuple[int, int], bool]]:
        """Find the given string(s) in a screenshot from the selected monitor using EasyOCR. Returns (string, (x, y) center, is_button) if found and clicks the position. Always uses ScreenshotModel for the monitor."""
        import easyocr
        import json

        if self.screenshot_model is None:
            try:
                from models.screenshot_model import ScreenshotModel

                self.screenshot_model = ScreenshotModel()
            except Exception as e:
                self.logger.error(f"Could not initialize ScreenshotModel: {e}")
                return None
        if monitor_index is None:
            try:
                config_path = os.path.join(
                    os.path.dirname(__file__), "..", "config.json"
                )
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                monitor_index = config.get("selected_monitor_capture_setting", 1)
            except Exception as e:
                self.logger.error(f"Could not read monitor index from config.json: {e}")
                monitor_index = 1
        img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
        if img is None:
            self.logger.warning(
                f"Could not capture screenshot from monitor {monitor_index}"
            )
            return None
        screenshot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        reader = easyocr.Reader(["en"], gpu=False)
        results = reader.readtext(img_rgb)
        x_offset, y_offset = 0, 0
        try:
            with self.screenshot_model._get_mss() as sct:
                monitors = sct.monitors
                if 0 < monitor_index < len(monitors):
                    mon = monitors[monitor_index]
                    x_offset, y_offset = mon["left"], mon["top"]
        except Exception:
            pass
        found_strings = []
        button_like = [s.lower() for s in search_strings]
        for bbox, text, conf in results:
            found_strings.append(text)
            for search in search_strings:
                if search.lower() in text.lower():
                    x = int((bbox[0][0] + bbox[2][0]) / 2) + x_offset
                    y = int((bbox[0][1] + bbox[2][1]) / 2) + y_offset
                    is_button = text.strip().lower() in button_like
                    self.logger.info(
                        f"Found '{text}' at ({x}, {y}) in image with EasyOCR. Button-like: {is_button}."
                    )
                    if is_button:
                        self.move_mouse_and_click(x, y)
                        self.logger.info(
                            f"Clicked on button-like text '{text}' at ({x}, {y})"
                        )
                        print(f"Button found: {text}")
                        try:
                            self.save_string_position_to_config(text.strip(), [x, y])
                        except Exception as e:
                            self.logger.error(
                                f"Failed to save string position to config: {e}"
                            )
                        return (text, (x, y), True)
        print(f"OCR found strings: {found_strings}")
        self.logger.info(
            f"None of the button-like strings {search_strings} found in image (EasyOCR)."
        )
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
            self.logger.warning(
                f"Could not capture screenshot from monitor {monitor_index}"
            )
            return None
        screenshot = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        reader = easyocr.Reader(["en"], gpu=True)
        results = reader.readtext(img_rgb)
        self.ocr_cache[monitor_index] = results
        return results

    def save_found_positions_to_config(self, found_positions, config_path=None):
        """Save found string positions to config.json under 'ocr_found_positions'."""
        import json

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
        config["ocr_found_positions"] = found_positions
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        self.logger.info(f"Saved OCR found positions to {config_path}")

    def save_string_position_to_config(
        self, string, position, monitor_index=None, config_path=None
    ):
        """Save or update the position and monitor of a found string in config.json under 'ocr_found_positions'.
        If monitor_index is None, use the current selected_monitor_capture_setting from config.
        """
        import json

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}
        if "ocr_found_positions" not in config:
            config["ocr_found_positions"] = {}
        if monitor_index is None:
            monitor_index = config.get("selected_monitor_capture_setting", 1)
        config["ocr_found_positions"][string] = {
            "position": position,
            "monitor_index": monitor_index,
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        self.logger.info(
            f"Saved position and monitor for string '{string}' to {config_path}"
        )

    def get_cached_ocr(self, monitor_index: int):
        """Get cached OCR results for a monitor, or perform OCR if not cached."""
        if monitor_index in self.ocr_cache:
            return self.ocr_cache[monitor_index]
        return self.cache_ocr_for_monitor(monitor_index)

    def get_position_from_config(self, string, config_path=None):
        """Retrieve the position and monitor index for a string from config.json."""
        import json

        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            entry = config.get("ocr_found_positions", {}).get(string)
            if entry:
                return entry["position"], entry.get("monitor_index")
        except Exception:
            pass
        return None, None


try:
    from models.screenshot_model import ScreenshotModel

    if not hasattr(ScreenshotModel, "_get_mss"):
        import mss

        def _get_mss(self):
            return mss.mss()

        ScreenshotModel._get_mss = _get_mss
except Exception:
    pass
