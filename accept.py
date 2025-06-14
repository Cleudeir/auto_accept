import pyautogui
import cv2
import numpy as np
import time
import pygetwindow as gw
from PIL import ImageGrab, Image, ImageTk
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
import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Set up logging configuration
log_file = os.path.join("logs", "dota2_auto_accept.log")
logger = logging.getLogger("Dota2AutoAccept")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    log_file, maxBytes=1024 * 1024, backupCount=5
)  # 1MB file size, keep 5 backups
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

selected_device_id = None
alert_volume = 1.0
SETTINGS_FILE = "config.json"  # Changed from 'alert_volume.json'
selected_monitor_capture_setting = 1  # Default to monitor 1
always_on_top = True
is_running = False
detection_thread = None
match_found = False
latest_screenshot_img = None  # Global variable to hold the latest screenshot image
latest_screenshot_time = None  # Global variable to hold the time of the latest screenshot


def save_fullscreen_screenshot(filename):
    screenshot = pyautogui.screenshot()
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, screenshot_np)
    logger.info(f"Fullscreen screenshot saved to {filename}")


def save_dota2_window_screenshot(filename):
    windows = gw.getWindowsWithTitle("Dota 2")
    if not windows:
        logger.warning("Dota 2 window not found!")
        return False
    win = windows[0]
    if win.isMinimized:
        logger.warning("Dota 2 window is minimized!")
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
        if (
            not monitors or len(monitors) <= 1
        ):  # Need at least one actual monitor besides the combined one
            logger.warning("No distinct monitors found by mss to capture from!")
            return False

        # Validate target_monitor_index (it's 1-based for user, so it maps to monitors[target_monitor_index])
        if not isinstance(target_monitor_index, int) or not (
            0 < target_monitor_index < len(monitors)
        ):
            logger.warning(
                f"Invalid monitor index {target_monitor_index} specified. Available: 1 to {len(monitors)-1}. Screenshot not taken."
            )
            return False

        monitor_to_capture = monitors[target_monitor_index]

        try:
            img = sct.grab(monitor_to_capture)
            # mss grabs in BGRA, convert to BGR for OpenCV compatibility and to avoid alpha channel issues
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            cv2.imwrite(filename, img_bgr)
            logger.info(
                f"Screenshot of Monitor {target_monitor_index} saved to {filename}"
            )
            return True
        except mss.exception.ScreenShotError as e:
            logger.error(
                f"Error capturing screenshot from Monitor {target_monitor_index} using mss: {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while capturing/saving screenshot from Monitor {target_monitor_index}: {e}"
            )
            return False


def capture_dota2_monitor_screenshot(target_monitor_index: int):
    # Captures the selected monitor directly and returns the image (PIL Image)
    global latest_screenshot_time
    with mss.mss() as sct:
        monitors = sct.monitors
        if not monitors or len(monitors) <= 1:
            logger.warning("No distinct monitors found by mss to capture from!")
            return None
        if not isinstance(target_monitor_index, int) or not (0 < target_monitor_index < len(monitors)):
            logger.warning(
                f"Invalid monitor index {target_monitor_index} specified. Available: 1 to {len(monitors)-1}. Screenshot not taken."
            )
            return None
        monitor = monitors[target_monitor_index]
        try:
            sct_img = sct.grab(monitor)
            img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
            latest_screenshot_time = datetime.datetime.now()
            return img
        except Exception as e:
            logger.error(f"An unexpected error occurred while capturing screenshot from Monitor {target_monitor_index}: {e}")
            return None


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
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".png")]
    files.sort(key=os.path.getmtime, reverse=True)
    for f in files[n:]:
        os.remove(f)


def play_alert_sound():
    try:
        import pygame
        import time as _time

        mp3_path = os.path.join("bin", "dota2.mp3")
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
        if d["max_output_channels"] > 0:
            output_devices.append({"id": i, "name": d["name"]})
    return output_devices


