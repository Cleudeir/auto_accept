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
from pycaw.pycaw import AudioUtilities, AudioEndpointVolume, ISimpleAudioVolume

class DotaAutoAccept:
    def __init__(self, root):
        self.root = root
        self.root.title("Dota 2 Auto Accept")
        self.root.geometry("450x420")
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
        
        # Initialize audio system
        self.init_audio_system()
        self.load_audio_settings()

        self.setup_ui()

    def init_audio_system(self):
        """Initialize the audio system and discover available devices"""
        try:
            # Get available audio output devices
            devices = sd.query_devices()
            self.audio_devices = []
            
            for i, device in enumerate(devices):
                if device['max_output_channels'] > 0:  # Output devices only
                    self.audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_output_channels']
                    })
            
            print(f"Found {len(self.audio_devices)} audio output devices")
            
            # Set default device if none selected
            if not self.selected_device_id and self.audio_devices:
                self.selected_device_id = sd.default.device[1]  # Default output device
                
        except Exception as e:
            print(f"Error initializing audio system: {e}")
            messagebox.showwarning("Audio Warning", f"Could not initialize audio system: {e}")

    def load_audio_settings(self):
        """Load saved audio settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.selected_device_id = settings.get('selected_device_id', self.selected_device_id)
                    print(f"Loaded audio device: {self.selected_device_id}")
        except Exception as e:
            print(f"Error loading audio settings: {e}")

    def save_audio_settings(self):
        """Save audio settings to file"""
        try:
            settings = {
                'selected_device_id': self.selected_device_id
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
            print(f"Saved audio device: {self.selected_device_id}")
        except Exception as e:
            print(f"Error saving audio settings: {e}")

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
        """Test the selected audio device with a short beep"""
        try:
            if self.selected_device_id is not None:
                # Test with a short beep
                sample_rate = 44100
                duration = 0.2
                freq = 800
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                tone = (np.sin(2 * np.pi * freq * t) * 0.3).astype(np.float32)
                
                sd.play(tone, samplerate=sample_rate, device=self.selected_device_id)
                sd.wait()  # Wait until the sound finishes
                print("Audio test successful")
        except Exception as e:
            print(f"Audio test failed: {e}")
            messagebox.showwarning("Audio Test", f"Failed to test audio device: {e}")

    def play_high_beep(self):
        """Play a high-pitched beep using the selected audio device"""
        try:
            if self.selected_device_id is None:
                print("No audio device selected")
                return
                
            # Generate a 1kHz beep for 500ms with fade in/out
            sample_rate = 44100
            duration = 0.5
            freq = 1000
            fade_duration = 0.05  # 50ms fade
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * freq * t).astype(np.float32)
            
            # Apply fade in/out to avoid clicks
            fade_samples = int(fade_duration * sample_rate)
            if fade_samples > 0:
                # Fade in
                tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
                # Fade out
                tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Adjust volume (0.0 to 1.0)
            tone *= 0.6
            
            # Play the sound on the selected device
            sd.play(tone, samplerate=sample_rate, device=self.selected_device_id)
            
            # Optional: wait for completion in a separate thread to not block UI
            threading.Thread(target=lambda: sd.wait(), daemon=True).start()
              print("Beep played successfully")
            
        except Exception as e:
            print(f"Error playing beep: {e}")
            # Fallback to pygame if sounddevice fails
            self.play_fallback_beep()

    def play_fallback_beep(self):
        """Fallback beep using pygame mixer"""
        try:
            if not self.pygame_initialized:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                self.pygame_initialized = True
            
            # Generate a 1kHz beep for 300ms
            sample_rate = 44100
            duration = 0.3
            freq = 1000
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = (np.sin(2 * np.pi * freq * t) * 32767 * 0.6).astype(np.int16)
            sound = pygame.sndarray.make_sound(tone)
            sound.play()
            
            print("Fallback beep played")
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
                    self.play_high_beep()
                    pyautogui.press('enter')
                    print("Match Accepted!")
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
        self.start_button.pack(side=tk.LEFT, padx=10)    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(main_frame, text="Not Running", fg="white", bg='#2c3e50', font=("Arial", 16, "bold"))
        self.status_label.pack(pady=(0, 10))

        # Audio device selection frame
        audio_frame = tk.Frame(main_frame, bg='#2c3e50')
        audio_frame.pack(pady=10, fill=tk.X)

        audio_label = tk.Label(audio_frame, text="Audio Output Device:", 
                              fg="white", bg='#2c3e50', font=("Arial", 10, "bold"))
        audio_label.pack(anchor=tk.W)

        # Audio device dropdown
        device_frame = tk.Frame(audio_frame, bg='#2c3e50')
        device_frame.pack(fill=tk.X, pady=(5, 0))

        self.device_combo = ttk.Combobox(device_frame, state="readonly", width=40)
        device_names = [device['name'] for device in self.audio_devices]
        self.device_combo['values'] = device_names
        
        # Set current selection
        if self.selected_device_id is not None:
            for i, device in enumerate(self.audio_devices):
                if device['id'] == self.selected_device_id:
                    self.device_combo.current(i)
                    break
        elif device_names:
            self.device_combo.current(0)
            
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

        info_label = tk.Label(info_frame, text="Auto-accepting matches", 
                             fg="#f1c40f", bg='#2c3e50', font=("Arial", 10))
        info_label.pack()

        device_count_label = tk.Label(info_frame, text=f"Found {len(self.audio_devices)} audio devices", 
                                     fg="#95a5a6", bg='#2c3e50', font=("Arial", 8))
        device_count_label.pack()

def main():
    root = tk.Tk()
    app = DotaAutoAccept(root)
    app.start_script()
    root.mainloop()

if __name__ == "__main__":
    main()
