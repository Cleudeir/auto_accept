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
        
    def create_window(self):
        """Create and setup the main window"""
        self.window = tk.Tk()
        self.window.title(self.title)
        
        # Window configuration
        window_width = 420
        window_height = 900
        
        # Center window on screen
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.resizable(False, False)
        
        # Set icon
        self._set_window_icon()
        
        # Setup window components
        self._create_status_section()
        self._create_screenshot_section()
        self._create_settings_sections()
        self._create_control_section()
        self._create_log_section()
        self._create_info_section()
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Setup window close handler
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
    
    def _create_status_section(self):
        """Create status display section"""
        self.status_label = tk.Label(
            self.window, 
            text="Status: Stopped", 
            font=("Arial", 12, "bold"), 
            fg="red"
        )
        self.status_label.pack(pady=(10, 5))
    
    def _create_screenshot_section(self):
        """Create screenshot preview section"""
        screenshot_frame = tk.LabelFrame(self.window, text="Screenshot Preview", padx=10, pady=10)
        screenshot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Screenshot label
        self.screenshot_label = tk.Label(screenshot_frame)
        self.screenshot_label.pack(fill=tk.BOTH, expand=True)
        
        # Timestamp label
        self.timestamp_label = tk.Label(screenshot_frame, font=("Arial", 8), fg="gray")
        self.timestamp_label.pack(side=tk.BOTTOM, pady=(2, 0))
        
        # Screenshot controls
        screenshot_controls = tk.Frame(screenshot_frame)
        screenshot_controls.pack(fill="x", pady=(5, 0))
        
        take_screenshot_btn = tk.Button(
            screenshot_controls,
            text="📷 Take Screenshot",
            command=self._on_take_screenshot_click
        )
        take_screenshot_btn.pack(side=tk.LEFT, padx=2)
    
    def _create_settings_sections(self):
        """Create settings sections"""
        # Main frame for settings
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill="both", expand=True)
        
        # Audio settings
        self._create_audio_settings(left_frame)
        
        # Monitor settings
        self._create_monitor_settings(right_frame)
    
    def _create_audio_settings(self, parent):
        """Create audio settings section"""
        audio_frame = tk.LabelFrame(parent, text="Audio Settings", padx=10, pady=10)
        audio_frame.pack(fill="x", padx=5, pady=5)
        
        # Device selection
        tk.Label(audio_frame, text="Output Device:").pack(pady=(5, 0))
        self.device_combo = ttk.Combobox(audio_frame, state="readonly")
        self.device_combo.pack(pady=5)
        self.device_combo.bind("<<ComboboxSelected>>", self._on_device_change_event)
        
        # Volume control
        tk.Label(audio_frame, text="Volume:").pack(pady=(10, 0))
        self.volume_slider = tk.Scale(
            audio_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL, 
            command=self._on_volume_change_event
        )
        self.volume_slider.pack(pady=5)
        
        # Test sound button
        test_btn = tk.Button(audio_frame, text="🎵 Test Sound", command=self._on_test_sound_click)
        test_btn.pack(pady=5)
    
    def _create_monitor_settings(self, parent):
        """Create monitor settings section"""
        monitor_frame = tk.LabelFrame(parent, text="Monitor Settings", padx=10, pady=10)
        monitor_frame.pack(fill="x", padx=5, pady=5)
        
        # Monitor selection
        tk.Label(monitor_frame, text="Capture Monitor:").pack(pady=(5, 0))
        self.monitor_combo = ttk.Combobox(monitor_frame, state="readonly")
        self.monitor_combo.pack(pady=5)
        self.monitor_combo.bind("<<ComboboxSelected>>", self._on_monitor_change_event)
        
        # Always on top option
        self.always_on_top_var = tk.BooleanVar()
        self.always_on_top_check = tk.Checkbutton(
            monitor_frame,
            text="Keep window on top",
            variable=self.always_on_top_var,
            command=self._on_always_on_top_change_event
        )
        self.always_on_top_check.pack(pady=5)
    
    def _create_control_section(self):
        """Create detection control section"""
        control_frame = tk.LabelFrame(self.window, text="Detection Control", padx=10, pady=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        button_frame = tk.Frame(control_frame)
        button_frame.pack()
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ Start Detection",
            command=self._on_start_detection_click,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ Stop Detection",
            command=self._on_stop_detection_click,
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=5)
    
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
    
    def _create_info_section(self):
        """Create info section with instructions"""
        info_frame = tk.Frame(self.window)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        info_text = ("Instructions:\n• Start detection before launching Dota 2\n"
                    "• Detection stops automatically after finding a match\n"
                    "• Use Test Sound to verify your audio settings\n\n"
                    "Keyboard Shortcuts: F1=Start | F2=Stop | F3=Test Sound | F4=Manual Screenshot")
        
        info_label = tk.Label(
            info_frame, 
            text=info_text, 
            font=("Arial", 8), 
            fg="gray", 
            justify="left"
        )
        info_label.pack()
    
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
        if self.status_label:
            self.status_label.config(text=text, fg=color)
    
    def set_detection_state(self, is_running: bool, match_found: bool = False):
        """Update detection state and UI"""
        self.is_running = is_running
        self.match_found = match_found
        
        if is_running:
            self.set_status("Status: Running Detection", "green")
            self.start_btn.pack_forget()
            self.stop_btn.pack(side="left", padx=5)
            self.stop_btn.config(state="normal")
        elif match_found:
            self.set_status("Status: Match Found! Detection Stopped", "blue")
            self.stop_btn.pack_forget()
            self.start_btn.pack(side="left", padx=5)
            self.start_btn.config(state="normal", text="▶ Start New Detection")
        else:
            self.set_status("Status: Stopped", "red")
            self.stop_btn.pack_forget()
            self.start_btn.pack(side="left", padx=5)
            self.start_btn.config(state="normal", text="▶ Start Detection")
    
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
                
                self.screenshot_label.config(image=photo)
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
            self.screenshot_label.config(image=None, text="No screenshot available")
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
        """Set audio device options"""
        if self.device_combo:
            self.device_combo['values'] = devices
            if 0 <= selected_index < len(devices):
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