def get_available_monitors():
    monitor_options = []  # No "Auto-detect"
    try:
        with mss.mss() as sct:
            # sct.monitors[0] is the full virtual screen, physical monitors start at index 1
            if len(sct.monitors) > 1:
                for i, monitor in enumerate(sct.monitors[1:], start=1):
                    monitor_options.append(
                        (f"Monitor {i} ({monitor['width']}x{monitor['height']})", i)
                    )
            else:
                logger.warning(
                    "No individual monitors detected by mss, only the combined virtual screen."
                )
    except Exception as e:
        logger.error(f"Error getting monitor list: {e}")
    return monitor_options


def test_alert_sound():
    try:
        import pygame
        import time as _time

        mp3_path = os.path.join("bin", "dota2.mp3")
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
    global selected_device_id, alert_volume, selected_monitor_capture_setting, always_on_top
    # Set defaults before trying to load
    selected_monitor_capture_setting = 1  # Default to monitor 1
    alert_volume = 1.0
    selected_device_id = None
    always_on_top = False  # Default to not always on top

    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                alert_volume = float(data.get("alert_volume", 1.0))
                selected_device_id = data.get("selected_device_id", None)
                loaded_monitor_setting = data.get("selected_monitor_capture_setting", 1)
                if (
                    isinstance(loaded_monitor_setting, int)
                    and loaded_monitor_setting > 0
                ):
                    # We'll validate if this index is currently available in show_audio_settings
                    selected_monitor_capture_setting = loaded_monitor_setting
                else:
                    logger.warning(
                        f"Invalid monitor setting '{loaded_monitor_setting}' in config. Defaulting to Monitor 1."
                    )
                    selected_monitor_capture_setting = 1

                always_on_top = data.get("always_on_top", False)
        else:
            logger.info(
                f"Settings file {SETTINGS_FILE} not found. Using default settings."
            )
            # Defaults are already set above

    except Exception as e:
        logger.error(
            f"Error loading settings from {SETTINGS_FILE}: {e}. Using default values."
        )
        # Defaults are already set above


