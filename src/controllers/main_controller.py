import os
import mss
import logging
import requests
import threading
import time
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

        self._telegram_session = requests.Session()
        self._last_telegram_sent = 0

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
        self.view.on_test_telegram = self._on_test_telegram
        self.view.on_device_change = self._on_device_change
        self.view.on_volume_change = self._on_volume_change
        self.view.on_always_on_top_change = self._on_always_on_top_change
        self.view.on_closing = self._on_closing

        # Add callback for score threshold changes if the view supports it
        if hasattr(self.view, 'on_score_threshold_change'):
            self.view.on_score_threshold_change = self._on_score_threshold_change

        if hasattr(self.view, 'on_telegram_enabled_change'):
            self.view.on_telegram_enabled_change = self._on_telegram_enabled_change
        if hasattr(self.view, 'on_telegram_bot_token_change'):
            self.view.on_telegram_bot_token_change = self._on_telegram_bot_token_change
        if hasattr(self.view, 'on_telegram_chat_id_change'):
            self.view.on_telegram_chat_id_change = self._on_telegram_chat_id_change
        if hasattr(self.view, 'on_telegram_message_change'):
            self.view.on_telegram_message_change = self._on_telegram_message_change

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

        if hasattr(self.view, 'set_telegram_enabled'):
            self.view.set_telegram_enabled(self.config_model.telegram_enabled)
        if hasattr(self.view, 'set_telegram_bot_token'):
            self.view.set_telegram_bot_token(self.config_model.telegram_bot_token)
        if hasattr(self.view, 'set_telegram_chat_id'):
            self.view.set_telegram_chat_id(self.config_model.telegram_chat_id)
        if hasattr(self.view, 'set_telegram_message'):
            self.view.set_telegram_message(self.config_model.telegram_message)

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

    def _on_test_telegram(self):
        """Handle Telegram test button click"""
        message = self.config_model.telegram_message or "Telegram test message from Dota 2 Auto Accept"
        self._send_telegram_notification(message, force=True)

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

    def _on_telegram_enabled_change(self, enabled: bool):
        self.config_model.telegram_enabled = enabled

    def _on_telegram_bot_token_change(self, bot_token: str):
        self.config_model.telegram_bot_token = bot_token.strip()

    def _on_telegram_chat_id_change(self, chat_id: str):
        self.config_model.telegram_chat_id = chat_id.strip()

    def _on_telegram_message_change(self, message: str):
        self.config_model.telegram_message = message.strip()

    def _send_telegram_notification(self, message: str, force: bool = False):
        """Send a Telegram message asynchronously if configured."""
        if not self.config_model.telegram_enabled and not force:
            return

        bot_token = self.config_model.telegram_bot_token
        chat_id = self.config_model.telegram_chat_id
        if not bot_token:
            if hasattr(self.view, 'show_error'):
                self.view.show_error("Telegram Error", "Bot token is missing.")
            self.logger.warning("Telegram alert is enabled but bot token is missing.")
            return

        if not chat_id:
            chat_id = self._fetch_telegram_chat_id()
            if chat_id:
                self.logger.info(f"Telegram chat ID retrieved automatically: {chat_id}")
            else:
                if hasattr(self.view, 'show_error'):
                    self.view.show_error(
                        "Telegram Error",
                        "Chat ID is missing and could not be retrieved automatically. Envie uma mensagem para o bot e tente novamente."
                    )
                self.logger.warning("Telegram alert is enabled but chat_id is missing and could not be retrieved.")
                return

        now = time.time()
        if now - self._last_telegram_sent < 7:
            self.logger.debug("Skipping Telegram send because cooldown is active.")
            return

        self._last_telegram_sent = now

        def send():
            try:
                self._telegram_session.get(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    params={
                        "chat_id": chat_id,
                        "text": message,
                    },
                    timeout=5,
                )
                self.logger.info("Telegram notification sent.")
            except Exception as e:
                self.logger.warning(f"Telegram send failed: {e}")
                if hasattr(self.view, 'show_error'):
                    self.view.show_error("Telegram Error", str(e))

        threading.Thread(target=send, daemon=True).start()


    def _fetch_telegram_chat_id(self):
        """Fetch chat id from Telegram getUpdates using the bot token."""
        bot_token = self.config_model.telegram_bot_token
        if not bot_token:
            return None

        try:
            response = self._telegram_session.get(
                f"https://api.telegram.org/bot{bot_token}/getUpdates",
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as e:
            self.logger.warning(f"Telegram getUpdates failed: {e}")
            return None

        if not payload.get("ok"):
            self.logger.warning(f"Telegram API returned error: {payload.get('description', 'Unknown error')}")
            return None

        chat_id = self._extract_chat_id_from_updates(payload)
        if chat_id is not None:
            self.config_model.telegram_chat_id = str(chat_id)
            if hasattr(self.view, 'set_telegram_chat_id'):
                self.view.set_telegram_chat_id(str(chat_id))
        return chat_id

    def _extract_chat_id_from_updates(self, payload: dict):
        for update in payload.get("result", []):
            if not isinstance(update, dict):
                continue

            candidates = [
                update.get("message"),
                update.get("edited_message"),
                update.get("channel_post"),
                update.get("edited_channel_post"),
                update.get("callback_query"),
                update.get("inline_query"),
                update.get("chosen_inline_result"),
                update.get("chat_join_request"),
            ]

            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue

                chat = candidate.get("chat") or candidate.get("from")
                if isinstance(chat, dict) and "id" in chat:
                    return chat["id"]

                if "message" in candidate and isinstance(candidate["message"], dict):
                    inner_chat = candidate["message"].get("chat")
                    if isinstance(inner_chat, dict) and "id" in inner_chat:
                        return inner_chat["id"]

        return None

    def _on_closing(self):
        """Handle application closing"""
        self.detection_controller.stop_detection()

    def _on_match_found(self):
        """Handle match found event"""
        self._send_telegram_notification(self.config_model.telegram_message)

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
