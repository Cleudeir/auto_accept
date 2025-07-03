import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import datetime
import logging
from typing import Callable, Optional, List, Tuple

class MainView:
    """Main GUI view for the Dota 2 Auto Accept application"""
    
    def __init__(self, title: str = "Dota 2 Auto Accept - Control Panel", config_model=None):
        self.logger = logging.getLogger("Dota2AutoAccept.MainView")
        self.window = None
        self.title = title
        self.config_model = config_model
        
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
        self.on_device_change = None
        self.on_volume_change = None
        self.on_monitor_change = None
        self.on_always_on_top_change = None
        self.on_score_threshold_change = None  # Add sensitivity callback
        self.on_closing = None
        
        # UI State
        self.is_running = False
        self.match_found = False
        self.current_match_percent = 0.0
        self.current_match_name = "none"
        
    def create_window(self):
        """Create and setup the main window with modern responsive design"""
        self.window = tk.Tk()
        self.window.title(self.title)
        self.window.configure(bg="#ffffff")  # Set app background to white

        # Modern responsive window configuration
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate responsive dimensions based on screen size and resolution
        # Ensure minimum height of 800px for all screen sizes
        if screen_height <= 768:  # Small screens (laptops, tablets)
            window_width = min(750, int(screen_width * 0.9))
            window_height = max(800, min(int(screen_height * 0.9), 800))  # Force min 800px height
            min_width, min_height = 700, 800
        elif screen_height <= 1080:  # Medium screens (1080p)
            window_width = min(850, int(screen_width * 0.85))
            window_height = max(800, min(820, int(screen_height * 0.75)))
            min_width, min_height = 800, 800
        elif screen_height <= 1440:  # High resolution screens (1440p)
            window_width = min(950, int(screen_width * 0.8))
            window_height = max(800, min(850, int(screen_height * 0.65)))
            min_width, min_height = 850, 800
        else:  # Ultra-high resolution screens (4K+)
            window_width = min(1050, int(screen_width * 0.75))
            window_height = max(800, min(900, int(screen_height * 0.6)))
            min_width, min_height = 900, 800
        
        # Smart positioning - avoid taskbars and system areas
        if screen_width > 2560:  # Ultra-wide or multi-monitor setups
            x = int(screen_width * 0.1)  # Position towards left on very wide screens
        elif screen_width > 1920:  # Wide screens
            x = int(screen_width * 0.15)  # Slightly offset from center
        else:
            x = (screen_width // 2) - (window_width // 2)  # Center on standard screens
        
        # Position slightly above center, accounting for taskbar
        y = max(30, (screen_height // 2) - (window_height // 2) - 40)
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(True, True)
        self.window.minsize(min_width, min_height)

        # Set icon
        self._set_window_icon()

        # --- Modern layout with improved spacing ---
        main_frame = tk.Frame(self.window, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left column: status, screenshot, control buttons
        self.left_col = tk.Frame(main_frame, bg="#ffffff")
        self.left_col.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Right column: settings with modern spacing
        self.right_col = tk.Frame(main_frame, bg="#ffffff", width=250)
        self.right_col.pack(side=tk.RIGHT, fill="y", padx=(8, 5), pady=5)
        self.right_col.pack_propagate(False)  # Maintain fixed width

        # Status and screenshot on left with modern layout
        self._create_status_section(parent=self.left_col)
        self._create_screenshot_section(parent=self.left_col)
        self._create_control_buttons_section(parent=self.left_col)

        # Settings permanently visible on right
        self._create_permanent_settings(parent=self.right_col)

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
        """Create modern status display section with improved visuals"""
        # Status label with modern styling
        self.status_label = tk.Label(
            parent, text="Status: Stopped", font=("Segoe UI", 11, "bold"), fg="#e53935", bg="#ffffff"
        )
        self.status_label.pack(pady=(8, 4), fill="x")
        
        # Modern card-like frame for progress bar and sensitivity
        card_frame = tk.Frame(parent, bg="#f8f9fa", bd=1, relief="solid")
        card_frame.pack(pady=(0, 6), padx=8, fill="x")
        
        # Progress bar with percent - compact and modern
        bar_frame = tk.Frame(card_frame, bg="#f8f9fa")
        bar_frame.pack(pady=(6, 3), padx=6, fill="x")
        
        self.match_percent_bar = ttk.Progressbar(
            bar_frame,
            orient="horizontal",
            length=160,  # Further reduced for compactness
            mode="determinate",
            maximum=100
        )
        self.match_percent_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.match_percent_text = tk.Label(
            bar_frame,
            text="0.0%",
            font=("Segoe UI", 8, "bold"),  # Further reduced font size
            fg="#555",
            bg="#f8f9fa",
            width=5,
            anchor="e"
        )
        self.match_percent_text.pack(side=tk.LEFT, padx=(4, 0))
        
        # Detected image name - compact
        self.match_name_label = tk.Label(
            card_frame,
            text="none",
            font=("Segoe UI", 9, "bold"),  # Further reduced font size
            fg="#1976d2",
            bg="#f8f9fa"
        )
        self.match_name_label.pack(pady=(0, 4))
        
        # Enhanced sensitivity slider with better feedback
        threshold_frame = tk.Frame(card_frame, bg="#f8f9fa")
        threshold_frame.pack(pady=(0, 6))
        tk.Label(threshold_frame, text="Threshold:", font=("Segoe UI", 8), bg="#f8f9fa", fg="#666").pack(side=tk.LEFT)
        self.score_threshold_var = tk.DoubleVar(value=70.0)
        self.score_threshold_slider = tk.Scale(
            threshold_frame,
            from_=50, to=95, resolution=1, orient=tk.HORIZONTAL,  # Updated range 50-95
            variable=self.score_threshold_var,
            command=self._on_score_threshold_change_event,
            length=80,
            showvalue=0,
            bg="#f8f9fa",
            fg="#666",
            highlightthickness=0,
            bd=0,
            troughcolor="#e0e0e0",
            activebackground="#1976d2"
        )
        self.score_threshold_slider.pack(side=tk.LEFT, padx=(4, 0))
        self.score_threshold_value_label = tk.Label(
            threshold_frame, text="70%", font=("Segoe UI", 8, "bold"), 
            bg="#f8f9fa", fg="#ff9800"  # Start with orange (medium sensitivity)
        )
        self.score_threshold_value_label.pack(side=tk.LEFT, padx=(4, 0))
    
    def _create_screenshot_section(self, parent=None):
        parent = parent or self.window
        """Create compact screenshot preview section"""
        screenshot_frame = tk.LabelFrame(
            parent, text="Screenshot", padx=0, pady=0, bg="#ffffff", 
            fg="#1976d2", font=("Segoe UI", 9, "bold"), bd=1, relief="solid"
        )
        screenshot_frame.pack(fill="both", expand=True, padx=8, pady=4)
        
        # Compact fixed height frame
        fixed_height_frame = tk.Frame(screenshot_frame, height=160, bg="#ffffff")  # Further reduced
        fixed_height_frame.pack(fill=tk.X)
        fixed_height_frame.pack_propagate(False)
        
        # Screenshot label with modern styling
        self.screenshot_label = tk.Label(
            fixed_height_frame, bg="#f5f5f5", relief="flat", bd=1
        )
        self.screenshot_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Compact timestamp label
        self.timestamp_label = tk.Label(
            screenshot_frame, font=("Segoe UI", 7), fg="#999", bg="#ffffff"
        )
        self.timestamp_label.pack(side=tk.BOTTOM, pady=(1, 2))
        # Removed screenshot controls/button from here

    def _create_control_buttons_section(self, parent=None):
        parent = parent or self.window
        """Create compact control buttons section"""
        control_frame = tk.Frame(parent, bg="#ffffff")
        control_frame.pack(fill="x", padx=5, pady=5)
        # Center the buttons vertically and horizontally
        control_frame.pack_propagate(False)
        control_frame.configure(height=60)  # Reduced from 80
        button_inner = tk.Frame(control_frame, bg="#ffffff")
        button_inner.place(relx=0.5, rely=0.5, anchor="center")
        # Compact button styling with modern look
        button_height = 1  # Reduced from 2
        button_font = ("Segoe UI", 9, "bold")  # Reduced font size
        button_config = {
            "font": button_font,
            "pady": 0,
            "height": button_height,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "highlightthickness": 0,
        }
        
        self.start_btn = tk.Button(
            button_inner,
            text="▶ Start",
            command=self._on_start_detection_click,
            bg="#43a047",
            fg="#fff",
            activebackground="#388e3c",
            activeforeground="#fff",
            padx=12,
            **button_config
        )
        self.stop_btn = tk.Button(
            button_inner,
            text="⏹ Stop",
            command=self._on_stop_detection_click,
            bg="#e53935",
            fg="#fff",
            activebackground="#b71c1c",
            activeforeground="#fff",
            padx=12,
            **button_config
        )
        self.test_sound_btn = tk.Button(
            button_inner,
            text="🎵 Sound",  # Shortened text
            command=self._on_test_sound_click,
            bg="#ff9800",
            fg="#fff",
            activebackground="#f57c00",
            activeforeground="#fff",
            padx=10,
            **button_config
        )
        self.start_btn.pack(side="left", padx=3)  # Further reduced spacing
        self.stop_btn.pack(side="left", padx=3)
        self.test_sound_btn.pack(side="left", padx=3)
        # Initial state: only show start
        self.stop_btn.pack_forget()

    def _create_audio_settings(self, parent=None):
        parent = parent or self.window
        """Create compact audio settings section"""
        audio_frame = tk.LabelFrame(parent, text="Audio", padx=0, pady=0, bg="#ffffff", fg="#43a047", font=("Segoe UI", 10, "bold"), bd=1, relief="groove")
        audio_frame.pack(fill="x", padx=5, pady=5)
        # Device selection with reduced spacing
        tk.Label(audio_frame, text="Device:", font=("Segoe UI", 9), bg="#ffffff", fg="#333").pack(pady=(5, 0), anchor="w", padx=8)
        self.device_combo = ttk.Combobox(audio_frame, state="readonly", font=("Segoe UI", 9))
        self.device_combo.pack(pady=3, padx=8, fill="x")
        self.device_combo.bind("<<ComboboxSelected>>", self._on_device_change_event)
        # Volume control with reduced spacing
        tk.Label(audio_frame, text="Volume:", font=("Segoe UI", 9), bg="#ffffff", fg="#333").pack(pady=(5, 0), anchor="w", padx=8)
        self.volume_slider = tk.Scale(
            audio_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._on_volume_change_event,
            length=120,  # Reduced from 160
            bg="#ffffff",
            highlightthickness=0,
            troughcolor="#e3e3e3",
            sliderrelief="flat"
        )
        self.volume_slider.pack(pady=3, padx=8, fill="x")
        # Removed test sound button from here

    def _create_monitor_settings(self, parent=None):
        parent = parent or self.window
        """Create compact monitor settings section"""
        monitor_frame = tk.LabelFrame(parent, text="Monitor", padx=0, pady=0, bg="#ffffff", fg="#1976d2", font=("Segoe UI", 10, "bold"), bd=1, relief="groove")
        monitor_frame.pack(fill="x", padx=5, pady=5)
        # Monitor selection with reduced spacing
        tk.Label(monitor_frame, text="Capture:", font=("Segoe UI", 9), bg="#ffffff", fg="#333").pack(pady=(5, 0), anchor="w", padx=8)
        self.monitor_combo = ttk.Combobox(monitor_frame, state="readonly", font=("Segoe UI", 9))
        self.monitor_combo.pack(pady=3, padx=8, fill="x")
        self.monitor_combo.bind("<<ComboboxSelected>>", self._on_monitor_change_event)
        # Always on top option with reduced spacing
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_check = tk.Checkbutton(
            monitor_frame,
            text="Always on top",  # Shortened text
            variable=self.always_on_top_var,
            command=self._on_always_on_top_change_event,
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#333",
            activebackground="#e3e3e3",
            selectcolor="#e3e3e3",
            highlightthickness=0
        )
        self.always_on_top_check.pack(pady=5, padx=8, anchor="w")
        
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
                # Resize image for compact preview
                img_copy = img.copy()
                width, height = img_copy.size
                
                max_width = 280  # Reduced from 360
                max_height = 180  # Reduced from 240
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
            # Create a compact empty image with fixed dimensions to maintain layout
            empty_img = Image.new('RGB', (280, 180), color=(240, 240, 240))  # Reduced from 360x240
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
            "watch-game": "Watch Game Dialog",
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
        """Handle sensitivity slider change with enhanced feedback"""
        percent = float(val)
        
        # Update percentage display
        self.score_threshold_value_label.config(text=f"{percent:.0f}%")
        
        # Color code the threshold value based on sensitivity level
        if percent <= 60:  # High sensitivity (low threshold)
            color = "#4caf50"  # Green - More detections
        elif percent <= 75:  # Medium sensitivity 
            color = "#ff9800"  # Orange - Balanced
        else:  # Low sensitivity (high threshold)
            color = "#f44336"  # Red - Strict detection
            
        self.score_threshold_value_label.config(fg=color)
        
        # Call the callback if it exists
        if hasattr(self, 'on_score_threshold_change') and self.on_score_threshold_change:
            self.on_score_threshold_change(percent / 100.0)

    def set_score_threshold(self, percent: float):
        """Set the score threshold slider value (0-1 float) with color coding"""
        value = max(50, min(95, int(percent * 100)))  # Updated range 50-95
        self.score_threshold_var.set(value)
        self.score_threshold_value_label.config(text=f"{value}%")
        
        # Apply color coding based on threshold level
        if value <= 60:  # High sensitivity (low threshold)
            color = "#4caf50"  # Green
        elif value <= 75:  # Medium sensitivity 
            color = "#ff9800"  # Orange
        else:  # Low sensitivity (high threshold)
            color = "#f44336"  # Red
            
        self.score_threshold_value_label.config(fg=color)
    
    def _create_permanent_settings(self, parent=None):
        """Create the permanently visible settings panel"""
        parent = parent or self.window
        
        # Settings header - more compact
        settings_header = tk.Label(
            parent,
            text="⚙️ Settings",
            font=("Segoe UI", 11, "bold"),  # Reduced font size
            fg="#1976d2",
            bg="#ffffff"
        )
        settings_header.pack(pady=(0, 5))  # Reduced padding
        
        # Create the settings sections
        self._create_audio_settings(parent=parent)
        self._create_monitor_settings(parent=parent)

    # ... existing methods continue below ...
