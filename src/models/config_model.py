import os
import json
import logging

class ConfigModel:
    """Model for handling application configuration"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger("Dota2AutoAccept.ConfigModel")
        self._config = self._load_default_config()
        self.load()
    
    def _load_default_config(self):
        """Load default configuration values"""
        return {
            "alert_volume": 1.0,
            "selected_device_id": None,
            "selected_monitor_capture_setting": 1,
            "always_on_top": False,
            "enhanced_window_focus": True,
            "auto_focus_on_detection": True,
            "focus_retry_attempts": 3,
            "focus_delay_ms": 150  # Slightly longer delay for better reliability
        }
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    # Update config with loaded values, keeping defaults for missing keys
                    for key, value in data.items():
                        if key in self._config:
                            # Validate monitor setting
                            if key == "selected_monitor_capture_setting":
                                if isinstance(value, int) and value > 0:
                                    self._config[key] = value
                                else:
                                    self.logger.warning(
                                        f"Invalid monitor setting '{value}' in config. Using default."
                                    )
                            else:
                                self._config[key] = value
                self.logger.info("Configuration loaded successfully")
            else:
                self.logger.info(f"Config file {self.config_file} not found. Using defaults.")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}. Using defaults.")
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save"""
        if key in self._config:
            self._config[key] = value
            self.save()
            self.logger.info(f"Config updated: {key} = {value}")
        else:
            self.logger.warning(f"Unknown config key: {key}")
    
    def get_all(self):
        """Get all configuration as dictionary"""
        return self._config.copy()
    
    @property
    def alert_volume(self):
        return self._config["alert_volume"]
    
    @alert_volume.setter
    def alert_volume(self, value):
        self.set("alert_volume", float(value))
    
    @property
    def selected_device_id(self):
        return self._config["selected_device_id"]
    
    @selected_device_id.setter
    def selected_device_id(self, value):
        self.set("selected_device_id", value)
    
    @property
    def selected_monitor_capture_setting(self):
        return self._config["selected_monitor_capture_setting"]
    
    @selected_monitor_capture_setting.setter
    def selected_monitor_capture_setting(self, value):
        self.set("selected_monitor_capture_setting", int(value))
    
    @property
    def always_on_top(self):
        return self._config["always_on_top"]
    
    @always_on_top.setter
    def always_on_top(self, value):
        self.set("always_on_top", bool(value))

    @property
    def enhanced_window_focus(self):
        return self._config.get("enhanced_window_focus", True)
    
    @enhanced_window_focus.setter
    def enhanced_window_focus(self, value):
        self.set("enhanced_window_focus", bool(value))

    @property
    def auto_focus_on_detection(self):
        return self._config.get("auto_focus_on_detection", True)
    
    @auto_focus_on_detection.setter
    def auto_focus_on_detection(self, value):
        self.set("auto_focus_on_detection", bool(value))

    @property
    def focus_retry_attempts(self):
        return self._config.get("focus_retry_attempts", 3)
    
    @focus_retry_attempts.setter
    def focus_retry_attempts(self, value):
        self.set("focus_retry_attempts", int(value))

    @property
    def focus_delay_ms(self):
        return self._config.get("focus_delay_ms", 100)
    
    @focus_delay_ms.setter
    def focus_delay_ms(self, value):
        self.set("focus_delay_ms", int(value))
