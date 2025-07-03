import threading
import time
from typing import Callable, Optional


class DetectionController:
    """Controller for handling detection logic and threading"""

    def __init__(self, detection_model, screenshot_model, audio_model, config_model):
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
            return True
        else:
            if hasattr(self, "on_start_failed") and callable(self.on_start_failed):
                self.on_start_failed("Detection is already running.")
        return False

    def stop_detection(self):
        """Stop the detection process"""
        if self.is_running:
            self.is_running = False
            return True
        return False

    def _detection_loop(self):
        """Main detection loop that runs in a separate thread"""

        try:
            while self.is_running:
                monitor_index = self.screenshot_model.auto_detect_dota_monitor()
                img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
                if img is not None:
                    highest_match, highest_score = self.detection_model.detect_match_in_image_with_score(img)

                    if highest_match == "ad":
                        self.is_running = False
                        break

                    if highest_match in [
                        "dota",
                        "dota2_plus",
                        "read_check",
                        "long_time",
                        "watch-game",
                        "ad",
                    ]:
                        action = self.detection_model.process_detection_result(
                            highest_match
                        )

                        if action == "read_check_detected":
                            try:                               
                                pass
                            except Exception as e:
                                pass
                        elif action == "long_time_dialog_detected":
                            pass
                        elif action == "match_detected":
                            self.audio_model.play_alert_sound(
                                self.config_model.selected_device_id,
                                self.config_model.alert_volume,
                            )
                            self.match_found = True
                            if self.on_match_found:
                                self.on_match_found()
                        elif action == "watch_game_dialog_detected":
                            pass

                    if self.on_detection_update:
                        self.on_detection_update(img, highest_match, highest_score)
                else:
                    pass

                time.sleep(1)

        except Exception as e:
            pass
        finally:
            pass

    def get_status(self) -> dict:
        """Get current detection status"""
        return {
            "is_running": self.is_running,
            "match_found": self.match_found,
            "thread_alive": (
                self.detection_thread.is_alive() if self.detection_thread else False
            ),
        }
