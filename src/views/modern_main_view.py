import os
import customtkinter as ctk
from PIL import Image, ImageTk
import datetime
import logging
from typing import Callable, Optional, List, Tuple

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernMainView:
    """Modern GUI view for the Dota 2 Auto Accept application using CustomTkinter"""
    
    def __init__(self, title: str = "Dota 2 Auto Accept - Control Panel", config_model=None):
        self.logger = logging.getLogger("Dota2AutoAccept.ModernMainView")
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
        self.match_percent_label = None
        self.match_name_label = None
        
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
        
        # Modern UI specific
        self.theme_mode = "dark"
        
    def create_window(self):
        """Create and setup the modern main window with responsive design"""
        self.window = ctk.CTk()
        self.window.title(self.title)
        
        # Get screen dimensions for responsive design
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate responsive dimensions based on screen size and resolution
        # Ensure minimum height of 800px for all screen sizes
        if screen_height <= 768:  # Small screens (laptops, tablets)
            window_width = min(800, int(screen_width * 0.9))
            window_height = max(800, min(int(screen_height * 0.9), 800))  # Force min 800px height
            min_width, min_height = 750, 800
        elif screen_height <= 1080:  # Medium screens (1080p)
            window_width = min(900, int(screen_width * 0.85))
            window_height = max(800, min(850, int(screen_height * 0.75)))
            min_width, min_height = 850, 800
        elif screen_height <= 1440:  # High resolution screens (1440p)
            window_width = min(1000, int(screen_width * 0.8))
            window_height = max(800, min(900, int(screen_height * 0.7)))
            min_width, min_height = 900, 800
        else:  # Ultra-high resolution screens (4K+)
            window_width = min(1100, int(screen_width * 0.75))
            window_height = max(800, min(950, int(screen_height * 0.65)))
            min_width, min_height = 950, 800
        
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
        self.window.resizable(True, True)  # Allow resizing for modern UX
        self.window.minsize(min_width, min_height)  # Dynamic minimum size

        # Set icon
        self._set_window_icon()

        # Create main layout with modern styling
        self._create_modern_layout()

        # Setup keyboard shortcuts and close handler
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

    def _create_modern_layout(self):
        """Create the modern layout with improved styling"""
        # Configure grid weights for responsive design
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Main container with padding
        self.main_container = ctk.CTkFrame(self.window, corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header section
        self._create_header_section()
        
        # Content area with left and right panels
        self._create_content_area()
        
        # Footer/Control buttons
        self._create_control_section()

    def _create_header_section(self):
        """Create modern header with status and theme toggle"""
        self.header_frame = ctk.CTkFrame(self.main_container, height=80, corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)

        # App title/logo area
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)
        
        self.app_title = ctk.CTkLabel(
            self.title_frame,
            text="🎮 Dota 2 Auto Accept",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.app_title.pack()

        # Status section
        self.status_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.status_frame.grid(row=0, column=1, sticky="ew", padx=20, pady=10)
        self.status_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Status: Stopped",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#ff4444", "#ff6666")  # (light mode, dark mode)
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        # Theme button only (removed settings toggle)
        self.controls_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=2, sticky="e", padx=20, pady=10)

        self.theme_btn = ctk.CTkButton(
            self.controls_frame,
            text="🌙",
            width=36,
            height=36,
            command=self._toggle_theme,
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.theme_btn.pack(side="left")

    def _create_content_area(self):
        """Create the main content area with left and right panels"""
        self.content_frame = ctk.CTkFrame(self.main_container, corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Left panel (main content)
        self.left_panel = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Create left panel content
        self._create_match_status_section()
        self._create_screenshot_section()

        # Right panel (settings) - permanently visible
        self.right_panel = ctk.CTkFrame(self.content_frame, width=300, corner_radius=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.content_frame.grid_columnconfigure(1, weight=0, minsize=300)
        
        self._create_settings_panel()

    def _create_match_status_section(self):
        """Create modern match status section"""
        # Status card
        self.status_card = ctk.CTkFrame(self.left_panel, corner_radius=10)
        self.status_card.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.status_card.grid_columnconfigure(0, weight=1)

        # Match progress section
        self.progress_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        self.progress_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        self.progress_frame.grid_columnconfigure(0, weight=1)

        # Progress bar
        self.match_percent_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=20,
            corner_radius=10
        )
        self.match_percent_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.match_percent_bar.set(0)

        # Match info
        self.match_info_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.match_info_frame.grid(row=1, column=0, sticky="ew")
        self.match_info_frame.grid_columnconfigure(0, weight=1)
        self.match_info_frame.grid_columnconfigure(1, weight=1)

        self.match_percent_text = ctk.CTkLabel(
            self.match_info_frame,
            text="0.0%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.match_percent_text.grid(row=0, column=0, sticky="w")

        self.match_name_label = ctk.CTkLabel(
            self.match_info_frame,
            text="No Match Detected",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2196f3", "#64b5f6")
        )
        self.match_name_label.grid(row=0, column=1, sticky="e")

        # Sensitivity slider
        self.sensitivity_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        self.sensitivity_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.sensitivity_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.sensitivity_frame,
            text="Detection Sensitivity:",
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.score_threshold_slider = ctk.CTkSlider(
            self.sensitivity_frame,
            from_=50,
            to=100,
            number_of_steps=50,
            command=self._on_score_threshold_change_event
        )
        self.score_threshold_slider.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.score_threshold_slider.set(70)

        self.score_threshold_value_label = ctk.CTkLabel(
            self.sensitivity_frame,
            text="70%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.score_threshold_value_label.grid(row=0, column=2, sticky="e")

    def _create_screenshot_section(self):
        """Create modern screenshot preview section"""
        # Screenshot card
        self.screenshot_card = ctk.CTkFrame(self.left_panel, corner_radius=10)
        self.screenshot_card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.screenshot_card.grid_columnconfigure(0, weight=1)
        self.screenshot_card.grid_rowconfigure(1, weight=1)

        # Screenshot header
        ctk.CTkLabel(
            self.screenshot_card,
            text="📸 Screenshot Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Screenshot display area
        self.screenshot_frame = ctk.CTkFrame(self.screenshot_card, corner_radius=10)
        self.screenshot_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.screenshot_frame.grid_columnconfigure(0, weight=1)
        self.screenshot_frame.grid_rowconfigure(0, weight=1)

        self.screenshot_label = ctk.CTkLabel(
            self.screenshot_frame,
            text="No screenshot taken yet",
            font=ctk.CTkFont(size=14),
            fg_color=("#f0f0f0", "#2b2b2b"),
            corner_radius=10
        )
        self.screenshot_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Timestamp
        self.timestamp_label = ctk.CTkLabel(
            self.screenshot_card,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray40")
        )
        self.timestamp_label.grid(row=2, column=0, sticky="e", padx=20, pady=(0, 15))

    def _create_settings_panel(self):
        """Create modern settings panel"""
        if not hasattr(self, 'right_panel'):
            return

        # Settings header
        settings_header = ctk.CTkLabel(
            self.right_panel,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_header.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Audio settings
        self._create_modern_audio_settings()
        
        # Monitor settings  
        self._create_modern_monitor_settings()

    def _create_modern_audio_settings(self):
        """Create modern audio settings section"""
        # Audio card
        self.audio_card = ctk.CTkFrame(self.right_panel, corner_radius=10)
        self.audio_card.grid(row=1, column=0, sticky="ew", padx=15, pady=10)
        self.audio_card.grid_columnconfigure(0, weight=1)

        # Audio header
        ctk.CTkLabel(
            self.audio_card,
            text="🔊 Audio Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Device selection
        ctk.CTkLabel(
            self.audio_card,
            text="Output Device:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 5))

        self.device_combo = ctk.CTkComboBox(
            self.audio_card,
            command=self._on_device_change_event,
            font=ctk.CTkFont(size=12)
        )
        self.device_combo.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Volume control
        ctk.CTkLabel(
            self.audio_card,
            text="Volume:",
            font=ctk.CTkFont(size=12)
        ).grid(row=3, column=0, sticky="w", padx=15, pady=(0, 5))

        self.volume_slider = ctk.CTkSlider(
            self.audio_card,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._on_volume_change_event
        )
        self.volume_slider.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 15))

    def _create_modern_monitor_settings(self):
        """Create modern monitor settings section"""
        # Monitor card
        self.monitor_card = ctk.CTkFrame(self.right_panel, corner_radius=10)
        self.monitor_card.grid(row=2, column=0, sticky="ew", padx=15, pady=10)
        self.monitor_card.grid_columnconfigure(0, weight=1)

        # Monitor header
        ctk.CTkLabel(
            self.monitor_card,
            text="🖥️ Monitor Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Monitor selection
        ctk.CTkLabel(
            self.monitor_card,
            text="Capture Monitor:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 5))

        self.monitor_combo = ctk.CTkComboBox(
            self.monitor_card,
            command=self._on_monitor_change_event,
            font=ctk.CTkFont(size=12)
        )
        self.monitor_combo.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Always on top option
        self.always_on_top_var = ctk.BooleanVar()
        self.always_on_top_check = ctk.CTkCheckBox(
            self.monitor_card,
            text="Keep window on top",
            variable=self.always_on_top_var,
            command=self._on_always_on_top_change_event,
            font=ctk.CTkFont(size=12)
        )
        self.always_on_top_check.grid(row=3, column=0, sticky="w", padx=15, pady=(0, 15))

    def _create_control_section(self):
        """Create modern control buttons section"""
        self.control_frame = ctk.CTkFrame(self.main_container, height=80, corner_radius=10)
        self.control_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_propagate(False)

        # Button container
        self.button_container = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        self.button_container.grid(row=0, column=0, sticky="", padx=20, pady=15)

        # Control buttons with modern styling and improved responsiveness
        self.start_btn = ctk.CTkButton(
            self.button_container,
            text="▶️ Start",
            command=self._on_start_detection_click,
            width=110,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#4caf50", "#45a049"),
            hover_color=("#45a049", "#3d8b40"),
            corner_radius=8
        )
        self.start_btn.grid(row=0, column=0, padx=8)

        self.stop_btn = ctk.CTkButton(
            self.button_container,
            text="⏹️ Stop",
            command=self._on_stop_detection_click,
            width=110,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#d32f2f", "#b71c1c"),
            corner_radius=8
        )
        # Initially hidden
        
        self.test_sound_btn = ctk.CTkButton(
            self.button_container,
            text="🎵 Sound",
            command=self._on_test_sound_click,
            width=100,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#ff9800", "#f57c00"),
            hover_color=("#f57c00", "#ef6c00"),
            corner_radius=8
        )
        self.test_sound_btn.grid(row=0, column=2, padx=8)

        self.take_screenshot_btn = ctk.CTkButton(
            self.button_container,
            text="📷 Screenshot",
            command=self._on_take_screenshot_click,
            width=100,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#2196f3", "#1976d2"),
            hover_color=("#1976d2", "#1565c0"),
            corner_radius=8
        )
        self.take_screenshot_btn.grid(row=0, column=3, padx=8)

    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.theme_mode == "dark":
            ctk.set_appearance_mode("light")
            self.theme_mode = "light"
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_mode = "dark"
            self.theme_btn.configure(text="🌙")

    # Event handlers and utility methods
    def _on_start_detection_click(self):
        """Handle start detection button click"""
        if self.on_start_detection:
            self.on_start_detection()

    def _on_stop_detection_click(self):
        """Handle stop detection button click"""
        if self.on_stop_detection:
            self.on_stop_detection()

    def _on_test_sound_click(self):
        """Handle test sound button click"""
        if self.on_test_sound:
            self.on_test_sound()

    def _on_take_screenshot_click(self):
        """Handle take screenshot button click"""
        if self.on_take_screenshot:
            self.on_take_screenshot()

    def _on_device_change_event(self, choice):
        """Handle device selection change"""
        if self.on_device_change:
            self.on_device_change(choice)

    def _on_volume_change_event(self, value):
        """Handle volume slider change"""
        if self.on_volume_change:
            self.on_volume_change(int(value))

    def _on_monitor_change_event(self, choice):
        """Handle monitor selection change"""
        if self.on_monitor_change:
            self.on_monitor_change(choice)

    def _on_always_on_top_change_event(self):
        """Handle always on top checkbox change"""
        if self.on_always_on_top_change:
            self.on_always_on_top_change(self.always_on_top_var.get())

    def _on_score_threshold_change_event(self, value):
        """Handle sensitivity slider change"""
        percent = int(value)
        self.score_threshold_value_label.configure(text=f"{percent}%")
        if hasattr(self, 'on_score_threshold_change') and self.on_score_threshold_change:
            self.on_score_threshold_change(percent / 100.0)

    def _on_window_closing(self):
        """Handle window closing event"""
        if self.on_closing:
            self.on_closing()
        self.window.destroy()

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

    # Status update methods
    def update_status(self, status: str):
        """Update status label"""
        if self.status_label:
            color_map = {
                "Running Detection": ("#4caf50", "#66bb6a"),
                "Stopped": ("#f44336", "#ef5350"),
                "Match Found": ("#ff9800", "#ffa726"),
                "Starting": ("#2196f3", "#42a5f5")
            }
            
            status_text = f"Status: {status}"
            colors = color_map.get(status, ("#666666", "#999999"))
            
            self.status_label.configure(text=status_text, text_color=colors)

    def set_detection_running(self, running: bool):
        """Update UI for detection running state"""
        self.is_running = running
        
        if running:
            self.start_btn.grid_remove()
            self.stop_btn.grid(row=0, column=1, padx=10)
            self.update_status("Running Detection")
        else:
            self.stop_btn.grid_remove()
            self.start_btn.grid(row=0, column=0, padx=10)
            self.update_status("Stopped")

    def update_screenshot(self, image_data, timestamp: str = None):
        """Update screenshot display"""
        if self.screenshot_label:
            try:
                # Handle both file path and Image object
                if isinstance(image_data, str):
                    # File path provided
                    if os.path.exists(image_data):
                        pil_image = Image.open(image_data)
                    else:
                        return
                elif hasattr(image_data, 'mode'):
                    # PIL Image object provided
                    pil_image = image_data
                else:
                    # No valid image data
                    return
                
                # Resize to fit display area while maintaining aspect ratio
                display_size = (400, 250)
                pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(pil_image)
                self.screenshot_label.configure(image=photo, text="")
                self.screenshot_label.image = photo  # Keep reference
                
                if timestamp and self.timestamp_label:
                    self.timestamp_label.configure(text=f"Captured: {timestamp}")
            except Exception as e:
                self.logger.error(f"Error updating screenshot: {e}")

    def set_match_percent_and_name(self, percent: float, name: str):
        """Update match percent and name"""
        self.current_match_percent = percent
        self.current_match_name = name
        
        # Update progress bar
        if self.match_percent_bar:
            self.match_percent_bar.set(percent / 100.0)
            
        # Update percentage text
        if self.match_percent_text:
            self.match_percent_text.configure(text=f"{percent:.1f}%")
            
        # Update match name
        if self.match_name_label:
            display_name = self._get_match_display_name(name)
            self.match_name_label.configure(text=display_name)

    def _get_match_display_name(self, name: str) -> str:
        """Return a user-friendly display name for each match type"""
        mapping = {
            "dota": "🎯 Match Found!",
            "dota2_plus": "⭐ Dota Plus Offer",
            "read_check": "✅ Read-Check Required",
            "long_time": "⏰ Long Wait Warning",
            "ad": "📢 Advertisement",
            "watch-game": "👁️ Watch Game Dialog",
            "none": "❌ No Match Detected"
        }
        return mapping.get(name, f"🔍 {name}")

    # Configuration methods
    def set_device_options(self, devices: List[str], selected_index: int = 0):
        """Set audio device options"""
        if self.device_combo:
            # Remove duplicates while preserving order
            unique_devices = []
            seen = set()
            for device in devices:
                if device not in seen:
                    unique_devices.append(device)
                    seen.add(device)
            
            self.device_combo.configure(values=unique_devices)
            if 0 <= selected_index < len(unique_devices):
                self.device_combo.set(unique_devices[selected_index])

    def set_monitor_options(self, monitors: List[str], selected_index: int = 0):
        """Set monitor options"""
        if self.monitor_combo:
            self.monitor_combo.configure(values=monitors)
            if 0 <= selected_index < len(monitors):
                self.monitor_combo.set(monitors[selected_index])

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

    def set_score_threshold(self, percent: float):
        """Set the score threshold slider value (0-1 float)"""
        value = max(50, min(100, int(percent * 100)))
        if self.score_threshold_slider:
            self.score_threshold_slider.set(value)
        if self.score_threshold_value_label:
            self.score_threshold_value_label.configure(text=f"{value}%")

    def show_error(self, title: str, message: str):
        """Show error message"""
        from tkinter import messagebox
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str):
        """Show info message"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)

    def mainloop(self):
        """Start the GUI main loop"""
        if self.window:
            self.window.mainloop()

    def after(self, delay: int, callback: Callable):
        """Schedule a callback after delay milliseconds"""
        if self.window:
            self.window.after(delay, callback)

    def set_detection_state(self, is_running: bool, match_found: bool):
        """Set detection state for compatibility with MainController"""
        self.set_detection_running(is_running)
        self.match_found = match_found

    def update_logs(self, log_content: str):
        """Update log viewer content (compatibility method)"""
        # Modern UI doesn't have a log viewer, but we keep the method for compatibility
        pass
