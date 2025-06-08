import pyautogui
import cv2
import numpy as np
import time
import pygetwindow as gw
from PIL import ImageGrab
import mss
import os
from skimage.metrics import structural_similarity as ssim
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging configuration
log_file = os.path.join('logs', 'dota2_auto_accept.log')
logger = logging.getLogger('Dota2AutoAccept')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)  # 1MB file size, keep 5 backups
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

selected_device_id = None
alert_volume = 1.0
SETTINGS_FILE = 'config.json'  # Changed from 'alert_volume.json'
selected_monitor_capture_setting = 1 # Default to monitor 1
is_running = False
detection_thread = None
match_found = False

def save_fullscreen_screenshot(filename):
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, screenshot_np)
    logger.info(f"Fullscreen screenshot saved to {filename}")

def save_dota2_window_screenshot(filename):
    windows = gw.getWindowsWithTitle('Dota 2')
    if not windows:
        logger.warning('Dota 2 window not found!')
        return False
    win = windows[0]
    if win.isMinimized:
        logger.warning('Dota 2 window is minimized!')
        return False
    bbox = (win.left, win.top, win.right, win.bottom)
    screenshot = ImageGrab.grab(bbox)
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, screenshot_np)
    logger.info(f"Dota 2 window screenshot saved to {filename}")
    return True

def save_dota2_monitor_screenshot(filename, target_monitor_index: int):
    # Captures the selected monitor directly.
    with mss.mss() as sct:
        monitors = sct.monitors
        # monitors[0] is all-in-one, actual monitors start from index 1.
        # target_monitor_index is 1-based from user selection.
        if not monitors or len(monitors) <= 1: # Need at least one actual monitor besides the combined one
            logger.warning('No distinct monitors found by mss to capture from!')
            return False

        # Validate target_monitor_index (it's 1-based for user, so it maps to monitors[target_monitor_index])
        if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
            logger.warning(f"Invalid monitor index {target_monitor_index} specified. Available: 1 to {len(monitors)-1}. Screenshot not taken.")
            return False
            
        monitor_to_capture = monitors[target_monitor_index]
        
        try:
            img = sct.grab(monitor_to_capture)
            # mss grabs in BGRA, convert to BGR for OpenCV compatibility and to avoid alpha channel issues
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            cv2.imwrite(filename, img_bgr)
            logger.info(f"Screenshot of Monitor {target_monitor_index} saved to {filename}")
            return True
        except mss.exception.ScreenShotError as e:
            logger.error(f"Error capturing screenshot from Monitor {target_monitor_index} using mss: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while capturing/saving screenshot from Monitor {target_monitor_index}: {e}")
            return False

def compare_images(img1_path, img2_path):
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    if img1 is None or img2 is None:
        return 0.0
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # Resize to the same size
    if img1_gray.shape != img2_gray.shape:
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score

def keep_last_n_files(folder, n):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.png')]
    files.sort(key=os.path.getmtime, reverse=True)
    for f in files[n:]:
        os.remove(f)

def play_alert_sound():
    try:
        import pygame
        import time as _time
        mp3_path = os.path.join('bin', 'dota2.mp3')
        if os.path.exists(mp3_path):
            pygame.mixer.init()
            sound = pygame.mixer.Sound(mp3_path)
            arr = pygame.sndarray.array(sound)
            # Apply volume to the audio array
            arr = (arr * alert_volume).astype(arr.dtype)
            sample_rate = pygame.mixer.get_init()[0]
            sd.play(arr, samplerate=sample_rate, device=selected_device_id)
            sd.wait()
            pygame.mixer.quit()
        else:
            # fallback beep
            logger.warning("MP3 file not found. Using fallback beep.")
            import winsound
            winsound.Beep(1000, 500)
    except Exception as e:
        logger.error(f"Error playing alert sound: {e}")

def get_output_devices():
    devices = sd.query_devices()
    output_devices = []
    for i, d in enumerate(devices):
        if d['max_output_channels'] > 0:
            output_devices.append({'id': i, 'name': d['name']})
    return output_devices

