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

selected_device_id = None
alert_volume = 1.0
SETTINGS_FILE = 'alert_volume.json'
is_running = False
detection_thread = None
match_found = False

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
    global selected_device_id, alert_volume, is_running, detection_thread
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
        if os.path.exists('icon.ico'):
            win.iconbitmap('icon.ico')
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
            print("Detection started!")

    def stop_detection():
        global is_running
        is_running = False
        print("Detection stopped!")

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
    global is_running, match_found
    folder = 'debug_screenshots'
    os.makedirs(folder, exist_ok=True)
    ref1 = 'dota.png'
    ref2 = 'print.png'
    while is_running:
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
            match_found = True
            is_running = False  # Stop detection after match found
            break
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

