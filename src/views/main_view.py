import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import datetime
import logging
from typing import Callable, Optional, List, Tuple

class MainView:
    """Main GUI view for the Dota 2 Auto Accept application"""
    
    def __init__(self, title: str = "Dota 2 Auto Accept - Control Panel"):
        self.logger = logging.getLogger("Dota2AutoAccept.MainView")
        self.window = None
        self.title = title
        
        # UI Components
        self.status_label = None
        self.screenshot_label = None
        self.timestamp_label = None
        self.log_text = None
        self.start_btn = None
        self.stop_btn = None
        self.match_percent_label = None  # Add label for match %
        self.match_name_label = None     # Add label for match name
        
        # Callbacks
        self.on_start_detection = None
        self.on_stop_detection = None
        self.on_test_sound = None
        self.on_take_screenshot = None
        self.on_device_change = None
        self.on_volume_change = None
        self.on_monitor_change = None
        self.on_always_on_top_change = None
        self.on_closing = None
        
        # UI State
        self.is_running = False
        self.match_found = False
        self.current_match_percent = 0.0
        self.current_match_name = "none"
        
    def create_window(self):
        """Create and setup the main window"""
        self.window = tk.Tk()
        self.window.title(self.title)
        self.window.configure(bg="#ffffff")  # Set app background to white

        # Window configuration
        window_width = 1020  # Wider for side-by-side layout
        window_height = 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)

        # Set icon
        self._set_window_icon()

        # --- Main horizontal layout ---
        main_frame = tk.Frame(self.window, bg="#ffffff")
        main_frame.pack(fill="both", expand=True)

        # Left column: status, screenshot, control buttons
        left_col = tk.Frame(main_frame, bg="#ffffff")
        left_col.pack(side=tk.LEFT, fill="both", expand=True)
        # Right column: settings
        right_col = tk.Frame(main_frame, bg="#ffffff")
        right_col.pack(side=tk.RIGHT, fill="y", padx=(10, 18), pady=10)

        # Status and screenshot on left
        self._create_status_section(parent=left_col)
        self._create_screenshot_section(parent=left_col)
        self._create_control_buttons_section(parent=left_col)

        # Settings on right
        self._create_audio_settings(parent=right_col)
        self._create_monitor_settings(parent=right_col)

        # Keyboard shortcuts and close handler
        self._setup_keyboard_shortcuts()
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_closing)
        return self.window

    def _set_window_icon(self):
        """Set the window icon"""
        try:
            icon_path = os.path.join("bin", "icon.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except Exception as e:
            self.logger.warning(f"Could not set window icon: {e}")
    
    def _create_status_section(self, parent=None):
        parent = parent or self.window
        """Create status display section with improved visuals"""
        # Status label
        self.status_label = tk.Label(
            parent, text="Status: Stopped", font=("Segoe UI", 14, "bold"), fg="#e53935", bg="#ffffff"
        )
        self.status_label.pack(pady=(18, 8), fill="x")
        # Card-like frame for progress bar and sensitivity
        card_frame = tk.Frame(parent, bg="#ffffff", bd=2, relief="groove")
        card_frame.pack(pady=(0, 14), padx=18, fill="x")
        # Progress bar with percent
        bar_frame = tk.Frame(card_frame, bg="#ffffff")
        bar_frame.pack(pady=(12, 2), padx=10, fill="x")
        self.match_percent_bar = ttk.Progressbar(
            bar_frame,
            orient="horizontal",
            length=220,
            mode="determinate",
            maximum=100
        )
        self.match_percent_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.match_percent_text = tk.Label(
            bar_frame,
            text="0.0%",
            font=("Segoe UI", 10, "bold"),
            fg="#333",
            bg="#ffffff",
            width=7,
            anchor="e"
        )
        self.match_percent_text.pack(side=tk.LEFT, padx=(8, 0))
        # Detected image name
        self.match_name_label = tk.Label(
            card_frame,
            text="none",
            font=("Segoe UI", 12, "bold"),
            fg="#1976d2",
            bg="#ffffff"
        )
        self.match_name_label.pack(pady=(0, 8))
        # Sensitivity slider
        threshold_frame = tk.Frame(card_frame, bg="#ffffff")
        threshold_frame.pack(pady=(0, 10))
        tk.Label(threshold_frame, text="Detection Sensitivity:", font=("Segoe UI", 10), bg="#ffffff").pack(side=tk.LEFT)
        self.score_threshold_var = tk.DoubleVar(value=65.0)
        self.score_threshold_slider = tk.Scale(
            threshold_frame,
            from_=50, to=100, resolution=1, orient=tk.HORIZONTAL,
            variable=self.score_threshold_var,
            command=self._on_score_threshold_change_event,
            length=120,
            showvalue=0,
            bg="#ffffff",
            highlightthickness=0,
            troughcolor="#e3e3e3",
            sliderrelief="flat"
        )
        self.score_threshold_slider.pack(side=tk.LEFT, padx=(8, 0))
        self.score_threshold_value_label = tk.Label(threshold_frame, text="70%", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#1976d2")
        self.score_threshold_value_label.pack(side=tk.LEFT, padx=(8, 0))
    
    def _create_screenshot_section(self, parent=None):
        parent = parent or self.window
        """Create screenshot preview section with improved visuals"""
        screenshot_frame = tk.LabelFrame(parent, text="Screenshot Preview", padx=0, pady=0, bg="#ffffff", fg="#1976d2", font=("Segoe UI", 11, "bold"), bd=2, relief="groove")
        screenshot_frame.pack(fill="both", expand=True, padx=18, pady=8)
        # Fixed height frame to maintain consistent size
        fixed_height_frame = tk.Frame(screenshot_frame, height=240, bg="#ffffff")
        fixed_height_frame.pack(fill=tk.X)
        fixed_height_frame.pack_propagate(False)
        # Screenshot label
        self.screenshot_label = tk.Label(fixed_height_frame, bg="#e3e3e3", relief="ridge", bd=1)
        self.screenshot_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        # Timestamp label
        self.timestamp_label = tk.Label(screenshot_frame, font=("Segoe UI", 9), fg="#888", bg="#ffffff")
        self.timestamp_label.pack(side=tk.BOTTOM, pady=(2, 0))
        # Removed screenshot controls/button from here

    def _create_control_buttons_section(self, parent=None):
        parent = parent or self.window
        """Create start, stop, test sound, and take screenshot buttons below the settings sections, centered, with improved style"""
        control_frame = tk.Frame(parent, bg="#ffffff")
        control_frame.pack(fill="x", padx=10, pady=10)
        # Center the buttons vertically and horizontally
        control_frame.pack_propagate(False)
        control_frame.configure(height=80)  # Give enough height for vertical centering
        button_inner = tk.Frame(control_frame, bg="#ffffff")
        button_inner.place(relx=0.5, rely=0.5, anchor="center")
        # Standardize button height and font for all control buttons
        button_height = 2  # tkinter height in text lines
        button_font = ("Segoe UI", 10, "bold")
        self.start_btn = tk.Button(
            button_inner,
            text="▶ Start",
            command=self._on_start_detection_click,
            bg="#43a047",
            fg="#fff",
            activebackground="#388e3c",
            activeforeground="#fff",
            font=button_font,
            padx=20,
            pady=0,
            height=button_height,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
        )
        self.stop_btn = tk.Button(
            button_inner,
            text="⏹ Stop",
            command=self._on_stop_detection_click,
            bg="#e53935",
            fg="#fff",
            activebackground="#b71c1c",
            activeforeground="#fff",
            font=button_font,
            padx=20,
            pady=0,
            height=button_height,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
        )
        self.test_sound_btn = tk.Button(
            button_inner,
            text="🎵 Test Sound",
            command=self._on_test_sound_click,
            bg="#43a047",
            fg="#fff",
            activebackground="#388e3c",
            activeforeground="#fff",
            font=button_font,
            padx=12,
            pady=0,
            height=button_height,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
        )
        self.take_screenshot_btn = tk.Button(
            button_inner,
            text="📷 Take Screenshot",
            command=self._on_take_screenshot_click,
            bg="#1976d2",
            fg="#fff",
            activebackground="#1565c0",
            activeforeground="#fff",
            font=button_font,
            padx=12,
            pady=0,
            height=button_height,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=0,
        )
        self.start_btn.pack(side="left", padx=8)
        self.stop_btn.pack(side="left", padx=8)
        self.test_sound_btn.pack(side="left", padx=8)
        self.take_screenshot_btn.pack(side="left", padx=8)
        # Initial state: only show start
        self.stop_btn.pack_forget()

    def _create_audio_settings(self, parent=None):
        parent = parent or self.window
        """Create audio settings section with improved visuals"""
        audio_frame = tk.LabelFrame(parent, text="Audio Settings", padx=0, pady=0, bg="#ffffff", fg="#43a047", font=("Segoe UI", 11, "bold"), bd=2, relief="groove")
        audio_frame.pack(fill="x", padx=8, pady=8)
        # Device selection
        tk.Label(audio_frame, text="Output Device:", font=("Segoe UI", 10), bg="#ffffff", fg="#333").pack(pady=(8, 0), anchor="w", padx=10)
        self.device_combo = ttk.Combobox(audio_frame, state="readonly", font=("Segoe UI", 10))
        self.device_combo.pack(pady=5, padx=10, fill="x")
        self.device_combo.bind("<<ComboboxSelected>>", self._on_device_change_event)
        # Volume control
        tk.Label(audio_frame, text="Volume:", font=("Segoe UI", 10), bg="#ffffff", fg="#333").pack(pady=(10, 0), anchor="w", padx=10)
        self.volume_slider = tk.Scale(
            audio_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_volume_change_event,
            length=160,
            bg="#ffffff",
            highlightthickness=0,
            troughcolor="#e3e3e3",
            sliderrelief="flat"
        )
        self.volume_slider.pack(pady=5, padx=10, fill="x")
        # Removed test sound button from here

    def _create_monitor_settings(self, parent=None):
        parent = parent or self.window
        """Create monitor settings section with improved visuals"""
        monitor_frame = tk.LabelFrame(parent, text="Monitor Settings", padx=0, pady=0, bg="#ffffff", fg="#1976d2", font=("Segoe UI", 11, "bold"), bd=2, relief="groove")
        monitor_frame.pack(fill="x", padx=8, pady=8)
        # Monitor selection
        tk.Label(monitor_frame, text="Capture Monitor:", font=("Segoe UI", 10), bg="#ffffff", fg="#333").pack(pady=(8, 0), anchor="w", padx=10)
        self.monitor_combo = ttk.Combobox(monitor_frame, state="readonly", font=("Segoe UI", 10))
        self.monitor_combo.pack(pady=5, padx=10, fill="x")
        self.monitor_combo.bind("<<ComboboxSelected>>", self._on_monitor_change_event)
        # Always on top option
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_check = tk.Checkbutton(
            monitor_frame,
            text="Keep window on top",
            variable=self.always_on_top_var,
            command=self._on_always_on_top_change_event,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#333",
            activebackground="#e3e3e3",
            selectcolor="#e3e3e3",
            highlightthickness=0
        )
        self.always_on_top_check.pack(pady=8, padx=10, anchor="w")
        
    def _create_log_section(self):
        """Create log viewer section"""
        log_frame = tk.LabelFrame(self.window, text="Log Viewer", padx=10, pady=10)
        log_frame.pack(fill="x", padx=10, pady=5)
        
        # Text widget for logs
        self.log_text = tk.Text(log_frame, height=6, width=50, font=("Consolas", 8))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Make read-only
        self.log_text.config(state=tk.DISABLED)
   
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        def on_key_press(event):
            if event.keysym == "F1" and not self.is_running:
                self._on_start_detection_click()
            elif event.keysym == "F2" and self.is_running:
                self._on_stop_detection_click()
            elif event.keysym == "F3":
                self._on_test_sound_click()
            elif event.keysym == "F4":
                self._on_take_screenshot_click()
                
        self.window.bind("<KeyPress>", on_key_press)
        self.window.focus_set()
    
    # Event handlers
    def _on_start_detection_click(self):
        if self.on_start_detection:
            self.on_start_detection()
    
    def _on_stop_detection_click(self):
        if self.on_stop_detection:
            self.on_stop_detection()
    
    def _on_test_sound_click(self):
        if self.on_test_sound:
            self.on_test_sound()
    
    def _on_take_screenshot_click(self):
        if self.on_take_screenshot:
            self.on_take_screenshot()
    
    def _on_device_change_event(self, event=None):
        if self.on_device_change:
            idx = self.device_combo.current()
            self.on_device_change(idx)
    
    def _on_volume_change_event(self, val):
        if self.on_volume_change:
            self.on_volume_change(int(val))
    
    def _on_monitor_change_event(self, event=None):
        if self.on_monitor_change:
            idx = self.monitor_combo.current()
            self.on_monitor_change(idx)
    
    def _on_always_on_top_change_event(self):
        if self.on_always_on_top_change:
            self.on_always_on_top_change(self.always_on_top_var.get())
    
    def _on_window_closing(self):
        if self.on_closing:
            self.on_closing()
        if self.window:
            self.window.destroy()
    
    # Public methods for updating UI
    def set_status(self, text: str, color: str = "black"):
        """Update status label"""
        if self.status_label:            self.status_label.config(text=text, fg=color)
    
    def set_detection_state(self, is_running: bool, match_found: bool = False):
        """Update detection state and UI for control buttons (no pause)"""
        self.is_running = is_running
        self.match_found = match_found
        if is_running:
            self.set_status("Status: Running Detection", "green")
            self.start_btn.pack_forget()
            self.stop_btn.pack(side="left", padx=5)
        elif match_found:
            self.set_status("Status: Match Found! Detection Stopped", "blue")
            self.stop_btn.pack_forget()
            self.start_btn.pack(side="left", padx=5)
        else:
            self.set_status("Status: Stopped", "red")
            self.stop_btn.pack_forget()
            self.start_btn.pack(side="left", padx=5)

    def update_screenshot(self, img: Optional[Image.Image], timestamp: Optional[datetime.datetime] = None):
        """Update screenshot preview"""
        if img is not None:
            try:
                # Resize image for preview
                img_copy = img.copy()
                width, height = img_copy.size
                
                max_width = 360
                max_height = 240
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                img_copy = img_copy.resize((new_width, new_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img_copy)
                
                self.screenshot_label.config(image=photo, text="")
                self.screenshot_label.image = photo  # Keep reference
                
                # Update timestamp
                if timestamp:
                    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    self.timestamp_label.config(text=f"Captured: {timestamp_str}")
                else:
                    self.timestamp_label.config(text="")
            except Exception as e:
                self.logger.error(f"Error displaying screenshot: {e}")
                self.screenshot_label.config(image=None, text=f"Error: {str(e)}")
                self.timestamp_label.config(text="")
        else:
            # Create an empty image with fixed dimensions to maintain layout
            empty_img = Image.new('RGB', (360, 240), color=(240, 240, 240))
            photo = ImageTk.PhotoImage(empty_img)
            self.screenshot_label.config(image=photo, text="No screenshot available")
            self.screenshot_label.image = photo  # Keep reference
            self.timestamp_label.config(text="")
    
    def update_logs(self, log_content: str):
        """Update log viewer content"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, log_content)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def set_device_options(self, devices: List[str], selected_index: int = 0):
        """Set audio device options (output devices only, no duplicates, no similar names)"""
        if self.device_combo:
            import re
            seen = set()
            unique_devices = []
            for d in devices:
                # Normalize: remove content in parentheses and trim
                base = re.sub(r"\s*\(.*?\)", "", d).strip().lower()
                if base not in seen:
                    seen.add(base)
                    unique_devices.append(d)
            self.device_combo['values'] = unique_devices
            if 0 <= selected_index < len(unique_devices):
                self.device_combo.current(selected_index)
    
    def set_monitor_options(self, monitors: List[str], selected_index: int = 0):
        """Set monitor options"""
        if self.monitor_combo:
            self.monitor_combo['values'] = monitors
            if 0 <= selected_index < len(monitors):
                self.monitor_combo.current(selected_index)
    
    def set_volume(self, volume: int):
        """Set volume slider value"""
        if self.volume_slider:
            self.volume_slider.set(volume)
    
    def set_always_on_top(self, always_on_top: bool):
        """Set always on top checkbox and window property"""
        if self.always_on_top_var:
            self.always_on_top_var.set(always_on_top)
        if self.window:
            self.window.attributes("-topmost", always_on_top)
    
    def show_error(self, title: str, message: str):
        """Show error message box"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info message box"""
        messagebox.showinfo(title, message)
    
    def mainloop(self):
        """Start the GUI main loop"""
        if self.window:
            self.window.mainloop()
    
    def after(self, delay: int, callback: Callable):
        """Schedule a callback after delay milliseconds"""
        if self.window:
            self.window.after(delay, callback)
    
    def set_match_percent_and_name(self, percent: float, name: str):
        """Update match percent bar, percent text, and detected image name only"""
        self.current_match_percent = percent
        self.current_match_name = name
        if self.match_percent_bar:
            self.match_percent_bar['value'] = percent
            # Color bar: green >80, yellow >60, orange >40, red else
            if percent >= 80:
                color = '#4caf50'  # green
            elif percent >= 60:
                color = '#ffc107'  # yellow
            elif percent >= 40:
                color = '#ff9800'  # orange
            else:
                color = '#f44336'  # red
            style = ttk.Style()
            style.theme_use('default')
            style.configure("Custom.Horizontal.TProgressbar", troughcolor='#e0e0e0', background=color)
            self.match_percent_bar.config(style="Custom.Horizontal.TProgressbar")
            # Update percent text to the right of the bar
            self.match_percent_text.config(text=f"{percent:.1f}%")
        if self.match_name_label:
            self.match_name_label.config(text=self._get_match_display_name(name))

    def _get_match_display_name(self, name: str) -> str:
        """Return a user-friendly display name for each match type"""
        mapping = {
            "dota": "Match Found!",
            "dota2_plus": "Dota Plus Offer",
            "read_check": "Read-Check Confirmation",
            "long_time": "Long Wait Warning",
            "ad": "Advertisement",
            "none": "No Match Detected"
        }
        return mapping.get(name, name)

    def _get_match_description(self, name: str) -> str:
        """Return a descriptive text for each match type"""
        mapping = {
            "dota": "A Dota 2 match has been found. Ready to accept!",
            "dota2_plus": "Dota Plus subscription dialog detected.",
            "read_check": "Read-check dialog detected. Please confirm to continue.",
            "long_time": "Long matchmaking wait dialog detected.",
            "ad": "Advertisement detected on screen.",
            "none": "No known pattern detected."
        }
        return mapping.get(name, "Unknown pattern.")
    
    def _on_score_threshold_change_event(self, val):
        percent = float(val)
        self.score_threshold_value_label.config(text=f"{percent:.0f}%")
        if hasattr(self, 'on_score_threshold_change') and self.on_score_threshold_change:
            self.on_score_threshold_change(percent / 100.0)

    def set_score_threshold(self, percent: float):
        """Set the score threshold slider value (0-1 float)"""
        value = max(50, min(100, int(percent * 100)))
        self.score_threshold_var.set(value)
        self.score_threshold_value_label.config(text=f"{value}%")