def get_available_monitors():
    monitor_options = [] # No "Auto-detect"
    try:
        with mss.mss() as sct:
            # sct.monitors[0] is the full virtual screen, physical monitors start at index 1
            if len(sct.monitors) > 1:
                for i, monitor in enumerate(sct.monitors[1:], start=1): 
                    monitor_options.append((f"Monitor {i} ({monitor['width']}x{monitor['height']})", i))
            else:
                logger.warning("No individual monitors detected by mss, only the combined virtual screen.")
    except Exception as e:
        logger.error(f"Error getting monitor list: {e}")
    return monitor_options

def test_alert_sound():
    try:
        import pygame
        import time as _time
        mp3_path = os.path.join('bin', 'dota2.mp3')
        if os.path.exists(mp3_path):
            pygame.mixer.init()
            sound = pygame.mixer.Sound(mp3_path)
            arr = pygame.sndarray.array(sound)
            # Apply volume to the audio array
            arr = (arr * alert_volume).astype(arr.dtype)
            sample_rate = pygame.mixer.get_init()[0]
            sd.play(arr, samplerate=sample_rate, device=selected_device_id)
            sd.wait()
            pygame.mixer.quit()
        else:
            import winsound
            winsound.Beep(1000, 500)
    except Exception as e:
        logger.error(f"Error playing alert sound: {e}")
        messagebox.showerror("Test Error", str(e))

def load_audio_settings():
    global selected_device_id, alert_volume, selected_monitor_capture_setting
    
    # Set defaults before trying to load
    selected_monitor_capture_setting = 1 # Default to monitor 1
    alert_volume = 1.0
    selected_device_id = None

    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                alert_volume = float(data.get('alert_volume', 1.0))
                selected_device_id = data.get('selected_device_id', None)
                
                loaded_monitor_setting = data.get('selected_monitor_capture_setting', 1)
                if isinstance(loaded_monitor_setting, int) and loaded_monitor_setting > 0:
                    # We'll validate if this index is currently available in show_audio_settings
                    selected_monitor_capture_setting = loaded_monitor_setting
                else:
                    logger.warning(f"Invalid monitor setting '{loaded_monitor_setting}' in config. Defaulting to Monitor 1.")
                    selected_monitor_capture_setting = 1
        else:
            logger.info(f"Settings file {SETTINGS_FILE} not found. Using default settings.")
            # Defaults are already set above
            
    except Exception as e:
        logger.error(f"Error loading settings from {SETTINGS_FILE}: {e}. Using default values.")
        # Defaults are already set above

