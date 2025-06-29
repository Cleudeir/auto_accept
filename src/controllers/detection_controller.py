import logging
import threading
import time
from typing import Callable, Optional


class DetectionController:
    """Controller for handling detection logic and threading"""

    def __init__(self, detection_model, screenshot_model, audio_model, config_model):
        self.logger = logging.getLogger("Dota2AutoAccept.DetectionController")
        self.detection_model = detection_model
        self.screenshot_model = screenshot_model
        self.audio_model = audio_model
        self.config_model = config_model

        self.is_running = False
        self.match_found = False
        self.detection_thread = None

        self.on_match_found = None
        self.on_detection_update = None
        self.on_start_failed = None

    def start_detection(self):
        """Start the detection process"""
        if not self.is_running:
            self.is_running = True
            self.match_found = False
            self.detection_thread = threading.Thread(
                target=self._detection_loop, daemon=True
            )
            self.detection_thread.start()
            self.logger.info("Detection started!")
            return True
        else:
            self.logger.warning("Detection already running. Start request ignored.")
            if hasattr(self, "on_start_failed") and callable(self.on_start_failed):
                self.on_start_failed("Detection is already running.")
        return False

    def stop_detection(self):
        """Stop the detection process"""
        if self.is_running:
            self.is_running = False
            self.logger.info("Detection stopped!")
            return True
        return False

    def _detection_loop(self):
        """Main detection loop that runs in a separate thread"""
        self.logger.info("Detection loop started")

        try:
            while self.is_running:
                monitor_index = self.config_model.selected_monitor_capture_setting
                img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
                if img is not None:
                    highest_match = self.detection_model.detect_match_in_image(img)

                    self.logger.info(f"Highest match: {highest_match}")

                    if highest_match == "ad":
                        self.logger.info("AD.png detected. Stopping detection loop.")
                        self.is_running = False
                        break

                    if highest_match in [
                        "dota",
                        "dota2_plus",
                        "read_check",
                        "long_time",
                    ]:
                        action = self.detection_model.process_detection_result(
                            highest_match
                        )

                        if action == "read_check_detected":
                            self.logger.info(
                                "Read-check pattern detected! Pressing Enter."
                            )
                            try:
                                # Simulate pressing Enter or handle read-check here
                                # (Add your actual code for pressing Enter if needed)
                                self.logger.debug("Read-check action executed successfully.")
                            except Exception as e:
                                self.logger.error(f"Error during read-check action: {e}")
                        elif action == "long_time_dialog_detected":
                            self.logger.info(
                                "Long matchmaking wait dialog detected! Clicking OK button."
                            )
                        elif action == "match_detected":
                            self.logger.info(
                                "Match detected! Focusing Dota 2 window, pressing Enter and playing sound."
                            )
                            self.audio_model.play_alert_sound(
                                self.config_model.selected_device_id,
                                self.config_model.alert_volume,
                            )
                            self.match_found = True
                            if self.on_match_found:
                                self.on_match_found()

                    if self.on_detection_update:
                        self.on_detection_update(img, highest_match)
                else:
                    self.logger.warning(
                        "Monitor capture failed for this iteration. Will retry."
                    )

                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Error in detection loop: {e}")
        finally:
            self.logger.info("Detection loop ended")

    def get_status(self) -> dict:
        """Get current detection status"""
        return {
            "is_running": self.is_running,
            "match_found": self.match_found,
            "thread_alive": (
                self.detection_thread.is_alive() if self.detection_thread else False
            ),
        }
