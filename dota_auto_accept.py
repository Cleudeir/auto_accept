import pyautogui
import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import os
import sys
import win32gui
from screeninfo import get_monitors
import pygame
import sounddevice as sd
import json
# Add pycaw imports for volume control
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import comtypes
    from ctypes import cast, POINTER
    pycaw_available = True
except ImportError:
    pycaw_available = False


class DotaAutoAccept:
    def __init__(self, root):
        self.root = root
        self.root.title("Dota 2 Auto Accept")
        self.root.geometry("520x420")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a2e')

        self.reference_image_path = self.resource_path("dota.png")
        self.reference_image = cv2.imread(
            self.reference_image_path, cv2.IMREAD_COLOR)

        self.reference_image_plus_path = self.resource_path("dota2-plus.jpeg")
        self.reference_image_plus = cv2.imread(
            self.reference_image_plus_path, cv2.IMREAD_COLOR)

        if self.reference_image is None and self.reference_image_plus is None:
            messagebox.showerror(
                "Error", f"Reference images not found: {
                    self.reference_image_path} and {
                    self.reference_image_plus_path}")
            sys.exit(1)

        self.running = False
        self.start_button = None
        self.stop_button = None

        # Audio system variables
        self.audio_devices = []
        self.selected_device_id = None
        self.settings_file = self.resource_path("audio_settings.json")
        self.pygame_initialized = False        # Initialize alert volume
        self.alert_volume = 1.0  # Default to 100%
        self.volume_settings_file = self.resource_path("alert_volume.json")
        self.load_volume_setting()
        
        # Monitor info
        self.monitors = []
        self.load_monitors()

        # Initialize audio system
        self.init_audio_system()
        self.load_audio_settings()

        self.setup_ui()

    def load_volume_setting(self):
        try:
            if os.path.exists(self.volume_settings_file):
                with open(self.volume_settings_file, 'r') as f:
                    data = json.load(f)
                    self.alert_volume = float(data.get('alert_volume', 1.0))
        except Exception:
            self.alert_volume = 1.0

    def save_volume_setting(self):
        try:
            with open(self.volume_settings_file, 'w') as f:
                json.dump({'alert_volume': self.alert_volume}, f)
        except Exception:
            pass

    def _normalize_device_name(self, name):
        # Use only the first 12 characters, lowercase, and remove extra spaces
        # for duplicate detection
        name = name.lower()
        name = name[:12]
        name = ' '.join(name.split())
        return name.strip()

    def init_audio_system(self):
        """Initialize the audio system and discover only active output devices, removing similar duplicates by first 12 chars"""
        try:
            # Get available audio output devices
            devices = sd.query_devices()
            self.audio_devices = []
            seen_normalized = set()
            for i, device in enumerate(devices):
                # Filter for active output devices only
                if (device['max_output_channels'] > 0 and
                    device['hostapi'] >= 0 and
                        device['default_samplerate'] > 0):
                    device_name = device['name'].strip()
                    # Skip devices that are typically inactive or cause issues
                    skip_keywords = [
                        'communications',
                        'comm',
                        'recording',
                        'input',
                        'line in',
                        'microphone']
                    if any(keyword in device_name.lower()
                           for keyword in skip_keywords):
                        continue
                    norm_name = self._normalize_device_name(device_name)
                    if norm_name in seen_normalized:
                        continue
                    # Check if device is actually available by trying to query
                    # it
                    try:
                        sd.check_output_settings(
                            device=i, channels=1, samplerate=44100)
                        self.audio_devices.append({
                            'id': i,
                            'name': device_name,
                            'channels': device['max_output_channels'],
                            'samplerate': device['default_samplerate']
                        })
                        seen_normalized.add(norm_name)
                        print(f"Active output device found: {device_name}")
                    except Exception:
                        continue
            print(
                f"Found {len(self.audio_devices)} active audio output devices (no similar duplicates by first 12 chars)")

            # Set default device if none selected
            if not self.selected_device_id and self.audio_devices:
                try:
                    # Default output device
                    default_output = sd.default.device[1]
                    # Check if default device is in our filtered list
                    for device in self.audio_devices:
                        if device['id'] == default_output:
                            self.selected_device_id = default_output
                            print(
                                f"Using system default device: {
                                    device['name']}")
                            break
                    # If default not found, use first available device
                    if self.selected_device_id is None:
                        self.selected_device_id = self.audio_devices[0]['id']
                        print(
                            f"Using first available device: {
                                self.audio_devices[0]['name']}")
                except Exception:
                    if self.audio_devices:
                        self.selected_device_id = self.audio_devices[0]['id']
                        print(
                            f"Using first available device: {
                                self.audio_devices[0]['name']}")

        except Exception as e:
            print(f"Error initializing audio system: {e}")
            messagebox.showwarning(
                "Audio Warning",
                f"Could not initialize audio system: {e}")

    def load_audio_settings(self):
        """Load saved audio settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    saved_device_id = settings.get('selected_device_id')

                    # Validate that the saved device still exists in our active
                    # devices list
                    if saved_device_id is not None:
                        for device in self.audio_devices:
                            if device['id'] == saved_device_id:
                                self.selected_device_id = saved_device_id
                                print(
                                    f"Loaded saved audio device: {
                                        device['name']}")
                                return
                        print("Saved audio device no longer available, using default")

        except Exception as e:
            print(f"Error loading audio settings: {e}")

    def save_audio_settings(self):
        """Save audio settings to file"""
        try:
            settings = {
                'selected_device_id': self.selected_device_id
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)

            # Find device name for logging
            device_name = "Unknown"
            for device in self.audio_devices:
                if device['id'] == self.selected_device_id:
                    device_name = device['name']
                    break

            print(
                f"Saved audio device: {device_name} (ID: {
                    self.selected_device_id})")
        except Exception as e:
            print(f"Error saving audio settings: {e}")

    def on_device_change(self, event=None):
        """Handle audio device selection change"""
        if hasattr(self, 'device_combo') and self.device_combo:
            selected_idx = self.device_combo.current()
            if 0 <= selected_idx < len(self.audio_devices):
                self.selected_device_id = self.audio_devices[selected_idx]['id']
                self.save_audio_settings()
                print(
                    f"Audio device changed to: {
                        self.audio_devices[selected_idx]['name']}")

                # Test the new device
                self.test_audio_device()

    def set_device_volume(self, vol):
        """Set the selected audio device's volume to vol (0.0-1.0) using pycaw. Returns previous volume or None."""
        if not pycaw_available:
            print("pycaw not available, cannot set device volume programmatically.")
            return None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            prev_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(vol, None)
            print(
                f"Set system default output device volume to {
                    vol:.2f}, previous was {
                    prev_vol:.2f}")
            return prev_vol
        except Exception as e:
            print(f"Failed to set device volume: {e}")
            return None

    def restore_device_volume(self, prev_vol):
        """Restore the system default output device volume to previous value using pycaw."""
        if not pycaw_available or prev_vol is None:
            return
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(prev_vol, None)
            print(
                f"Restored system default output device volume to {
                    prev_vol:.2f}")
        except Exception as e:
            print(f"Failed to restore device volume: {e}")

    def stop_other_audio(self):
        """Stop all other audio sessions except this process (using pycaw, Windows only)."""
        if not pycaw_available:
            return
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.pid != os.getpid():
                    try:
                        session.SimpleAudioVolume.SetMute(1, None)
                        print(f"Muted audio session: {session.Process.name()}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Failed to mute other audio sessions: {e}")

    def unmute_other_audio(self):
        """Unmute all audio sessions previously muted (using pycaw, Windows only)."""
        if not pycaw_available:
            return
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.pid != os.getpid():
                    try:
                        session.SimpleAudioVolume.SetMute(0, None)
                        print(
                            f"Unmuted audio session: {
                                session.Process.name()}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Failed to unmute other audio sessions: {e}")

    def test_audio_device(self):
        """Test the selected audio device with the dota2.mp3 file or a 3s beep, using user volume and pausing other audio."""
        prev_vol = None
        try:
            prev_vol = self.set_device_volume(self.alert_volume)
            self.stop_other_audio()
            if self.selected_device_id is not None:
                mp3_path = self.resource_path("dota2.mp3")
                if os.path.exists(mp3_path):
                    try:
                        if not self.pygame_initialized:
                            pygame.mixer.init(
                                frequency=44100, size=-16, channels=2, buffer=512)
                            self.pygame_initialized = True
                        sound = pygame.mixer.Sound(mp3_path)
                        sound_array = pygame.sndarray.array(sound)
                        if sound_array.dtype != np.float32:
                            if sound_array.dtype == np.int16:
                                sound_array = sound_array.astype(
                                    np.float32) / 32768.0
                            else:
                                sound_array = sound_array.astype(np.float32)
                        sample_rate = pygame.mixer.get_init()[0]
                        test_length = min(sample_rate * 3, len(sound_array))
                        test_audio = sound_array[:test_length] * 0.8
                        sd.play(
                            test_audio,
                            samplerate=sample_rate,
                            device=self.selected_device_id)
                        sd.wait()
                        print("Audio test successful using dota2.mp3 (3s)")
                        return
                    except Exception as mp3_error:
                        print(
                            f"MP3 test failed: {mp3_error}, using fallback beep")
                sample_rate = 44100
                duration = 3.0
                freq = 800
                t = np.linspace(
                    0, duration, int(
                        sample_rate * duration), False)
                tone = (np.sin(2 * np.pi * freq * t) * 0.3).astype(np.float32)
                sd.play(
                    tone,
                    samplerate=sample_rate,
                    device=self.selected_device_id)
                sd.wait()
                print("Audio test successful using fallback beep (3s)")
        except Exception as e:
            print(f"Audio test failed: {e}")
            messagebox.showwarning(
                "Audio Test", f"Failed to test audio device: {e}")
        finally:
            self.restore_device_volume(prev_vol)
            self.unmute_other_audio()

    def play_high_beep(self):
        """Play dota2.mp3 sound using the selected audio device at user-defined volume, then restore previous volume and unmute others."""
        prev_vol = None
        try:
            prev_vol = self.set_device_volume(self.alert_volume)
            self.stop_other_audio()
            if self.selected_device_id is None:
                print("No audio device selected, using fallback")
                self.play_fallback_beep()
                return
            mp3_path = self.resource_path("dota2.mp3")
            if not os.path.exists(mp3_path):
                print("dota2.mp3 not found, using fallback beep")
                self.play_fallback_beep()
                return
            if not self.pygame_initialized:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512)
                self.pygame_initialized = True
            sound = pygame.mixer.Sound(mp3_path)
            sound_array = pygame.sndarray.array(sound)
            if sound_array.dtype != np.float32:
                if sound_array.dtype == np.int16:
                    sound_array = sound_array.astype(np.float32) / 32768.0
                elif sound_array.dtype == np.int32:
                    sound_array = sound_array.astype(np.float32) / 2147483648.0
                else:
                    sound_array = sound_array.astype(np.float32)
            max_val = np.max(np.abs(sound_array))
            if max_val > 0:
                sound_array = sound_array / max_val
            sample_rate = pygame.mixer.get_init()[0]
            print(
                f"Playing dota2.mp3 at user volume {
                    self.alert_volume:.2f} on device {
                    self.selected_device_id}")
            sd.play(
                sound_array,
                samplerate=sample_rate,
                device=self.selected_device_id)
            sd.wait()
            print("dota2.mp3 played successfully at user volume")
        except Exception as e:
            print(f"Error playing dota2.mp3: {e}")
            self.play_fallback_beep()
        finally:
            self.restore_device_volume(prev_vol)
            self.unmute_other_audio()

    def play_fallback_beep(self):
        """Fallback beep using pygame mixer - try MP3 first, then generated beep"""
        try:
            if not self.pygame_initialized:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512)
                self.pygame_initialized = True

            # Try to play dota2.mp3 first
            mp3_path = self.resource_path("dota2.mp3")
            if os.path.exists(mp3_path):
                try:
                    pygame.mixer.music.load(mp3_path)
                    pygame.mixer.music.set_volume(1.0)  # Maximum volume
                    pygame.mixer.music.play()
                    print("Fallback: dota2.mp3 played using pygame")
                    return
                except Exception as mp3_error:
                    print(f"Failed to play MP3 in fallback: {mp3_error}")
              # If MP3 fails, generate a 1kHz beep for 300ms
            sample_rate = 44100
            duration = 0.3
            freq = 1000
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = (
                np.sin(
                    2 *
                    np.pi *
                    freq *
                    t) *
                32767 *
                1.0).astype(
                np.int16)  # Maximum volume
            sound = pygame.sndarray.make_sound(tone)
            sound.set_volume(1.0)  # Maximum volume
            sound.play()
            print("Fallback beep played at maximum volume")
        except Exception as e:
            print(f"Error playing fallback beep: {e}")

    def get_dota_monitor(self):
        try:
            # Print all available monitors first
            print("\n----- MONITOR DETECTION DEBUG -----")
            monitors = get_monitors()
            print(f"Found {len(monitors)} monitors:")
            for i, m in enumerate(monitors):
                is_primary = " (PRIMARY)" if hasattr(
                    m, 'is_primary') and m.is_primary else ""
                print(
                    f"  Monitor {i}: {m.name}{is_primary} - Position: ({m.x}, {m.y}) - Size: {m.width}x{m.height}")

            # Find Dota 2 window
            hwnd = win32gui.FindWindow(None, "Dota 2")
            if hwnd == 0:
                print(
                    "Dota 2 window not found. Make sure the game is running and the window title is 'Dota 2'.")
                return None

            # Get window position and size
            rect = win32gui.GetWindowRect(hwnd)
            window_x, window_y, window_right, window_bottom = rect
            window_width = window_right - window_x
            window_height = window_bottom - window_y
            print(
                f"Dota 2 window found at: ({window_x}, {window_y}) - Size: {window_width}x{window_height}")

            # Check which monitor contains the Dota 2 window
            print("Checking which monitor contains the Dota 2 window:")
            for i, monitor in enumerate(monitors):
                # Calculate monitor boundaries
                monitor_left = monitor.x
                monitor_right = monitor.x + monitor.width
                monitor_top = monitor.y
                monitor_bottom = monitor.y + monitor.height

                # Check if window is within this monitor (use window top-left
                # corner as reference)
                is_in_monitor = (monitor_left <= window_x < monitor_right and
                                 monitor_top <= window_y < monitor_bottom)

                # Print detailed check information
                print(f"  Monitor {i} check: window ({window_x}, {window_y}) in bounds " +
                      f"({monitor_left}-{monitor_right}, {monitor_top}-{monitor_bottom})? " +
                      f"{'YES' if is_in_monitor else 'NO'}")

                if is_in_monitor:
                    print(f"➤ Dota 2 found on monitor {i}: {monitor.name}")
                    print(
                        f"➤ Using screenshot region: ({
                            monitor.x}, {
                            monitor.y}, {
                            monitor.width}, {
                            monitor.height})")
                    print("----- END MONITOR DETECTION -----\n")
                    return (monitor.x, monitor.y,
                            monitor.width, monitor.height)

            # If we get here, we couldn't find the monitor
            print("❌ Could not determine the monitor for Dota 2 window.")
            print(
                "   Window might be outside all monitor boundaries or partially visible.")
            print("----- END MONITOR DETECTION -----\n")
            return None
        except Exception as e:
            print(f"❌ Error finding Dota 2 window/monitor: {e}")
            print("----- END MONITOR DETECTION -----\n")
            return None

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def find_and_press_enter(self):
        confidence = 0.6
        reference_gray = None
        reference_plus_gray = None
        if self.reference_image is not None:
            reference_gray = cv2.cvtColor(
                self.reference_image, cv2.COLOR_BGR2GRAY)
            print(
                f"Loaded reference image 'dota.png': {
                    self.reference_image.shape[1]}x{
                    self.reference_image.shape[0]}")
        if self.reference_image_plus is not None:            reference_plus_gray = cv2.cvtColor(
                self.reference_image_plus, cv2.COLOR_BGR2GRAY)
                
        print(
                f"Loaded reference image 'dota2-plus.jpeg': {
                    self.reference_image_plus.shape[1]}x{
                    self.reference_image_plus.shape[0]}")

        print(f"Template matching confidence threshold: {confidence}")
        monitor_printed = False
        
        while self.running:
            try:                # Use automatic monitor detection
                dota_monitor = self.get_dota_monitor()
                if dota_monitor is None:
                    print("⚠️ Dota 2 window not found. Will keep checking...")
                    if hasattr(self, 'monitor_info_label') and self.monitor_info_label:
                        self.monitor_info_label.config(text="Waiting for Dota 2...")
                    time.sleep(3)  # Wait a bit before trying again
                    continue
                    
                # Get monitor coordinates from detection
                left, top, width, height = dota_monitor
                
                # Print monitor info
                if not monitor_printed:
                    print(f"\n----- USING DETECTED DOTA 2 MONITOR -----")
                    print(f"Position: ({left}, {top}) - Size: {width}x{height}")
                    print("----- END MONITOR INFO -----\n")
                    
                    print(f"\n----- SCREENSHOT DEBUG -----")
                    print(f"Taking screenshot of region: ({left}, {top}, {width}, {height})")
                    monitor_printed = True
                    
                    # Update the monitor info label with detected monitor
                    if hasattr(self, 'monitor_info_label') and self.monitor_info_label:
                        monitor_idx = next((i for i, m in enumerate(self.monitors) 
                                           if m.x == left and m.y == top and m.width == width and m.height == height), -1)
                        if monitor_idx >= 0:
                            monitor = self.monitors[monitor_idx]
                            is_primary = " (PRIMARY)" if hasattr(monitor, 'is_primary') and monitor.is_primary else ""
                            self.monitor_info_label.config(
                                text=f"Using Monitor {monitor_idx}{is_primary}: {monitor.name} - Position: ({left}, {top})"
                            )

                screenshot = pyautogui.screenshot(
                    region=(left, top, width, height))
                screenshot_np = cv2.cvtColor(
                    np.array(screenshot), cv2.COLOR_RGB2BGR)
                screenshot_gray = cv2.cvtColor(
                    screenshot_np, cv2.COLOR_BGR2GRAY)

                # Debug screenshot dimensions
                if not monitor_printed:
                    print(
                        f"Screenshot dimensions: {
                            screenshot_np.shape[1]}x{
                            screenshot_np.shape[0]}")
                    print("----- END SCREENSHOT DEBUG -----\n")

                # Template matching
                found = False
                max_val = 0
                max_val1 = 0
                max_val2 = 0
                max_loc1 = None
                max_loc2 = None

                # Check dota.png
                if reference_gray is not None:
                    result = cv2.matchTemplate(
                        screenshot_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
                    _, max_val1, _, max_loc1 = cv2.minMaxLoc(result)
                    if max_val1 >= confidence:
                        found = True
                        max_val = max_val1

                # Check dota2-plus.png
                if not found and reference_plus_gray is not None:
                    result_plus = cv2.matchTemplate(
                        screenshot_gray, reference_plus_gray, cv2.TM_CCOEFF_NORMED)
                    _, max_val2, _, max_loc2 = cv2.minMaxLoc(result_plus)
                    if max_val2 >= confidence:
                        found = True
                        max_val = max_val2                # Update UI with detection information
                monitor_index = next((i for i, m in enumerate(get_monitors())
                                      if m.x == left and m.y == top and m.width == width and m.height == height), -1)
                monitor_type = "PRIMARY" if monitor_index == 0 else f"SECONDARY #{monitor_index}"
                monitor_info = f"Monitor: {monitor_type} ({width}x{height})"
                if self.analysis_label:
                    self.analysis_label.config(
                        text=f"{monitor_info} | dota.png={
                            max_val1:.3f} | dota2-plus.jpeg={
                            max_val2:.3f}"
                    )

                # Print detection debug info every few seconds (not every frame
                # to avoid log spam)
                if time.time() % 5 < 0.1:  # Print roughly every 5 seconds
                    print(f"\n----- DETECTION DEBUG -----")
                    print(
                        f"Monitoring region: ({left}, {top}, {width}, {height})")
                    monitor_idx = next((i for i, m in enumerate(get_monitors())
                                        if m.x == left and m.y == top and m.width == width and m.height == height), -1)
                    print(
                        f"Current monitor: #{monitor_idx} - {'PRIMARY' if monitor_idx == 0 else 'SECONDARY'}")
                    print(
                        f"Current confidence values: dota.png={
                            max_val1:.3f}, dota2-plus.jpeg={
                            max_val2:.3f}")
                    if max_loc1:
                        print(
                            f"Best match for dota.png at position: {max_loc1} (relative to monitor)")
                        print(
                            f"  Absolute position: ({
                                left +
                                max_loc1[0]}, {
                                top +
                                max_loc1[1]})")
                    if max_loc2:
                        print(
                            f"Best match for dota2-plus.jpeg at position: {max_loc2} (relative to monitor)")
                        print(
                            f"  Absolute position: ({
                                left +
                                max_loc2[0]}, {
                                top +
                                max_loc2[1]})")
                    print(f"Detection threshold: {confidence}")
                    # Save a debug screenshot periodically to help troubleshoot
                    # detection
                    print("----- END DETECTION DEBUG -----\n")
                if time.time() % 30 < 0.1:  # Every 30 seconds
                    monitor_idx = next((i for i, m in enumerate(get_monitors())
                                        if m.x == left and m.y == top and m.width == width and m.height == height), -1)
                    monitor_type = "PRIMARY" if monitor_index == 0 else f"SECONDARY_{monitor_index}"

                    # Save the current monitor screenshot
                    debug_filename = f"dota_monitor_{monitor_type}_confidence_{
                        max_val1:.3f}_{
                        max_val2:.3f}.png"
                    self.save_debug_screenshot(screenshot_np, debug_filename)
                    print(f"📸 Debug screenshot saved: {debug_filename}")

                    # Also save grayscale version with matches highlighted
                    debug_vis = cv2.cvtColor(
                        screenshot_gray, cv2.COLOR_GRAY2BGR)
                    if max_loc1 and reference_gray is not None:
                        h, w = reference_gray.shape
                        top_left = max_loc1
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        cv2.rectangle(
                            debug_vis, top_left, bottom_right, (0, 255, 0), 2)
                        cv2.putText(debug_vis, f"{max_val1:.3f}", (top_left[0], top_left[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    if max_loc2 and reference_plus_gray is not None:
                        h, w = reference_plus_gray.shape
                        top_left = max_loc2
                        bottom_right = (top_left[0] + w, top_left[1] + h)
                        cv2.rectangle(
                            debug_vis, top_left, bottom_right, (0, 0, 255), 2)
                        cv2.putText(debug_vis, f"{max_val2:.3f}", (top_left[0], top_left[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                    vis_filename = f"dota_monitor_{monitor_type}_matches_highlighted.png"
                    self.save_debug_screenshot(debug_vis, vis_filename)
                    print(f"📸 Highlighted matches saved: {vis_filename}")

                if found:
                    print(
                        f"✅ Detected ACCEPT screen! Confidence: {
                            max_val:.3f}")
                    repeat_count = 2
                    for i in range(repeat_count):
                        self.play_high_beep()
                        pyautogui.press('enter')
                        print(
                            f"Match Accepted! (Attempt {
                                i + 1}/{repeat_count})")
                        if i < repeat_count - 1:
                            time.sleep(3)
                    time.sleep(5)
                    self.stop_script()
                    return
            except Exception as e:
                print(f"❌ Error in detection: {e}")
                import traceback
                traceback.print_exc()

            time.sleep(1)
            
    def start_script(self):
        # Check for Dota 2 window before starting
        if self.get_dota_monitor() is None:
            messagebox.showwarning(
                "Warning", "Dota 2 window not found. Please start Dota 2.")
            return  # Don't start if Dota 2 isn't running

        if not self.running:
            self.running = True
            if self.analysis_label:
                self.analysis_label.config(text="Waiting for analysis...")
            threading.Thread(
                target=self.find_and_press_enter,
                daemon=True).start()
            self.status_label.config(text="● Running...", fg="#00d4aa")
            self.start_button.pack_forget()
            self.stop_button.pack(side=tk.LEFT, padx=10)

    def stop_script(self):
        self.running = False
        self.status_label.config(text="● Stopped", fg="#ff6b6b")
        if self.analysis_label:
            self.analysis_label.config(text="")
        self.stop_button.pack_forget()
        self.start_button.pack(side=tk.LEFT, padx=10)

    def init_monitors(self):
        """Initialize the list of available monitors"""
        try:
            self.monitors = get_monitors()
            print(f"Found {len(self.monitors)} monitors:")
            for i, m in enumerate(self.monitors):
                is_primary = " (PRIMARY)" if hasattr(m, 'is_primary') and m.is_primary else ""
                print(f"  Monitor {i}: {m.name}{is_primary} - Position: ({m.x}, {m.y}) - Size: {m.width}x{m.height}")
            
            # (Removed monitor selection logic)
        except Exception as e:
            print(f"Error initializing monitors: {e}")
            messagebox.showwarning("Monitor Warning", f"Could not detect monitors: {e}")
            
    def load_monitors(self):
        """Load all available monitors"""
        try:
            self.monitors = get_monitors()
            print(f"Found {len(self.monitors)} monitors:")
            for i, m in enumerate(self.monitors):
                is_primary = " (PRIMARY)" if hasattr(m, 'is_primary') and m.is_primary else ""
                print(f"  Monitor {i}: {m.name}{is_primary} - Position: ({m.x}, {m.y}) - Size: {m.width}x{m.height}")
        except Exception as e:
            print(f"Error loading monitors: {e}")
            messagebox.showwarning("Monitor Warning", f"Could not detect monitors: {e}")

    # Removed save_monitor_settings (no longer needed)
            
    # Removed on_monitor_change (no longer needed)

    def setup_ui(self):
        # Clean light theme colors
        bg_primary = '#f7f9fa'      # Very light gray background
        bg_secondary = '#ffffff'    # White for cards/sections
        accent_primary = '#4f8cff'  # Soft blue accent
        accent_secondary = '#e0e7ff'  # Light blue accent
        text_primary = '#222b45'    # Dark text
        text_secondary = '#6b778c'  # Muted text
        success_color = '#43b581'   # Green
        danger_color = '#ff5c5c'    # Red
        warning_color = '#f7b731'   # Yellow

        # Main container with padding
        main_frame = tk.Frame(self.root, bg=bg_primary, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header section
        header_frame = tk.Frame(main_frame, bg=bg_primary)
        header_frame.pack(fill=tk.X, pady=(0, 18))

        # Status with modern styling
        self.status_label = tk.Label(header_frame, text="● Not Running", fg=text_secondary,
                                     bg=bg_primary, font=("Segoe UI", 18, "bold"))
        self.status_label.pack()
        # Analysis/comparison label (hidden by default)
        self.analysis_label = tk.Label(
            header_frame,
            text="",
            fg=accent_primary,
            bg=bg_primary,
            font=(
                "Segoe UI",
                10,
                "bold"))
        self.analysis_label.pack(pady=(6, 0))

        # Card-style container for audio settings
        audio_card = tk.Frame(
            main_frame,
            bg=bg_secondary,
            relief=tk.GROOVE,
            bd=1,
            highlightbackground=accent_secondary,
            highlightthickness=1)
        audio_card.pack(fill=tk.X, pady=(0, 18), padx=10, ipady=10, ipadx=10)
        audio_card.configure(borderwidth=0, highlightcolor=accent_secondary)

        # Audio settings header
        audio_header = tk.Label(audio_card, text="🔊 Audio Settings",
                                fg=accent_primary, bg=bg_secondary, font=("Segoe UI", 12, "bold"))
        audio_header.pack(anchor=tk.W, pady=(0, 12))

        # Volume control section
        volume_section = tk.Frame(audio_card, bg=bg_secondary)
        volume_section.pack(fill=tk.X, pady=(0, 12))

        volume_label = tk.Label(volume_section, text="Alert Volume",
                                fg=text_secondary, bg=bg_secondary, font=("Segoe UI", 10))
        volume_label.pack(anchor=tk.W, pady=(0, 3))

        volume_container = tk.Frame(volume_section, bg=bg_secondary)
        volume_container.pack(fill=tk.X)

        self.volume_slider = tk.Scale(volume_container, from_=0, to=100, orient=tk.HORIZONTAL,
                                      length=250, bg=bg_secondary, fg=accent_primary,
                                      highlightbackground=bg_secondary, troughcolor=accent_secondary,
                                      activebackground=accent_primary, font=(
                                          "Segoe UI", 9),
                                      showvalue=True, relief=tk.FLAT, bd=0, sliderrelief=tk.FLAT)
        self.volume_slider.set(int(self.alert_volume * 100))
        self.volume_slider.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(
                0,
                10))

        def on_volume_change(val):
            self.alert_volume = int(val) / 100.0
            self.save_volume_setting()
        self.volume_slider.config(command=on_volume_change)        # Device selection section
        device_section = tk.Frame(audio_card, bg=bg_secondary)
        device_section.pack(fill=tk.X, pady=(0, 8))

        device_label = tk.Label(device_section, text="Output Device",
                                fg=text_secondary, bg=bg_secondary, font=("Segoe UI", 10))
        device_label.pack(anchor=tk.W, pady=(0, 3))

        device_container = tk.Frame(device_section, bg=bg_secondary)
        device_container.pack(fill=tk.X)

        # Modern dropdown styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Light.TCombobox',
                        fieldbackground=bg_secondary,
                        background=bg_secondary,
                        foreground=text_primary,
                        borderwidth=0,
                        relief=tk.FLAT)

        self.device_combo = ttk.Combobox(device_container, state="readonly", width=35,
                                         style='Light.TCombobox', font=("Segoe UI", 9))
        device_names = [device['name'] for device in self.audio_devices]
        self.device_combo['values'] = device_names

        # Set current selection based on saved device ID
        current_selection = 0
        if self.selected_device_id is not None:
            for i, device in enumerate(self.audio_devices):
                if device['id'] == self.selected_device_id:
                    current_selection = i
                    print(f"Restored saved device: {device['name']}")
                    break
            else:
                if self.audio_devices:
                    self.selected_device_id = self.audio_devices[0]['id']
                    self.save_audio_settings()
                    print(
                        f"Saved device not found, using: {
                            self.audio_devices[0]['name']}")
        elif self.audio_devices:
            current_selection = 0
            self.selected_device_id = self.audio_devices[0]['id']
            self.save_audio_settings()
            print(f"No saved device, using: {self.audio_devices[0]['name']}")

        if device_names:
            self.device_combo.current(current_selection)

        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_change)
        self.device_combo.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(
                0,
                10))        # Modern test button
        test_button = tk.Button(device_container, text="🎵 Test", command=self.test_audio_device,
                                bg=accent_primary, fg='white', font=("Segoe UI", 9, "bold"),
                                relief=tk.FLAT, bd=0, padx=15, pady=8,
                                activebackground='#6fa8ff', activeforeground='white', cursor='hand2')
        test_button.pack(side=tk.RIGHT)        # Add info about auto-detection of monitors
        monitor_info_frame = tk.Frame(main_frame, bg=bg_primary)
        monitor_info_frame.pack(fill=tk.X, pady=(0, 18), padx=10)
        
        monitor_info_label = tk.Label(monitor_info_frame, 
                                    text="🖥️ Auto-detecting monitor with Dota 2", 
                                    fg=accent_primary, bg=bg_primary, 
                                    font=("Segoe UI", 10, "italic"))
        monitor_info_label.pack(pady=(0, 3))
        
        # Add monitor info label that will be updated when detection runs
        self.monitor_info_label = tk.Label(monitor_info_frame, 
                                         text="Waiting for Dota 2...",
                                         fg=text_secondary, bg=bg_primary, 
                                         font=("Segoe UI", 8))
        self.monitor_info_label.pack(pady=(0, 5))

        # Control buttons section with padding and side-by-side
        controls_frame = tk.Frame(main_frame, bg=bg_primary)
        controls_frame.pack(pady=24)

        button_style = {
            'font': ("Segoe UI", 13, "bold"),
            'relief': tk.FLAT,
            'bd': 0,
            'padx': 30,
            'pady': 14,
            'cursor': 'hand2',
            'highlightthickness': 0,
        }
        # Start Button
        self.start_button = tk.Button(
            controls_frame, text="▶ Start Detection", command=self.start_script,
            bg=success_color, fg='white', activebackground='#5edc9a', activeforeground='white',
            **button_style)
        self.start_button.pack(side=tk.LEFT, padx=(0, 18), ipadx=8, ipady=2)
        self.start_button.bind(
            "<Enter>",
            lambda e: self.start_button.config(
                bg="#5edc9a"))
        self.start_button.bind(
            "<Leave>",
            lambda e: self.start_button.config(
                bg=success_color))
        self.start_button.config(highlightbackground="#d4f5e9")

        # Stop Button
        self.stop_button = tk.Button(
            controls_frame, text="⏹ Stop", command=self.stop_script,
            bg=danger_color, fg='white', activebackground='#ff8787', activeforeground='white',
            **button_style)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 0), ipadx=8, ipady=2)
        self.stop_button.bind(
            "<Enter>",
            lambda e: self.stop_button.config(
                bg="#ff8787"))
        self.stop_button.bind(
            "<Leave>",
            lambda e: self.stop_button.config(
                bg=danger_color))
        # Info section at bottom
        self.stop_button.config(highlightbackground="#ffd6d6")
        info_frame = tk.Frame(main_frame, bg=bg_primary)
        info_frame.pack(side=tk.BOTTOM, pady=(24, 0))

        # Add diagnostics button
        diag_frame = tk.Frame(main_frame, bg=bg_primary)
        diag_frame.pack(side=tk.BOTTOM, pady=(0, 10))

        diag_button = tk.Button(diag_frame, text="🔍 Run Monitor Diagnostics", command=self.run_monitor_diagnostics,
                                bg='#8a94a6', fg='white', font=("Segoe UI", 9, "bold"),
                                relief=tk.FLAT, bd=0, padx=15, pady=6,
                                activebackground='#6c7a8c', activeforeground='white', cursor='hand2')
        diag_button.pack()

        info_label = tk.Label(info_frame, text="🎮 Auto-accepting Dota 2 matches with audio alerts",
                              fg=accent_primary, bg=bg_primary, font=("Segoe UI", 10, "italic"))
        info_label.pack()

        device_count_label = tk.Label(info_frame, text=f"📊 {len(self.audio_devices)} active audio devices detected",
                                      fg=text_secondary, bg=bg_primary, font=("Segoe UI", 8))
        device_count_label.pack(pady=(5, 0))

    def save_debug_screenshot(self, screenshot_np,
                              filename="debug_screenshot.png"):
        """Save a debug screenshot to help troubleshoot detection issues"""
        try:
            debug_dir = "debug_screenshots"
            # Create the debug directory if it doesn't exist
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Limit to max 10 files - check current files and remove oldest if
            # needed
            try:
                files = [os.path.join(debug_dir, f) for f in os.listdir(debug_dir)
                         if os.path.isfile(os.path.join(debug_dir, f))]

                # Sort files by modification time (oldest first)
                files.sort(key=os.path.getmtime)

                # If we have 10 or more files, delete the oldest ones
                max_files = 10
                if len(files) >= max_files:
                    # Calculate how many to delete (keep max_files-1 to make
                    # room for the new one)
                    to_delete = len(files) - (max_files - 1)
                    for i in range(to_delete):
                        try:
                            os.remove(files[i])
                            print(
                                f"🗑️ Removed old debug screenshot: {
                                    files[i]} (maintaining max {max_files} files)")
                        except Exception as del_err:
                            print(
                                f"⚠️ Could not delete old screenshot {
                                    files[i]}: {del_err}")
            except Exception as limit_err:
                print(
                    f"⚠️ Error while limiting debug screenshots: {limit_err}")

            # Generate a filename with timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            path = os.path.join(debug_dir, f"{timestamp}_{filename}")

            # Save the screenshot
            cv2.imwrite(path, screenshot_np)
            print(f"✅ Debug screenshot saved to {path}")
            return path
        except Exception as e:
            print(f"❌ Failed to save debug screenshot: {e}")
            return None

    def run_monitor_diagnostics(self):
        """Run diagnostics: save screenshot of Dota 2 monitor or fallback to fullscreen, using test.py logic."""
        try:
            filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
            result = self.save_dota2_monitor_screenshot(filename)
            if result:
                print(f"✅ Dota 2 monitor screenshot saved to {result}")
            else:
                # fallback to fullscreen screenshot
                filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
                screenshot = pyautogui.screenshot()
                screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, screenshot_np)
                print(f"✅ Fullscreen screenshot saved to {filename}")
            messagebox.showinfo("Diagnostics Complete", "Screenshot saved. Check the file in your folder.")
        except Exception as e:
            print(f"❌ Error in monitor diagnostics: {e}")
            messagebox.showerror("Diagnostics Error", f"Error during monitor diagnostics: {e}")


def main():
    root = tk.Tk()
    app = DotaAutoAccept(root)
    app.start_script()
    root.mainloop()


if __name__ == "__main__":
    main()