def save_audio_settings():
    global selected_monitor_capture_setting, alert_volume, selected_device_id
    try:
        data = {
            'alert_volume': alert_volume,
            'selected_device_id': selected_device_id,
            'selected_monitor_capture_setting': selected_monitor_capture_setting # This will be an int
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")

def show_audio_settings():
    global selected_device_id, alert_volume, is_running, detection_thread, selected_monitor_capture_setting
    win = tk.Tk()
    win.title("Dota 2 Auto Accept - Control Panel")
    
    # Center window on screen
    window_width = 450
    window_height = 450
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")
    win.resizable(False, False)
      # Try to set the icon
    try:
        icon_path = os.path.join('bin', 'icon.ico')
        if os.path.exists(icon_path):
            win.iconbitmap(icon_path)
    except:
        pass

    devices = get_output_devices()
    device_names = [d['name'] for d in devices]
    current_device = tk.StringVar()
    # Try to restore last used device
    initial_idx = 0
    if devices:
        if selected_device_id is not None:
            for i, d in enumerate(devices):
                if d['id'] == selected_device_id:
                    initial_idx = i
                    break
            else:
                initial_idx = 0
                selected_device_id = devices[0]['id']
        else:
            initial_idx = 0
            selected_device_id = devices[0]['id']
        current_device.set(device_names[initial_idx])

    # Monitor selection
    monitors_available = get_available_monitors() # Now returns list of (display_name, index) or empty
    monitor_display_names = [m[0] for m in monitors_available]
    current_monitor_setting_tk = tk.StringVar()

    initial_monitor_idx = 0 # Default to the first in the list if available

    if monitors_available:
        found_saved_setting = False
        for i, (_, monitor_val_from_list) in enumerate(monitors_available):
            if monitor_val_from_list == selected_monitor_capture_setting:
                initial_monitor_idx = i
                found_saved_setting = True
                break
        
        if not found_saved_setting:
            logger.warning(f"Previously selected monitor {selected_monitor_capture_setting} is not currently available or invalid. Defaulting to Monitor {monitors_available[0][1]}.")
            initial_monitor_idx = 0
            selected_monitor_capture_setting = monitors_available[0][1] # Update global to the first available
            save_audio_settings() # Persist this default if changed
        
        current_monitor_setting_tk.set(monitor_display_names[initial_monitor_idx])
    else:
        current_monitor_setting_tk.set("No monitors available")
        selected_monitor_capture_setting = -1 # Indicate no valid monitor can be selected

    def on_device_change(event=None):
        nonlocal devices
        idx = combo.current()
        if 0 <= idx < len(devices):
            global selected_device_id
            selected_device_id = devices[idx]['id']
            save_audio_settings()

    def on_volume_change(val):
        global alert_volume
        alert_volume = int(val) / 100.0
        save_audio_settings()
        
    def on_monitor_select(event=None):
        nonlocal monitors_available # Ensure this is the list from show_audio_settings scope
        idx = monitor_combo.current()
        if monitors_available and 0 <= idx < len(monitors_available):
            global selected_monitor_capture_setting
            selected_monitor_capture_setting = monitors_available[idx][1] # Get the monitor index (int)
            save_audio_settings()
            logger.info(f"Monitor capture setting changed to: Monitor {selected_monitor_capture_setting}")
        elif not monitors_available:
            logger.warning("No monitors to select.")

    def update_status():
        if is_running:
            status_label.config(text="Status: Running Detection", fg="green")
            start_btn.pack_forget()
            stop_btn.pack(side="left", padx=5)
            stop_btn.config(state="normal", text="⏹ Stop Detection", bg="red")
        elif match_found:
            status_label.config(text="Status: Match Found! Detection Stopped", fg="blue")
            stop_btn.pack_forget()
            start_btn.pack(side="left", padx=5)
            start_btn.config(state="normal", text="▶ Start New Detection", bg="green")
        else:
            status_label.config(text="Status: Stopped", fg="red")
            stop_btn.pack_forget()
            start_btn.pack(side="left", padx=5)
            start_btn.config(state="normal", text="▶ Start Detection", bg="green")
        win.after(500, update_status)  # Update every 500ms
        
    def start_detection():
        global is_running, detection_thread, match_found
        if not is_running:
            is_running = True
            match_found = False
            detection_thread = threading.Thread(target=main_loop, daemon=True)
            detection_thread.start()
            logger.info("Detection started!")

    def stop_detection():
        global is_running
        is_running = False
        logger.info("Detection stopped!")

    def on_closing():
        global is_running
        is_running = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_closing)

    # Status label
    status_label = tk.Label(win, text="Status: Stopped", font=("Arial", 12, "bold"), fg="red")
    status_label.pack(pady=(10, 5))

    # Audio settings frame
    audio_frame = tk.LabelFrame(win, text="Audio Settings", padx=10, pady=10)
    audio_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(audio_frame, text="Output Device:").pack(pady=(5,0))
    combo = ttk.Combobox(audio_frame, values=device_names, state="readonly")
    combo.pack(pady=5)
    combo.current(initial_idx)
    combo.bind('<<ComboboxSelected>>', on_device_change)

    tk.Label(audio_frame, text="Volume:").pack(pady=(10,0))
    slider = tk.Scale(audio_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=on_volume_change)
    slider.set(int(alert_volume * 100))
    slider.pack(pady=5)

    test_btn = tk.Button(audio_frame, text="🎵 Test Sound", command=test_alert_sound)
    test_btn.pack(pady=5)
    
    # Monitor settings frame
    monitor_frame = tk.LabelFrame(win, text="Monitor Settings", padx=10, pady=10)
    monitor_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(monitor_frame, text="Capture Monitor:").pack(pady=(5,0))
    monitor_combo = ttk.Combobox(monitor_frame, textvariable=current_monitor_setting_tk, values=monitor_display_names, state="readonly")
    
    if not monitors_available:
        monitor_combo.config(state="disabled")
    
    monitor_combo.pack(pady=5)
    
    if monitors_available:
        monitor_combo.current(initial_monitor_idx)
    
    monitor_combo.bind('<<ComboboxSelected>>', on_monitor_select)

    # Control buttons frame
    control_frame = tk.LabelFrame(win, text="Detection Control", padx=10, pady=10)
    control_frame.pack(fill="x", padx=10, pady=5)

    button_frame = tk.Frame(control_frame)
    button_frame.pack()

    start_btn = tk.Button(button_frame, text="▶ Start Detection", command=start_detection,
                         bg="green", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
    start_btn.pack(side="left", padx=5)

    stop_btn = tk.Button(button_frame, text="⏹ Stop Detection", command=stop_detection,
                        bg="red", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5, state="disabled")
    stop_btn.pack(side="left", padx=5)

    # Info frame with instructions
    info_frame = tk.Frame(win)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    info_text = "Instructions:\n• Start detection before launching Dota 2\n• Detection stops automatically after finding a match\n• Use Test Sound to verify your audio settings\n\nKeyboard Shortcuts: F1=Start | F2=Stop | F3=Test Sound"
    info_label = tk.Label(info_frame, text=info_text, font=("Arial", 8), fg="gray", justify="left")
    info_label.pack()
    
    # Keyboard shortcuts
    def on_key_press(event):
        if event.keysym == 'F1':  # F1 to start
            if not is_running:
                start_detection()
        elif event.keysym == 'F2':  # F2 to stop
            if is_running:
                stop_detection()
        elif event.keysym == 'F3':  # F3 to test sound
            test_alert_sound()
    
    win.bind('<KeyPress>', on_key_press)
    win.focus_set()  # Make sure window can receive key events

    update_status()
    win.mainloop()

def main_loop():
    global is_running, match_found, selected_monitor_capture_setting
    folder = 'debug_screenshots'
    os.makedirs(folder, exist_ok=True)
    ref1 = os.path.join('bin', 'dota.png')
    ref2 = os.path.join('bin', 'print.png')
    logger.info("Detection loop started")
    while is_running:
        # Use a more specific name for the screenshot attempt for clarity
        screenshot_filename = os.path.join(folder, f'dota2_monitor_capture_{time.strftime("%Y%m%d-%H%M%S")}.png')
        
        if save_dota2_monitor_screenshot(screenshot_filename, selected_monitor_capture_setting):
            # Successfully captured Dota 2 monitor; proceed with comparison
            keep_last_n_files(folder, 5) # Manage screenshots in the folder
            sim1 = compare_images(screenshot_filename, ref1)
            sim2 = compare_images(screenshot_filename, ref2)
            logger.info(f"Similarity with {ref1}: {sim1:.2f}, with {ref2}: {sim2:.2f}")
            if sim1 > 0.7 or sim2 > 0.7:
                logger.info("Match detected! Pressing Enter and playing sound.")
                play_alert_sound()
                pyautogui.press('enter')
                match_found = True
                is_running = False  # Stop detection after match found
                break # Exit the while loop
        else:
            # Failed to capture Dota 2 monitor
            logger.warning("Monitor capture failed for this iteration. Will retry.")
            # No comparison is done. Loop will sleep and then try again.

        time.sleep(1)  # Adjust interval as needed
    
    logger.info("Detection loop ended")

def main():
    filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
    if not save_dota2_monitor_screenshot(filename, selected_monitor_capture_setting):
        # fallback to fullscreen screenshot
        filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
        save_fullscreen_screenshot(filename)

if __name__ == "__main__":
    logger.info("Application starting")
    load_audio_settings()
    is_running = True
    match_found = False
    detection_thread = threading.Thread(target=main_loop, daemon=True)
    detection_thread.start()
    show_audio_settings()
    logger.info("Application exiting")
