import os
import mss
import logging
from typing import List, Tuple

from models.config_model import ConfigModel
from models.audio_model import AudioModel
from models.screenshot_model import ScreenshotModel
from models.detection_model import DetectionModel
from views.main_view import MainView
from controllers.detection_controller import DetectionController


class MainController:
    """Main controller that coordinates between models and views"""

    def __init__(self):
        self.logger = logging.getLogger("Dota2AutoAccept.MainController")
        self.config_model = ConfigModel()
        self.audio_model = AudioModel()
        self.screenshot_model = ScreenshotModel()
        self.detection_model = DetectionModel(config_model=self.config_model)

        self.detection_controller = DetectionController(
            self.detection_model,
            self.screenshot_model,
            self.audio_model,
            self.config_model,
        )

        # Choose UI based on config preference
        if self.config_model.use_modern_ui:
            from views.modern_main_view import ModernMainView
            self.view = ModernMainView(config_model=self.config_model)
        else:
            self.view = MainView(config_model=self.config_model)

        self._setup_callbacks()

        self._initialize_ui()

        self._setup_periodic_updates()

    def _setup_callbacks(self):
        """Setup callbacks between controllers and views"""
        self.view.on_start_detection = self._on_start_detection
        self.view.on_stop_detection = self._on_stop_detection
        self.view.on_test_sound = self._on_test_sound
        self.view.on_device_change = self._on_device_change
        self.view.on_volume_change = self._on_volume_change
        self.view.on_always_on_top_change = self._on_always_on_top_change
        self.view.on_closing = self._on_closing

        # Add callback for score threshold changes if the view supports it
        if hasattr(self.view, 'on_score_threshold_change'):
            self.view.on_score_threshold_change = self._on_score_threshold_change

        self.detection_controller.on_match_found = self._on_match_found
        self.detection_controller.on_detection_update = self._on_detection_update

    def _initialize_ui(self):
        """Initialize UI with current settings"""
        self.view.create_window()

        devices = self.audio_model.get_output_devices()
        device_names = [d["name"] for d in devices]
        selected_device_index = 0

        # Try to find the previously selected device
        if devices and self.config_model.selected_device_id is not None:
            for i, d in enumerate(devices):
                if d["id"] == self.config_model.selected_device_id:
                    selected_device_index = i
                    break
            else:
                # If the configured device is not found, reset to default (first device)
                self.logger.warning(f"Previously selected device ID {self.config_model.selected_device_id} not found. Using default device.")
                self.config_model.selected_device_id = devices[0]["id"] if devices else None
                selected_device_index = 0

        self.view.set_device_options(device_names, selected_device_index)

        self.detection_controller.start_detection()



        self.view.set_volume(int(self.config_model.alert_volume * 100))
        self.view.set_always_on_top(self.config_model.always_on_top)

        # Set initial threshold value if the view supports it
        if hasattr(self.view, 'set_score_threshold'):
            self.view.set_score_threshold(self.config_model.detection_threshold)

        self._position_window_on_second_monitor()

    def _position_window_on_second_monitor(self):
        """Position the window on the second monitor if available"""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if len(monitors) > 2:
                    
                    second_monitor = monitors[2]

                    window_width = 650
                    window_height = 600
                    x = (
                        second_monitor["left"]
                        + (second_monitor["width"] // 2)
                        - (window_width // 2)
                    )
                    y = (
                        second_monitor["top"]
                        + (second_monitor["height"] // 2)
                        - (window_height // 2)
                    )

                    self.view.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        except Exception:
            pass

    def _setup_periodic_updates(self):
        """Setup periodic UI updates"""
        self._update_status()
        self._update_screenshot_preview()

    def _update_status(self):
        """Update detection status in UI"""
        status = self.detection_controller.get_status()
        self.view.set_detection_state(status["is_running"], status["match_found"])

        self.view.after(500, self._update_status)

    def _update_screenshot_preview(self):
        """Update screenshot preview in UI"""
        img, timestamp = self.screenshot_model.get_latest_screenshot()
        self.view.update_screenshot(img, timestamp)

        self.view.after(1000, self._update_screenshot_preview)

    def refresh_audio_devices(self):
        """Refresh the list of available audio devices"""
        try:
            self.audio_model.refresh_devices()
            devices = self.audio_model.get_output_devices()
            device_names = [d["name"] for d in devices]
            
            # Check if current device is still available
            selected_device_index = 0
            if devices and self.config_model.selected_device_id is not None:
                for i, d in enumerate(devices):
                    if d["id"] == self.config_model.selected_device_id:
                        selected_device_index = i
                        break
                else:
                    # Current device not found, reset to first device
                    self.logger.warning("Current audio device no longer available. Switching to first available device.")
                    self.config_model.selected_device_id = devices[0]["id"] if devices else None
                    selected_device_index = 0
            
            self.view.set_device_options(device_names, selected_device_index)
            self.logger.info(f"Audio devices refreshed: {len(devices)} devices available")
            
        except Exception as e:
            self.logger.error(f"Error refreshing audio devices: {e}")

    def _on_start_detection(self):
        """Handle start detection request"""
        self.detection_controller.start_detection()

    def _on_stop_detection(self):
        """Handle stop detection request"""
        self.detection_controller.stop_detection()

    def _on_test_sound(self):
        """Handle test sound request"""
        try:
            # Check if device is still available before testing
            if (self.config_model.selected_device_id is not None and 
                not self.audio_model.is_device_available(self.config_model.selected_device_id)):
                self.logger.warning("Selected audio device is no longer available. Refreshing devices.")
                self.refresh_audio_devices()
            
            self.audio_model.test_sound(
                self.config_model.selected_device_id, self.config_model.alert_volume
            )
        except Exception as e:
            self.view.show_error("Sound Test Error", str(e))

    def _on_device_change(self, device_index: int):
        """Handle audio device change"""
        devices = self.audio_model.get_output_devices()
        if 0 <= device_index < len(devices):
            device_id = devices[device_index]["id"]
            device_name = devices[device_index]["name"]
            self.config_model.selected_device_id = device_id
            self.logger.info(f"Audio device changed to: {device_name} (ID: {device_id})")
        else:
            self.logger.warning(f"Invalid device index: {device_index}")
            # Reset to first device if invalid index
            if devices:
                self.config_model.selected_device_id = devices[0]["id"]
                self.view.set_device_options([d["name"] for d in devices], 0)

    def _on_volume_change(self, volume: int):
        """Handle volume change"""
        self.config_model.alert_volume = volume / 100.0



    def _on_always_on_top_change(self, always_on_top: bool):
        """Handle always on top change"""
        self.config_model.always_on_top = always_on_top
        self.view.set_always_on_top(always_on_top)

    def _on_score_threshold_change(self, threshold: float):
        """Handle score threshold change"""
        self.detection_model.set_score_threshold(threshold)



    def _on_closing(self):
        """Handle application closing"""
        self.detection_controller.stop_detection()

    def _on_match_found(self):
        """Handle match found event"""
        pass

    def _on_detection_update(self, img, highest_match, match_score=None):
        """Handle detection update event"""
        if match_score is not None:
            self.view.set_match_percent_and_name(match_score * 100, highest_match)
        pass

    def debug_dota2_windows(self):
        """Debug method to get information about Dota 2 windows"""
        try:
            debug_info = self.detection_model.get_dota2_window_debug_info()
            self.logger.info("=== Dota 2 Window Debug Information ===")
            self.logger.info(f"Processes found: {len(debug_info['processes'])}")
            for proc in debug_info['processes']:
                self.logger.info(f"  - {proc['name']} (PID: {proc['pid']}) - {proc['exe']}")
            
            self.logger.info(f"Windows found: {len(debug_info['windows'])}")
            for window in debug_info['windows']:
                self.logger.info(f"  - {window['title']} (PID: {window['pid']}, Minimized: {window['is_minimized']})")
            
            return debug_info
        except Exception as e:
            self.logger.error(f"Error getting debug info: {e}")
            return None

    def force_focus_dota2(self):
        """Manually trigger Dota 2 window focusing"""
        try:
            success = self.detection_model.focus_dota2_window_enhanced()
            if success:
                self.view.show_info("Window Focus", "Successfully focused Dota 2 window")
            else:
                self.view.show_error("Window Focus", "Failed to focus Dota 2 window")
            return success
        except Exception as e:
            self.view.show_error("Window Focus Error", str(e))
            return False

    def manual_detect_monitor(self):
        """Manually trigger monitor auto-detection"""
        return self._auto_detect_and_set_monitor()

    def run(self):
        """Run the application"""
        self.view.mainloop()
