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

selected_device_id = None
alert_volume = 1.0
SETTINGS_FILE = 'alert_volume.json'

def save_fullscreen_screenshot(filename):
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, screenshot_np)
    print(f"✅ Fullscreen screenshot saved to {filename}")

def save_dota2_window_screenshot(filename):
    windows = gw.getWindowsWithTitle('Dota 2')
    if not windows:
        print('❌ Dota 2 window not found!')
        return False
    win = windows[0]
    if win.isMinimized:
        print('❌ Dota 2 window is minimized!')
        return False
    bbox = (win.left, win.top, win.right, win.bottom)
    screenshot = ImageGrab.grab(bbox)
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, screenshot_np)
    print(f"✅ Dota 2 window screenshot saved to {filename}")
    return True

def save_dota2_monitor_screenshot(filename):
    windows = gw.getWindowsWithTitle('Dota 2')
    if not windows:
        print('❌ Dota 2 window not found!')
        return False
    win = windows[0]
    if win.isMinimized:
        print('❌ Dota 2 window is minimized!')
        return False
    # Find which monitor the window is on
    with mss.mss() as sct:
        for monitor in sct.monitors[1:]:  # skip the first, which is the full virtual screen
            if (win.left >= monitor['left'] and win.right <= monitor['left'] + monitor['width'] and
                win.top >= monitor['top'] and win.bottom <= monitor['top'] + monitor['height']):
                img = sct.grab(monitor)
                img_np = np.array(img)
                cv2.imwrite(filename, img_np)
                print(f"✅ Dota 2 monitor screenshot saved to {filename}")
                return True
    print('❌ Dota 2 window not fully within a single monitor!')
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
        mp3_path = 'dota2.mp3'
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
            import winsound
            winsound.Beep(1000, 500)
    except Exception as e:
        print(f"Error playing alert sound: {e}")

def get_output_devices():
    devices = sd.query_devices()
    output_devices = []
    for i, d in enumerate(devices):
        if d['max_output_channels'] > 0:
            output_devices.append({'id': i, 'name': d['name']})
    return output_devices

def test_alert_sound():
    try:
        import pygame
        import time as _time
        mp3_path = 'dota2.mp3'
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
        print(f"Error playing alert sound: {e}")
        messagebox.showerror("Test Error", str(e))

def load_audio_settings():
    global selected_device_id, alert_volume
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                alert_volume = float(data.get('alert_volume', 1.0))
                selected_device_id = data.get('selected_device_id', None)
    except Exception as e:
        print(f"Error loading audio settings: {e}")
        alert_volume = 1.0
        selected_device_id = None

def save_audio_settings():
    try:
        data = {
            'alert_volume': alert_volume,
            'selected_device_id': selected_device_id
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving audio settings: {e}")

def show_audio_settings():
    global selected_device_id, alert_volume
    win = tk.Tk()
    win.title("Audio Settings")
    win.geometry("400x200")
    win.resizable(False, False)

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

    tk.Label(win, text="Output Device:").pack(pady=(10,0))
    combo = ttk.Combobox(win, values=device_names, state="readonly")
    combo.pack(pady=5)
    combo.current(initial_idx)
    combo.bind('<<ComboboxSelected>>', on_device_change)

    tk.Label(win, text="Volume:").pack(pady=(10,0))
    slider = tk.Scale(win, from_=0, to=100, orient=tk.HORIZONTAL, command=on_volume_change)
    slider.set(int(alert_volume * 100))
    slider.pack(pady=5)

    test_btn = tk.Button(win, text="Test Sound", command=test_alert_sound)
    test_btn.pack(pady=10)

    close_btn = tk.Button(win, text="Close", command=win.destroy)
    close_btn.pack(pady=5)

    win.mainloop()

def main_loop():
    folder = 'debug_screenshots'
    os.makedirs(folder, exist_ok=True)
    ref1 = 'dota.png'
    ref2 = 'print.png'
    while True:
        filename = os.path.join(folder, f'screenshot_{time.strftime("%Y%m%d-%H%M%S")}.png')
        if not save_dota2_monitor_screenshot(filename):
            filename = os.path.join(folder, f'fullscreen_{time.strftime("%Y%m%d-%H%M%S")}.png')
            save_fullscreen_screenshot(filename)
        keep_last_n_files(folder, 5)
        sim1 = compare_images(filename, ref1)
        sim2 = compare_images(filename, ref2)
        print(f"Similarity with {ref1}: {sim1:.2f}, with {ref2}: {sim2:.2f}")
        if sim1 > 0.7 or sim2 > 0.7:
            print("Detected match! Pressing Enter and playing sound.")
            play_alert_sound()
            pyautogui.press('enter')
            break  # Stop script after match found
        time.sleep(1)  # Adjust interval as needed

def main():
    filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
    if not save_dota2_monitor_screenshot(filename):
        # fallback to fullscreen screenshot
        filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
        save_fullscreen_screenshot(filename)

if __name__ == "__main__":
    load_audio_settings()
    show_audio_settings()
    main_loop()

