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
        self.root.geometry("450x280")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c3e50')

        self.reference_image_path = self.resource_path("dota.png")
        self.reference_image = cv2.imread(self.reference_image_path, cv2.IMREAD_COLOR)

        self.reference_image_plus_path = self.resource_path("dota2-plus.jpeg")
        self.reference_image_plus = cv2.imread(self.reference_image_plus_path, cv2.IMREAD_COLOR)

        if self.reference_image is None and self.reference_image_plus is None:
            messagebox.showerror("Error", f"Reference images not found: {self.reference_image_path} and {self.reference_image_plus_path}")
            sys.exit(1)

        self.running = False
        self.start_button = None
        self.stop_button = None
        
        # Audio system variables
        self.audio_devices = []
        self.selected_device_id = None
        self.settings_file = self.resource_path("audio_settings.json")
        self.pygame_initialized = False
        
        # Initialize alert volume
        self.alert_volume = 1.0  # Default to 100%
        self.volume_settings_file = self.resource_path("alert_volume.json")
        self.load_volume_setting()
        
        # Initialize audio system
        self.init_audio_system()
        self.load_audio_settings()

        self.setup_ui()

    def _normalize_device_name(self, name):
        # Use only the first 12 characters, lowercase, and remove extra spaces for duplicate detection
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
                    skip_keywords = ['communications', 'comm', 'recording', 'input', 'line in', 'microphone']
                    if any(keyword in device_name.lower() for keyword in skip_keywords):
                        continue
                    norm_name = self._normalize_device_name(device_name)
                    if norm_name in seen_normalized:
                        continue
                    # Check if device is actually available by trying to query it
                    try:
                        sd.check_output_settings(device=i, channels=1, samplerate=44100)
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
            print(f"Found {len(self.audio_devices)} active audio output devices (no similar duplicates by first 12 chars)")
            
            # Set default device if none selected
            if not self.selected_device_id and self.audio_devices:
                try:
                    default_output = sd.default.device[1]  # Default output device
                    # Check if default device is in our filtered list
                    for device in self.audio_devices:
                        if device['id'] == default_output:
                            self.selected_device_id = default_output
                            print(f"Using system default device: {device['name']}")
                            break
                    # If default not found, use first available device
                    if self.selected_device_id is None:
                        self.selected_device_id = self.audio_devices[0]['id']
                        print(f"Using first available device: {self.audio_devices[0]['name']}")
                except Exception:
                    if self.audio_devices:
                        self.selected_device_id = self.audio_devices[0]['id']
                        print(f"Using first available device: {self.audio_devices[0]['name']}")
                
        except Exception as e:
            print(f"Error initializing audio system: {e}")
            messagebox.showwarning("Audio Warning", f"Could not initialize audio system: {e}")

    def load_audio_settings(self):
        """Load saved audio settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    saved_device_id = settings.get('selected_device_id')
                    
                    # Validate that the saved device still exists in our active devices list
                    if saved_device_id is not None:
                        for device in self.audio_devices:
                            if device['id'] == saved_device_id:
                                self.selected_device_id = saved_device_id
                                print(f"Loaded saved audio device: {device['name']}")
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
            
            print(f"Saved audio device: {device_name} (ID: {self.selected_device_id})")
        except Exception as e:
            print(f"Error saving audio settings: {e}")

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
            print(f"Set system default output device volume to {vol:.2f}, previous was {prev_vol:.2f}")
            return prev_vol
        except Exception as e:
            print(f"Failed to set device volume: {e}")
            return None

    def on_device_change(self, event=None):
        """Handle audio device selection change"""
        if hasattr(self, 'device_combo') and self.device_combo:
            selected_idx = self.device_combo.current()
            if 0 <= selected_idx < len(self.audio_devices):
                self.selected_device_id = self.audio_devices[selected_idx]['id']
                self.save_audio_settings()
                print(f"Audio device changed to: {self.audio_devices[selected_idx]['name']}")
                
                # Test the new device
                self.test_audio_device()

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
                            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                            self.pygame_initialized = True
                        sound = pygame.mixer.Sound(mp3_path)
                        sound_array = pygame.sndarray.array(sound)
                        if sound_array.dtype != np.float32:
                            if sound_array.dtype == np.int16:
                                sound_array = sound_array.astype(np.float32) / 32768.0
                            else:
                                sound_array = sound_array.astype(np.float32)
                        sample_rate = pygame.mixer.get_init()[0]
                        # Play up to 3 seconds for test
                        test_length = min(sample_rate * 3, len(sound_array))
                        test_audio = sound_array[:test_length] * 0.8
                        sd.play(test_audio, samplerate=sample_rate, device=self.selected_device_id)
                        sd.wait()
                        print("Audio test successful using dota2.mp3 (3s)")
                        return
                    except Exception as mp3_error:
                        print(f"MP3 test failed: {mp3_error}, using fallback beep")
                # Fallback: 3s beep
                sample_rate = 44100
                duration = 3.0
                freq = 800
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                tone = (np.sin(2 * np.pi * freq * t) * 0.3).astype(np.float32)
                sd.play(tone, samplerate=sample_rate, device=self.selected_device_id)
                sd.wait()
                print("Audio test successful using fallback beep (3s)")
        except Exception as e:
            print(f"Audio test failed: {e}")
            messagebox.showwarning("Audio Test", f"Failed to test audio device: {e}")
        finally:
            self.restore_device_volume(prev_vol)
            self.unmute_other_audio()

    def set_device_volume_max(self):
        """Set the selected audio device's volume to maximum using pycaw (Windows only). Returns previous volume (0.0-1.0) or None on error."""
        if not pycaw_available:
            print("pycaw not available, cannot set device volume programmatically.")
            return None
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            prev_vol = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(1.0, None)  # 1.0 = 100%
            print(f"Set system default output device volume to 100% (max), previous was {prev_vol:.2f}")
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
            print(f"Restored system default output device volume to {prev_vol:.2f}")
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
                        print(f"Unmuted audio session: {session.Process.name()}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"Failed to unmute other audio sessions: {e}")

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
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
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
            print(f"Playing dota2.mp3 at user volume {self.alert_volume:.2f} on device {self.selected_device_id}")
            sd.play(sound_array, samplerate=sample_rate, device=self.selected_device_id)
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
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
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
            tone = (np.sin(2 * np.pi * freq * t) * 32767 * 1.0).astype(np.int16)  # Maximum volume
            sound = pygame.sndarray.make_sound(tone)
            sound.set_volume(1.0)  # Maximum volume
            sound.play()
            
            print("Fallback beep played at maximum volume")
        except Exception as e:
            print(f"Error playing fallback beep: {e}")

    def get_dota_monitor(self):
        try:
            hwnd = win32gui.FindWindow(None, "Dota 2")
            if hwnd == 0:
                print("Dota 2 window not found.")
                return None

            rect = win32gui.GetWindowRect(hwnd)
            window_x, window_y, _, _ = rect

            for monitor in get_monitors():
                if monitor.x <= window_x < monitor.x + monitor.width and \
                   monitor.y <= window_y < monitor.y + monitor.height:
                    print(f"Dota 2 found on monitor: {monitor.name}")
                    return (monitor.x, monitor.y, monitor.width, monitor.height)
            
            print("Could not determine the monitor for Dota 2 window.")
            return None
        except Exception as e:
            print(f"Error finding Dota 2 window/monitor: {e}")
            return None

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def find_and_press_enter(self):
        confidence = 0.6

        # Prepare reference images (gray)
        reference_gray = None
        reference_plus_gray = None
        if self.reference_image is not None:
            reference_gray = cv2.cvtColor(self.reference_image, cv2.COLOR_BGR2GRAY)
        if self.reference_image_plus is not None:
            reference_plus_gray = cv2.cvtColor(self.reference_image_plus, cv2.COLOR_BGR2GRAY)

        dota_monitor_region = self.get_dota_monitor()
        if dota_monitor_region is None:
            messagebox.showerror("Error", "Could not find Dota 2 window. Ensure Dota 2 is running.")
            self.stop_script() # Stop if monitor not found
            return

        while self.running:
            try:
                # Take screenshot of the specific monitor where Dota 2 is running
                screenshot = pyautogui.screenshot(region=dota_monitor_region)
                screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                screenshot_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

                found = False
                max_val = 0
                # Check dota.png
                if reference_gray is not None:
                    result = cv2.matchTemplate(screenshot_gray, reference_gray, cv2.TM_CCOEFF_NORMED)
                    _, max_val1, _, _ = cv2.minMaxLoc(result)
                    if max_val1 >= confidence:
                        found = True
                        max_val = max_val1
                # Check dota2-plus.png
                if not found and reference_plus_gray is not None:
                    result_plus = cv2.matchTemplate(screenshot_gray, reference_plus_gray, cv2.TM_CCOEFF_NORMED)
                    _, max_val2, _, _ = cv2.minMaxLoc(result_plus)
                    if max_val2 >= confidence:
                        found = True
                        max_val = max_val2

                if found:
                    print(f"Detected ACCEPT screen! Confidence: {max_val:.2f}")
                    repeat_count = 2  # Number of times to repeat the beep
                    for i in range(repeat_count):
                        self.play_high_beep()
                        pyautogui.press('enter')
                        print(f"Match Accepted! (Attempt {i+1}/{repeat_count})")
                        if i < repeat_count - 1:
                            time.sleep(3)  # 3 second delay between attempts
                    time.sleep(5)
                    self.stop_script() # Stop the script after finding the match.
                    return # exit the function
            except Exception as e:
                print(f"Error in detection: {e}")

            time.sleep(1)

    def start_script(self):
        # Check for Dota 2 window before starting
        if self.get_dota_monitor() is None:
             messagebox.showwarning("Warning", "Dota 2 window not found. Please start Dota 2.")
             return # Don't start if Dota 2 isn't running

        if not self.running:
            self.running = True
            threading.Thread(target=self.find_and_press_enter, daemon=True).start()
            self.status_label.config(text="Running...", fg="#2ecc71")
            self.start_button.pack_forget()
            self.stop_button.pack(side=tk.LEFT, padx=10)

    def stop_script(self):
        self.running = False
        self.status_label.config(text="Stopped", fg="#e74c3c")
        self.stop_button.pack_forget()
        self.start_button.pack(side=tk.LEFT, padx=10)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(main_frame, text="Not Running", fg="white", bg='#2c3e50', font=("Arial", 16, "bold"))
        self.status_label.pack(pady=(0, 10))

        # Audio device selection frame
        audio_frame = tk.Frame(main_frame, bg='#2c3e50')
        audio_frame.pack(pady=10, fill=tk.X)

        audio_label = tk.Label(audio_frame, text="Audio Output Device (Active Only):", 
                              fg="white", bg='#2c3e50', font=("Arial", 10, "bold"))
        audio_label.pack(anchor=tk.W)

        # Volume slider
        volume_frame = tk.Frame(audio_frame, bg='#2c3e50')
        volume_frame.pack(fill=tk.X, pady=(5, 0))
        tk.Label(volume_frame, text="Alert Volume:", fg="white", bg='#2c3e50', font=("Arial", 9)).pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=180, bg='#2c3e50', fg='white', highlightbackground='#2c3e50', troughcolor='#34495e', showvalue=True)
        self.volume_slider.set(int(self.alert_volume * 100))
        self.volume_slider.pack(side=tk.LEFT, padx=(5, 0))
        def on_volume_change(val):
            self.alert_volume = int(val) / 100.0
            self.save_volume_setting()
        self.volume_slider.config(command=on_volume_change)

        # Audio device dropdown
        device_frame = tk.Frame(audio_frame, bg='#2c3e50')
        device_frame.pack(fill=tk.X, pady=(5, 0))
        self.device_combo = ttk.Combobox(device_frame, state="readonly", width=40)
        device_names = [device['name'] for device in self.audio_devices]
        self.device_combo['values'] = device_names
        
        # Set current selection based on saved device ID
        current_selection = 0  # Default to first device
        if self.selected_device_id is not None:
            for i, device in enumerate(self.audio_devices):
                if device['id'] == self.selected_device_id:
                    current_selection = i
                    print(f"Restored saved device: {device['name']}")
                    break
            else:
                # Saved device not found, save the current default
                if self.audio_devices:
                    self.selected_device_id = self.audio_devices[0]['id']
                    self.save_audio_settings()
                    print(f"Saved device not found, using: {self.audio_devices[0]['name']}")
        elif self.audio_devices:
            # No saved device, use first available
            current_selection = 0
            self.selected_device_id = self.audio_devices[0]['id']
            self.save_audio_settings()
            print(f"No saved device, using: {self.audio_devices[0]['name']}")
            
        if device_names:
            self.device_combo.current(current_selection)
            
        self.device_combo.bind('<<ComboboxSelected>>', self.on_device_change)
        self.device_combo.pack(side=tk.LEFT, padx=(0, 10))

        # Test audio button
        test_button = tk.Button(device_frame, text="Test", command=self.test_audio_device,
                               bg="#3498db", fg="white", font=("Arial", 9), width=8)
        test_button.pack(side=tk.LEFT)

        # Start/Stop buttons
        self.button_frame = tk.Frame(main_frame, bg='#2c3e50')
        self.button_frame.pack(pady=20)

        self.start_button = tk.Button(
            self.button_frame, text="Start", command=self.start_script, 
            bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), width=10)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_script, 
            bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), width=10)

        # Information labels
        info_frame = tk.Frame(main_frame, bg='#2c3e50')
        info_frame.pack(side=tk.BOTTOM, pady=(20, 0))

        info_label = tk.Label(info_frame, text="Auto-accepting matches - Now with dota2.mp3 sound!", 
                             fg="#f1c40f", bg='#2c3e50', font=("Arial", 10))
        info_label.pack()

        device_count_label = tk.Label(info_frame, text=f"Found {len(self.audio_devices)} active audio devices", 
                                     fg="#95a5a6", bg='#2c3e50', font=("Arial", 8))
        device_count_label.pack()

def main():
    root = tk.Tk()
    app = DotaAutoAccept(root)
    app.start_script()
    root.mainloop()

if __name__ == "__main__":
    main()
