import os
import mss
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
        # Initialize models
        self.config_model = ConfigModel()
        self.audio_model = AudioModel()
        self.screenshot_model = ScreenshotModel()
        self.detection_model = DetectionModel()

        # Initialize controllers
        self.detection_controller = DetectionController(
            self.detection_model,
            self.screenshot_model,
            self.audio_model,
            self.config_model,
        )

        # Initialize view
        self.view = MainView()

        # Setup callbacks
        self._setup_callbacks()

        # Initialize UI
        self._initialize_ui()

        # Setup periodic updates
        self._setup_periodic_updates()

    def _setup_callbacks(self):
        """Setup callbacks between controllers and views"""
        # View callbacks
        self.view.on_start_detection = self._on_start_detection
        self.view.on_stop_detection = self._on_stop_detection
        self.view.on_test_sound = self._on_test_sound
        self.view.on_take_screenshot = self._on_take_screenshot
        self.view.on_device_change = self._on_device_change
        self.view.on_volume_change = self._on_volume_change
        self.view.on_monitor_change = self._on_monitor_change
        self.view.on_always_on_top_change = self._on_always_on_top_change
        self.view.on_closing = self._on_closing

        # Detection controller callbacks
        self.detection_controller.on_match_found = self._on_match_found
        self.detection_controller.on_detection_update = self._on_detection_update

    def _initialize_ui(self):
        """Initialize UI with current settings"""
        self.view.create_window()

        # Setup audio devices
        devices = self.audio_model.get_output_devices()
        device_names = [d["name"] for d in devices]
        selected_device_index = 0

        if devices and self.config_model.selected_device_id is not None:
            for i, d in enumerate(devices):
                if d["id"] == self.config_model.selected_device_id:
                    selected_device_index = i
                    break

        self.view.set_device_options(device_names, selected_device_index)

        # Start detection automatically when app starts
        self.detection_controller.start_detection()

        # Setup monitors
        monitors = self.screenshot_model.get_available_monitors()
        monitor_names = [m[0] for m in monitors]
        selected_monitor_index = 0

        if monitors:
            for i, (_, monitor_id) in enumerate(monitors):
                if monitor_id == self.config_model.selected_monitor_capture_setting:
                    selected_monitor_index = i
                    break

        self.view.set_monitor_options(monitor_names, selected_monitor_index)

        # Setup other settings
        self.view.set_volume(int(self.config_model.alert_volume * 100))
        self.view.set_always_on_top(self.config_model.always_on_top)

        # Position window on second monitor if available
        self._position_window_on_second_monitor()

    def _position_window_on_second_monitor(self):
        """Position the window on the second monitor if available"""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                if len(monitors) > 2:  # At least two physical monitors
                    second_monitor = monitors[2]

                    # Calculate center position on second monitor
                    window_width = 420
                    window_height = 850
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

        # Schedule next update
        self.view.after(500, self._update_status)

    def _update_screenshot_preview(self):
        """Update screenshot preview in UI"""
        img, timestamp = self.screenshot_model.get_latest_screenshot()
        self.view.update_screenshot(img, timestamp)

        # Schedule next update
        self.view.after(1000, self._update_screenshot_preview)

    # Event handlers
    def _on_start_detection(self):
        """Handle start detection request"""
        if self.detection_controller.start_detection():
            pass

    def _on_stop_detection(self):
        """Handle stop detection request"""
        if self.detection_controller.stop_detection():
            pass

    def _on_test_sound(self):
        """Handle test sound request"""
        try:
            self.audio_model.test_sound(
                self.config_model.selected_device_id, self.config_model.alert_volume
            )
        except Exception as e:
            self.view.show_error("Sound Test Error", str(e))

    def _on_take_screenshot(self):
        """Handle manual screenshot request"""
        img = self.screenshot_model.capture_monitor_screenshot(
            self.config_model.selected_monitor_capture_setting
        )
        if img is not None:
            pass
        else:
            self.view.show_error("Screenshot Error", "Failed to capture screenshot")

    def _on_device_change(self, device_index: int):
        """Handle audio device change"""
        devices = self.audio_model.get_output_devices()
        if 0 <= device_index < len(devices):
            device_id = devices[device_index]["id"]
            self.config_model.selected_device_id = device_id

    def _on_volume_change(self, volume: int):
        """Handle volume change"""
        self.config_model.alert_volume = volume / 100.0

    def _on_monitor_change(self, monitor_index: int):
        """Handle monitor change"""
        monitors = self.screenshot_model.get_available_monitors()
        if 0 <= monitor_index < len(monitors):
            monitor_id = monitors[monitor_index][1]
            self.config_model.selected_monitor_capture_setting = monitor_id

    def _on_always_on_top_change(self, always_on_top: bool):
        """Handle always on top change"""
        self.config_model.always_on_top = always_on_top
        self.view.set_always_on_top(always_on_top)

    def _on_closing(self):
        """Handle application closing"""
        self.detection_controller.stop_detection()

    def _on_match_found(self):
        """Handle match found event"""
        pass

    def _on_detection_update(self, img, highest_match, match_score=None):
        """Handle detection update event"""
        # Update match percent and name in the view if score is provided
        if match_score is not None:
            self.view.set_match_percent_and_name(match_score * 100, highest_match)
        # This is called frequently during detection, so we don't log it
        pass

    def run(self):
        """Run the application"""
        self.view.mainloop()
