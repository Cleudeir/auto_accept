import os
import logging
import pygame
import sounddevice as sd
import winsound
import sys
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
    
    def get_output_devices(self) -> List[Dict]:
        """Get list of available audio output devices, filtering by unique name[:10] and only output devices"""
        devices = sd.query_devices()
        output_devices = []
        seen = set()
        for i, d in enumerate(devices):
            # Only include devices that are output devices (not input-only)
            if d["max_output_channels"] > 0 and d["max_input_channels"] == 0:
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
                        # Get raw audio data from pygame Sound
                        arr = pygame.sndarray.array(self.sound)
                        # Apply volume to the audio array
                        arr = (arr * volume).astype(arr.dtype)
                        # Get the sample rate from pygame
                        sample_rate = pygame.mixer.get_init()[0]
                        # Play using sounddevice with selected output device
                        sd.play(arr, samplerate=sample_rate, device=device_id)
                        sd.wait()  # Wait for sound to finish
                        self.logger.info(f"Played alert sound on device {device_id}")
                    except Exception as e:
                        self.logger.error(f"Error playing sound with sounddevice: {e}")
                        # Fallback to pygame's playback
                        self.sound.set_volume(volume)
                        self.sound.play()
                        self.logger.info("Played alert sound with pygame fallback")
                else:
                    # Use pygame's built-in playback
                    self.sound.set_volume(volume)
                    self.sound.play()
                    self.logger.info("Played alert sound with pygame")
            else:
                # Use Windows beep as fallback
                self.logger.warning("Sound not loaded, using fallback beep")
                winsound.Beep(1000, 500)
        except Exception as e:
            self.logger.error(f"Error playing alert sound: {e}")
            try:
                # Ultimate fallback
                winsound.Beep(1000, 500)
            except:
                pass  # If even this fails, just continue silently
    
    def test_sound(self, device_id: Optional[int] = None, volume: float = 1.0):
        """Test the alert sound"""
        self.play_alert_sound(device_id, volume)
