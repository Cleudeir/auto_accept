import os
import logging
import pygame
import sounddevice as sd
import sys
import platform
from typing import List, Dict, Optional


class AudioModel:
    """Model for handling audio system and sound playback"""

    def __init__(self):
        self.logger = logging.getLogger("Dota2AutoAccept.AudioModel")
        self.sound = None
        self.sound_loaded = False
        self.initialize_sound_system()

    def initialize_sound_system(self):
        """Initialize the sound system at application startup"""
        try:
            pygame.mixer.init()
            # Use the src directory as base path for bin/dota2.mp3
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            mp3_path = os.path.join(base_path, "bin", "dota2.mp3")
            if os.path.exists(mp3_path):
                self.sound = pygame.mixer.Sound(mp3_path)
                self.sound_loaded = True
                self.logger.info(f"Sound system initialized successfully: {mp3_path}")
            else:
                self.logger.warning(f"Alert sound file not found at {mp3_path}")
        except Exception as e:
            self.logger.error(f"Error initializing sound system: {e}")

    def get_default_output_device(self) -> Optional[Dict]:
        """Get the system default output device"""
        try:
            default_device = sd.query_devices(kind="output")
            if default_device and default_device.get("max_output_channels", 0) > 0:
                devices = sd.query_devices()
                for i, d in enumerate(devices):
                    if d["name"] == default_device["name"]:
                        return {"id": i, "name": d["name"]}
            return None
        except Exception as e:
            self.logger.error(f"Error getting default output device: {e}")
            return None

    def get_output_devices(self) -> List[Dict]:
        """Get list of available audio output devices, filtering by unique name[:10] and only output devices"""
        devices = sd.query_devices()
        output_devices = []
        seen = set()

        # First, try to add the system default device at the top
        default_device = self.get_default_output_device()
        if default_device:
            output_devices.append(
                {
                    "id": default_device["id"],
                    "name": f"🔊 {default_device['name']} (Default)",
                }
            )
            seen.add(default_device["name"][:10])

        for i, d in enumerate(devices):
            # Include any device that has output capabilities (regardless of input capabilities)
            if d["max_output_channels"] > 0:
                name_slice = d["name"][:10]
                if name_slice not in seen:
                    output_devices.append({"id": i, "name": d["name"]})
                    seen.add(name_slice)
        return output_devices

    def play_alert_sound(self, device_id: Optional[int] = None, volume: float = 1.0):
        """Play the alert sound using the configured settings"""
        try:
            if self.sound_loaded and self.sound is not None:
                # If using a specific device and sounddevice (sd)
                if device_id is not None:
                    try:
                        # Validate device exists and has output capabilities
                        devices = sd.query_devices()
                        if (
                            device_id < len(devices)
                            and devices[device_id].get("max_output_channels", 0) > 0
                        ):
                            # Get raw audio data from pygame Sound
                            arr = pygame.sndarray.array(self.sound)
                            # Apply volume to the audio array
                            arr = (arr * volume).astype(arr.dtype)
                            # Get the sample rate from pygame
                            sample_rate = pygame.mixer.get_init()[0]
                            # Play using sounddevice with selected output device
                            sd.play(arr, samplerate=sample_rate, device=device_id)
                            sd.wait()  # Wait for sound to finish
                            self.logger.info(
                                f"Played alert sound on device {device_id} ({devices[device_id]['name']})"
                            )
                        else:
                            self.logger.warning(
                                f"Invalid device ID {device_id}, falling back to default"
                            )
                            # Fallback to pygame's playback
                            self.sound.set_volume(volume)
                            self.sound.play()
                            self.logger.info("Played alert sound with pygame fallback")
                    except Exception as e:
                        self.logger.error(
                            f"Error playing sound with sounddevice on device {device_id}: {e}"
                        )
                        # Fallback to pygame's playback
                        self.sound.set_volume(volume)
                        self.sound.play()
                        self.logger.info("Played alert sound with pygame fallback")
                else:
                    # Use pygame's built-in playback (system default)
                    self.sound.set_volume(volume)
                    self.sound.play()
                    self.logger.info("Played alert sound with pygame (system default)")
            else:
                # Use cross-platform beep as fallback
                self.logger.warning("Sound not loaded, using fallback beep")
                self._play_fallback_beep()
        except Exception as e:
            self.logger.error(f"Error playing alert sound: {e}")
            try:
                # Ultimate fallback
                self._play_fallback_beep()
            except:
                pass  # If even this fails, just continue silently

    def refresh_devices(self):
        """Refresh the list of available audio devices"""
        try:
            # This will query the system for current devices
            devices = sd.query_devices()
            self.logger.info(f"Refreshed audio devices: {len(devices)} devices found")
            return True
        except Exception as e:
            self.logger.error(f"Error refreshing audio devices: {e}")
            return False

    def is_device_available(self, device_id: int) -> bool:
        """Check if a specific device ID is currently available"""
        try:
            devices = sd.query_devices()
            return (
                device_id < len(devices)
                and devices[device_id].get("max_output_channels", 0) > 0
            )
        except Exception as e:
            self.logger.error(f"Error checking device availability: {e}")
            return False

    def test_sound(self, device_id: Optional[int] = None, volume: float = 1.0):
        """Test the alert sound"""
        self.play_alert_sound(device_id, volume)

    def _play_fallback_beep(self):
        """Play a cross-platform fallback beep sound"""
        try:
            if platform.system() == "Windows":
                import winsound

                winsound.Beep(1000, 500)
            else:
                # For Linux/Unix systems, use system bell or print beep
                try:
                    os.system('printf "\a"')
                except:
                    # If all else fails, just log the beep
                    self.logger.info("BEEP! (Alert sound fallback)")
        except Exception as e:
            self.logger.error(f"Error playing fallback beep: {e}")