def save_audio_settings():
    global selected_monitor_capture_setting, alert_volume, selected_device_id, always_on_top
    try:
        data = {
            "alert_volume": alert_volume,
            "selected_device_id": selected_device_id,
            "selected_monitor_capture_setting": selected_monitor_capture_setting,  # This will be an int
            "always_on_top": always_on_top,
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")


def show_audio_settings():
    global selected_device_id, alert_volume, is_running, detection_thread, selected_monitor_capture_setting, always_on_top, latest_screenshot_img, latest_screenshot_time

    win = tk.Tk()
    win.title("Dota 2 Auto Accept - Control Panel")

    # Center window on screen
    window_width = 420  # Increased width
    window_height = 900  # Increased height
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")
    win.resizable(False, False)

    # Set window to always stay on top
    win.attributes("-topmost", always_on_top)

    # Try to set the icon
    try:
        icon_path = os.path.join("bin", "icon.ico")
        if os.path.exists(icon_path):
            win.iconbitmap(icon_path)
    except:
        pass
        
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
    status_label = tk.Label(
        win, text="Status: Stopped", font=("Arial", 12, "bold"), fg="red"
    )
    status_label.pack(pady=(10, 5))

    # Create left and right frames for layout
    main_frame = tk.Frame(win)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill="both", expand=True)
    
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill="both", expand=True)

    # Screenshot preview frame - Now positioned at the top for prominence
    screenshot_frame = tk.LabelFrame(win, text="Screenshot Preview", padx=10, pady=10)
    screenshot_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Create a label for displaying the image
    screenshot_label = tk.Label(screenshot_frame)
    screenshot_label.pack(fill=tk.BOTH, expand=True)

    # Label to display timestamp
    timestamp_label = tk.Label(screenshot_frame, font=("Arial", 8), fg="gray")
    timestamp_label.pack(side=tk.BOTTOM, pady=(2, 0))

    # Screenshot controls
    screenshot_controls = tk.Frame(screenshot_frame)
    screenshot_controls.pack(fill="x", pady=(5, 0))

    def take_manual_screenshot():
        global latest_screenshot_img, latest_screenshot_time
        img = capture_dota2_monitor_screenshot(selected_monitor_capture_setting)
        if img is not None:
            latest_screenshot_img = img
            latest_screenshot_time = datetime.datetime.now()
            update_screenshot_preview()
            logger.info("Manual screenshot taken")
        else:
            logger.warning("Manual screenshot failed")
            messagebox.showerror("Screenshot Error", "Failed to capture screenshot")

    take_screenshot_btn = tk.Button(
        screenshot_controls,
        text="📷 Take Screenshot",
        command=take_manual_screenshot
    )
    take_screenshot_btn.pack(side=tk.LEFT, padx=2)

    def update_screenshot_preview():
        if 'latest_screenshot_img' in globals() and latest_screenshot_img is not None:
            try:
                img = latest_screenshot_img.copy()
                width, height = img.size
                
                # Calculate new dimensions to fit in the preview (larger than before)
                max_width = 360
                max_height = 240
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)

                img = img.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                # Update the label
                screenshot_label.config(image=photo)
                screenshot_label.image = photo  # Keep a reference to prevent garbage collection
                
                # Update timestamp
                if latest_screenshot_time:
                    timestamp_str = latest_screenshot_time.strftime("%Y-%m-%d %H:%M:%S")
                    timestamp_label.config(text=f"Captured: {timestamp_str}")
                else:
                    timestamp_label.config(text="")
            except Exception as e:
                logger.error(f"Error displaying screenshot: {e}")
                screenshot_label.config(image=None, text=f"Error: {str(e)}")
                timestamp_label.config(text="")
        else:
            screenshot_label.config(image=None, text="No screenshot available")
            timestamp_label.config(text="")

    def periodic_update():
        update_screenshot_preview()
        win.after(1000, periodic_update)  # Update every second instead of 2 seconds

    # Audio settings frame (moved to left frame)
    audio_frame = tk.LabelFrame(left_frame, text="Audio Settings", padx=10, pady=10)
    audio_frame.pack(fill="x", padx=5, pady=5)
    
    devices = get_output_devices()
    device_names = [d["name"] for d in devices]
    current_device = tk.StringVar()
    # Try to restore last used device
    initial_idx = 0
    if devices:
        if selected_device_id is not None:
            for i, d in enumerate(devices):
                if d["id"] == selected_device_id:
                    initial_idx = i
                    break
            else:
                initial_idx = 0
                selected_device_id = devices[0]["id"]
        else:
            initial_idx = 0
            selected_device_id = devices[0]["id"]
        current_device.set(device_names[initial_idx])

    def on_device_change(event=None):
        nonlocal devices
        idx = combo.current()
        if 0 <= idx < len(devices):
            global selected_device_id
            selected_device_id = devices[idx]["id"]
            save_audio_settings()

    def on_volume_change(val):
        global alert_volume
        alert_volume = int(val) / 100.0
        save_audio_settings()

    tk.Label(audio_frame, text="Output Device:").pack(pady=(5, 0))
    combo = ttk.Combobox(audio_frame, values=device_names, state="readonly")
    combo.pack(pady=5)
    combo.current(initial_idx)
    combo.bind("<<ComboboxSelected>>", on_device_change)

    tk.Label(audio_frame, text="Volume:").pack(pady=(10, 0))
    slider = tk.Scale(
        audio_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=on_volume_change
    )
    slider.set(int(alert_volume * 100))
    slider.pack(pady=5)

    test_btn = tk.Button(audio_frame, text="🎵 Test Sound", command=test_alert_sound)
    test_btn.pack(pady=5)

    # Monitor settings frame (moved to right frame)
    monitor_frame = tk.LabelFrame(right_frame, text="Monitor Settings", padx=10, pady=10)
    monitor_frame.pack(fill="x", padx=5, pady=5)

    # Monitor selection
    monitors_available = get_available_monitors()
    monitor_display_names = [m[0] for m in monitors_available]
    current_monitor_setting_tk = tk.StringVar()

    initial_monitor_idx = 0  # Default to the first in the list if available

    if monitors_available:
        found_saved_setting = False
        for i, (_, monitor_val_from_list) in enumerate(monitors_available):
            if monitor_val_from_list == selected_monitor_capture_setting:
                initial_monitor_idx = i
                found_saved_setting = True
                break

        if not found_saved_setting:
            logger.warning(
                f"Previously selected monitor {selected_monitor_capture_setting} is not currently available or invalid. Defaulting to Monitor {monitors_available[0][1]}."
            )
            initial_monitor_idx = 0
            selected_monitor_capture_setting = monitors_available[0][1]
            save_audio_settings()

        current_monitor_setting_tk.set(monitor_display_names[initial_monitor_idx])
    else:
        current_monitor_setting_tk.set("No monitors available")
        selected_monitor_capture_setting = -1

    def on_monitor_select(event=None):
        nonlocal monitors_available
        idx = monitor_combo.current()
        if monitors_available and 0 <= idx < len(monitors_available):
            global selected_monitor_capture_setting
            selected_monitor_capture_setting = monitors_available[idx][1]
            save_audio_settings()
            logger.info(
                f"Monitor capture setting changed to: Monitor {selected_monitor_capture_setting}"
            )
        elif not monitors_available:
            logger.warning("No monitors to select.")

    tk.Label(monitor_frame, text="Capture Monitor:").pack(pady=(5, 0))
    monitor_combo = ttk.Combobox(
        monitor_frame,
        textvariable=current_monitor_setting_tk,
        values=monitor_display_names,
        state="readonly",
    )

    if not monitors_available:
        monitor_combo.config(state="disabled")

    monitor_combo.pack(pady=5)

    if monitors_available:
        monitor_combo.current(initial_monitor_idx)

    monitor_combo.bind("<<ComboboxSelected>>", on_monitor_select)

    # Always on top option
    always_on_top_var = tk.BooleanVar(value=always_on_top)

    def toggle_always_on_top():
        global always_on_top
        always_on_top = always_on_top_var.get()
        win.attributes("-topmost", always_on_top)
        save_audio_settings()
        logger.info(f"Always on top set to: {always_on_top}")

    always_on_top_check = tk.Checkbutton(
        monitor_frame,
        text="Keep window on top",
        variable=always_on_top_var,
        command=toggle_always_on_top,
    )
    always_on_top_check.pack(pady=5)

    # Control buttons frame
    control_frame = tk.LabelFrame(win, text="Detection Control", padx=10, pady=10)
    control_frame.pack(fill="x", padx=10, pady=5)

    button_frame = tk.Frame(control_frame)
    button_frame.pack()

    start_btn = tk.Button(
        button_frame,
        text="▶ Start Detection",
        command=start_detection,
        bg="green",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=5,
    )
    start_btn.pack(side="left", padx=5)

    stop_btn = tk.Button(
        button_frame,
        text="⏹ Stop Detection",
        command=stop_detection,
        bg="red",
        fg="white",
        font=("Arial", 10, "bold"),
        padx=20,
        pady=5,
        state="disabled",
    )
    stop_btn.pack(side="left", padx=5)

    def update_status():
        if is_running:
            status_label.config(text="Status: Running Detection", fg="green")
            start_btn.pack_forget()
            stop_btn.pack(side="left", padx=5)
            stop_btn.config(state="normal", text="⏹ Stop Detection", bg="red")
        elif match_found:
            status_label.config(
                text="Status: Match Found! Detection Stopped", fg="blue"
            )
            stop_btn.pack_forget()
            start_btn.pack(side="left", padx=5)
            start_btn.config(state="normal", text="▶ Start New Detection", bg="green")
        else:
            status_label.config(text="Status: Stopped", fg="red")
            stop_btn.pack_forget()
            start_btn.pack(side="left", padx=5)
            start_btn.config(state="normal", text="▶ Start Detection", bg="green")
        win.after(500, update_status)  # Update every 500ms

    # Log viewer frame
    log_frame = tk.LabelFrame(win, text="Log Viewer", padx=10, pady=10)
    log_frame.pack(fill="x", padx=10, pady=5)

    # Create a text widget for displaying logs
    log_text = tk.Text(log_frame, height=6, width=50, font=("Consolas", 8))
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar
    scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)

    # Configure the text widget to be read-only
    log_text.config(state=tk.DISABLED)

    def refresh_logs():
        # Trim log file periodically to prevent it from growing too large
        keep_log_file_size(log_file, 1000)

        if os.path.exists(log_file):
            try:
                # Read the last 20 lines from the log file
                with open(log_file, "r") as f:
                    lines = f.readlines()
                    last_lines = lines[-20:] if len(lines) > 20 else lines

                # Update the text widget
                log_text.config(state=tk.NORMAL)
                log_text.delete(1.0, tk.END)
                log_text.insert(tk.END, "".join(last_lines))
                log_text.see(tk.END)  # Scroll to the end
                log_text.config(state=tk.DISABLED)
            except Exception as e:
                log_text.config(state=tk.NORMAL)
                log_text.delete(1.0, tk.END)
                log_text.insert(tk.END, f"Error reading log file: {str(e)}")
                log_text.config(state=tk.DISABLED)

        # Schedule the next refresh
        win.after(1000, refresh_logs)  # Refresh every 1 second

    # Log controls for log viewer
    log_controls_frame = tk.Frame(log_frame)
    log_controls_frame.pack(fill="x", pady=(5, 0))

    refresh_btn = tk.Button(
        log_controls_frame, text="🔄 Refresh", command=lambda: refresh_logs()
    )
    refresh_btn.pack(side=tk.LEFT, padx=2)

    clear_btn = tk.Button(
        log_controls_frame,
        text="🗑️ Clear",
        command=lambda: log_text.config(state=tk.NORMAL)
        or log_text.delete(1.0, tk.END)
        or log_text.config(state=tk.DISABLED),
    )
    clear_btn.pack(side=tk.LEFT, padx=2)

    # Info frame with instructions
    info_frame = tk.Frame(win)
    info_frame.pack(fill="x", padx=10, pady=5)

    info_text = "Instructions:\n• Start detection before launching Dota 2\n• Detection stops automatically after finding a match\n• Use Test Sound to verify your audio settings\n\nKeyboard Shortcuts: F1=Start | F2=Stop | F3=Test Sound | F4=Manual Screenshot"
    info_label = tk.Label(
        info_frame, text=info_text, font=("Arial", 8), fg="gray", justify="left"
    )
    info_label.pack()

    # Keyboard shortcuts
    def on_key_press(event):
        if event.keysym == "F1":  # F1 to start
            if not is_running:
                start_detection()
        elif event.keysym == "F2":  # F2 to stop
            if is_running:
                stop_detection()
        elif event.keysym == "F3":  # F3 to test sound
            test_alert_sound()
        elif event.keysym == "F4":  # F4 to take screenshot
            take_manual_screenshot()

    win.bind("<KeyPress>", on_key_press)
    win.focus_set()  # Make sure window can receive key events

    # Call refresh_logs initially to populate the log viewer
    refresh_logs()
    # Start periodic screenshot update
    periodic_update()
    # Start status update
    update_status()
    
    win.mainloop()


