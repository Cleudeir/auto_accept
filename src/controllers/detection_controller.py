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
        
        # Callbacks
        self.on_match_found = None
        self.on_detection_update = None
        self.on_start_failed = None
    
    def start_detection(self):
        """Start the detection process"""
        if not self.is_running:
            self.is_running = True
            self.match_found = False
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            self.logger.info("Detection started!")
            return True
        else:
            self.logger.warning("Detection already running. Start request ignored.")
            if hasattr(self, 'on_start_failed') and callable(self.on_start_failed):
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
                # Capture screenshot
                monitor_index = self.config_model.selected_monitor_capture_setting
                img = self.screenshot_model.capture_monitor_screenshot(monitor_index)
                
                if img is not None:
                    # Detect matches in the image
                    match_found, scores = self.detection_model.detect_match_in_image(img)
                    
                    # Log similarity scores
                    score_str = ", ".join([f"{k}={v:.2f}" for k, v in scores.items()])
                    self.logger.info(f"Similarity scores: {score_str}")
                    
                    if scores.get("ad_stop", False):
                        self.logger.info("AD.png detected with similarity >= 0.6. Stopping detection loop.")
                        self.is_running = False
                        break
                      # Process detection results
                    if match_found:
                        action = self.detection_model.process_detection_result(scores)
                        
                        if action == "read_check_detected":
                            self.logger.info("Read-check pattern detected! Pressing Enter.")
                        elif action == "long_time_dialog_detected":
                            self.logger.info("Long matchmaking wait dialog detected! Clicking OK button.")
                        elif action == "match_detected":
                            self.logger.info("Match detected! Focusing Dota 2 window, pressing Enter and playing sound.")
                            # Play alert sound
                            self.audio_model.play_alert_sound(
                                self.config_model.selected_device_id,
                                self.config_model.alert_volume
                            )
                            # Set match found flag (do not stop detection)
                            self.match_found = True
                            # self.is_running = False  # Removed stopping on accept
                            # Notify callback
                            if self.on_match_found:
                                self.on_match_found()
                        
                    # Notify update callback
                    if self.on_detection_update:
                        self.on_detection_update(img, scores)
                else:
                    self.logger.warning("Monitor capture failed for this iteration. Will retry.")
                
                # Wait before next detection
                time.sleep(5)
                
        except Exception as e:
            self.logger.error(f"Error in detection loop: {e}")
        finally:
            self.logger.info("Detection loop ended")
    
    def get_status(self) -> dict:
        """Get current detection status"""
        return {
            "is_running": self.is_running,
            "match_found": self.match_found,
            "thread_alive": self.detection_thread.is_alive() if self.detection_thread else False
        }