def keep_log_file_size(log_file_path, max_lines=1000):
    """
    Keeps the log file from growing too large by limiting the number of lines.
    Only keeps the most recent lines up to max_lines.
    """
    if not os.path.exists(log_file_path):
        return

    try:
        # Read all lines from the log file
        with open(log_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # If the number of lines exceeds the maximum, keep only the most recent ones
        if len(lines) > max_lines:
            with open(log_file_path, "w", encoding="utf-8") as file:
                file.writelines(lines[-max_lines:])
            logger.info(f"Log file trimmed to {max_lines} lines")
    except Exception as e:
        # Don't log this to avoid potential infinite recursion
        print(f"Error trimming log file: {e}")


def compare_image_with_reference(img, ref_path):
    """Compare a PIL Image directly with a reference image file path"""
    try:
        # Convert PIL Image to numpy array for OpenCV
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # Load reference image
        ref_img = cv2.imread(ref_path)
        
        if ref_img is None:
            logger.error(f"Failed to load reference image: {ref_path}")
            return 0.0
            
        # Resize reference to match captured image
        ref_img = cv2.resize(ref_img, (img_bgr.shape[1], img_bgr.shape[0]))
        
        # Convert both to grayscale for comparison
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
        
        # Compute SSIM between the two images
        score, _ = ssim(img_gray, ref_gray, full=True)
        return score
    except Exception as e:
        logger.error(f"Error comparing images: {e}")
        return 0.0


def main_loop():
    global is_running, match_found, selected_monitor_capture_setting, latest_screenshot_img, latest_screenshot_time
    ref1 = os.path.join("bin", "dota.png")
    ref2 = os.path.join("bin", "print.png")
    ref3 = os.path.join("bin", "read-check.jpg")
    logger.info("Detection loop started")
    keep_log_file_size(log_file, 1000)
    while is_running:
        img = capture_dota2_monitor_screenshot(selected_monitor_capture_setting)
        if img is not None:
            latest_screenshot_img = img.copy()  # Store for GUI
            
            # Compare directly with reference images
            sim1 = compare_image_with_reference(img, ref1)
            sim2 = compare_image_with_reference(img, ref2)
            sim3 = compare_image_with_reference(img, ref3)
            
            logger.info(
                f"Comparing monitor screenshot with reference images. Similarity scores: "
                f"dota.png={sim1:.2f}, print.png={sim2:.2f}, read-check.jpg={sim3:.2f}"
            )
            
            dota_windows = gw.getWindowsWithTitle("Dota 2")
            if sim3 > 0.8:
                pyautogui.press("enter")
            if sim1 > 0.8 or sim2 > 0.8:
                logger.info(
                    "Match detected! Focusing Dota 2 window, pressing Enter and playing sound."
                )
                play_alert_sound()
                dota_windows = gw.getWindowsWithTitle("Dota 2")
                if dota_windows:
                    try:
                        dota_window = dota_windows[0]
                        if dota_window.isMinimized:
                            dota_window.restore()
                        dota_window.activate()
                        logger.info("Successfully focused Dota 2 window")
                    except Exception as e:
                        logger.warning(f"Error focusing Dota 2 window: {e}")
                else:
                    logger.warning("Could not find Dota 2 window to focus")
                pyautogui.press("enter")
                match_found = True
                is_running = False
                break
        else:
            logger.warning("Monitor capture failed for this iteration. Will retry.")
        time.sleep(5)
    logger.info("Detection loop ended")


def main():
    filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
    if not save_dota2_monitor_screenshot(filename, selected_monitor_capture_setting):
        # fallback to fullscreen screenshot
        filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
        save_fullscreen_screenshot(filename)


if __name__ == "__main__":
    logger.info("Application starting")
    # Trim log file to prevent it from growing too large
    keep_log_file_size(log_file, 1000)
    load_audio_settings()
    is_running = True
    match_found = False
    detection_thread = threading.Thread(target=main_loop, daemon=True)
    detection_thread.start()
    show_audio_settings()
    logger.info("Application exiting")


def keep_log_file_size(log_file_path, max_lines=1000):
    """
    Keeps the log file from growing too large by limiting the number of lines.
    Only keeps the most recent lines up to max_lines.
    """
    if not os.path.exists(log_file_path):
        return

    try:
        # Read all lines from the log file
        with open(log_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # If the number of lines exceeds the maximum, keep only the most recent ones
        if len(lines) > max_lines:
            with open(log_file_path, "w", encoding="utf-8") as file:
                file.writelines(lines[-max_lines:])
            logger.info(f"Log file trimmed to {max_lines} lines")
    except Exception as e:
        # Don't log this to avoid potential infinite recursion
        print(f"Error trimming log file: {e}")
