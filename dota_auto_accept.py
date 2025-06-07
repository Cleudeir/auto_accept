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

# Add Bluetooth support
try:
    from bleak import BleakClient, BleakScanner
    import asyncio
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    print("Bluetooth not available. Install bleak: pip install bleak")

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
        
        # Bluetooth configuration
        self.phone_bluetooth_address = ""  # Set your phone's MAC address here (e.g., "XX:XX:XX:XX:XX:XX")
        self.enable_bluetooth_notifications = False  # Set to True when you have configured the MAC address
        
        self.setup_ui()

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

    async def discover_bluetooth_devices(self):
        """Discover nearby Bluetooth Low Energy devices"""
        if not BLUETOOTH_AVAILABLE:
            print("Bluetooth not available")
            return []
            
        try:
            print("Discovering Bluetooth LE devices...")
            devices = await BleakScanner.discover()
            print("Found devices:")
            for device in devices:
                print(f"  {device.name} - {device.address}")
            return devices
        except Exception as e:
            print(f"Error discovering devices: {e}")
            return []

    def open_device_discovery_window(self):
        """Open a window to discover and select Bluetooth devices"""
        if not BLUETOOTH_AVAILABLE:
            messagebox.showerror("Error", "Bluetooth not available. Please install bleak: pip install bleak")
            return
            
        discovery_window = tk.Toplevel(self.root)
        discovery_window.title("Bluetooth Device Discovery")
        discovery_window.geometry("500x400")
        discovery_window.resizable(True, True)
        discovery_window.configure(bg='#34495e')
        discovery_window.transient(self.root)
        discovery_window.grab_set()
        
        # Center the window
        discovery_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        main_frame = tk.Frame(discovery_window, bg='#34495e', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Discover Bluetooth Devices", 
                              fg="white", bg='#34495e', font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Current device info
        current_frame = tk.Frame(main_frame, bg='#34495e')
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        current_label = tk.Label(current_frame, text="Current Device:", 
                                fg="white", bg='#34495e', font=("Arial", 10, "bold"))
        current_label.pack(anchor=tk.W)
        
        current_device = self.phone_bluetooth_address if self.phone_bluetooth_address else "None configured"
        self.current_device_label = tk.Label(current_frame, text=current_device, 
                                            fg="#f39c12", bg='#34495e', font=("Arial", 10))
        self.current_device_label.pack(anchor=tk.W)
        
        # Scan button
        scan_button = tk.Button(main_frame, text="Scan for Devices", 
                               command=lambda: self.start_device_scan(devices_listbox, status_label),
                               bg="#3498db", fg="white", font=("Arial", 11, "bold"))
        scan_button.pack(pady=10)
        
        # Status label
        status_label = tk.Label(main_frame, text="Click 'Scan for Devices' to start", 
                               fg="#95a5a6", bg='#34495e', font=("Arial", 10))
        status_label.pack(pady=(0, 10))
        
        # Devices list
        list_frame = tk.Frame(main_frame, bg='#34495e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_label = tk.Label(list_frame, text="Discovered Devices:", 
                             fg="white", bg='#34495e', font=("Arial", 10, "bold"))
        list_label.pack(anchor=tk.W)
        
        # Listbox with scrollbar
        listbox_frame = tk.Frame(list_frame, bg='#34495e')
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        devices_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set,
                                    bg='#2c3e50', fg='white', font=("Arial", 10),
                                    selectbackground='#3498db')
        devices_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=devices_listbox.yview)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#34495e')
        button_frame.pack(fill=tk.X, pady=10)
        
        select_button = tk.Button(button_frame, text="Select Device", 
                                 command=lambda: self.select_device(devices_listbox, discovery_window),
                                 bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
        select_button.pack(side=tk.LEFT, padx=(0, 10))
        
        manual_button = tk.Button(button_frame, text="Enter Manually", 
                                 command=lambda: self.enter_manual_address(discovery_window),
                                 bg="#f39c12", fg="white", font=("Arial", 10, "bold"))
        manual_button.pack(side=tk.LEFT, padx=(0, 10))
        
        close_button = tk.Button(button_frame, text="Close", 
                                command=discovery_window.destroy,
                                bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        close_button.pack(side=tk.RIGHT)
        
        # Store references for later use
        self.discovery_window_devices = []
        
    def start_device_scan(self, listbox, status_label):
        """Start scanning for Bluetooth devices in a separate thread"""
        status_label.config(text="Scanning for devices...", fg="#f39c12")
        listbox.delete(0, tk.END)
        
        def scan_thread():
            try:
                # Run the async discovery in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                devices = loop.run_until_complete(self.discover_bluetooth_devices())
                loop.close()
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_device_list(devices, listbox, status_label))
            except Exception as e:
                self.root.after(0, lambda: status_label.config(text=f"Scan failed: {str(e)}", fg="#e74c3c"))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def update_device_list(self, devices, listbox, status_label):
        """Update the device list in the UI"""
        listbox.delete(0, tk.END)
        self.discovery_window_devices = devices
        
        if not devices:
            status_label.config(text="No devices found", fg="#e67e22")
            listbox.insert(tk.END, "No devices discovered")
            return
        
        status_label.config(text=f"Found {len(devices)} device(s)", fg="#2ecc71")
        
        for device in devices:
            device_name = device.name if device.name else "Unknown Device"
            device_info = f"{device_name} ({device.address})"
            listbox.insert(tk.END, device_info)
    
    def select_device(self, listbox, window):
        """Select a device from the list"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a device from the list.")
            return
        
        if not self.discovery_window_devices:
            messagebox.showwarning("No Devices", "No devices available to select.")
            return
        
        selected_index = selection[0]
        if selected_index >= len(self.discovery_window_devices):
            messagebox.showerror("Error", "Invalid device selection.")
            return
        
        selected_device = self.discovery_window_devices[selected_index]
        self.configure_bluetooth_device(selected_device.address, window)
    
    def enter_manual_address(self, window):
        """Allow manual entry of Bluetooth MAC address"""
        manual_window = tk.Toplevel(window)
        manual_window.title("Enter Bluetooth Address")
        manual_window.geometry("400x200")
        manual_window.configure(bg='#34495e')
        manual_window.transient(window)
        manual_window.grab_set()
        
        # Center the window
        manual_window.geometry("+%d+%d" % (window.winfo_rootx() + 50, window.winfo_rooty() + 50))
        
        frame = tk.Frame(manual_window, bg='#34495e', padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(frame, text="Enter Bluetooth MAC Address", 
                              fg="white", bg='#34495e', font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        info_label = tk.Label(frame, text="Format: XX:XX:XX:XX:XX:XX", 
                             fg="#95a5a6", bg='#34495e', font=("Arial", 10))
        info_label.pack(pady=(0, 10))
        
        entry = tk.Entry(frame, font=("Arial", 11), width=20)
        entry.pack(pady=10)
        entry.focus()
        
        if self.phone_bluetooth_address:
            entry.insert(0, self.phone_bluetooth_address)
        
        button_frame = tk.Frame(frame, bg='#34495e')
        button_frame.pack(pady=10)
        
        def save_address():
            address = entry.get().strip()
            if self.validate_mac_address(address):
                self.configure_bluetooth_device(address, window)
                manual_window.destroy()
            else:
                messagebox.showerror("Invalid Address", "Please enter a valid MAC address in format XX:XX:XX:XX:XX:XX")
        
        save_button = tk.Button(button_frame, text="Save", command=save_address,
                               bg="#2ecc71", fg="white", font=("Arial", 10, "bold"))
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=manual_window.destroy,
                                 bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        cancel_button.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        entry.bind('<Return>', lambda e: save_address())
    
    def validate_mac_address(self, address):
        """Validate MAC address format"""
        import re
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return re.match(pattern, address) is not None
    
    def configure_bluetooth_device(self, address, window):
        """Configure the selected Bluetooth device"""
        self.phone_bluetooth_address = address
        self.enable_bluetooth_notifications = True
        
        # Update the current device label if it exists
        if hasattr(self, 'current_device_label'):
            self.current_device_label.config(text=address)
        
        # Update the main UI bluetooth status
        if hasattr(self, 'bluetooth_status_label'):
            self.bluetooth_status_label.config(text=f"Bluetooth: {address[:17]}", fg="#2ecc71")
        
        messagebox.showinfo("Device Configured", 
                           f"Bluetooth device configured successfully!\nAddress: {address}\nNotifications: Enabled")
        window.destroy()

    def send_bluetooth_notification(self, message):
        """Send notification via Bluetooth to paired device"""
        if not self.enable_bluetooth_notifications or not BLUETOOTH_AVAILABLE:
            return False
            
        if not self.phone_bluetooth_address:
            print("Bluetooth MAC address not configured")
            return False
            
        try:
            print(f"Sending Bluetooth notification: {message}")
            # Use asyncio to run the async Bluetooth operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._send_bluetooth_async(message))
            loop.close()
            return result
        except Exception as e:
            print(f"Failed to send Bluetooth notification: {e}")
            return False
    
    async def _send_bluetooth_async(self, message):
        """Async helper for Bluetooth communication"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            full_message = f"[{timestamp}] Dota 2: {message}"
            
            # For demonstration - bleak is primarily for BLE, not classic Bluetooth
            # You might need a different approach for classic Bluetooth notifications
            print("Bluetooth notification prepared (bleak is for BLE)")
            print(f"Message: {full_message}")
            print("Note: For classic Bluetooth notifications, consider using Windows notifications instead")
            return True
        except Exception as e:
            print(f"Bluetooth async error: {e}")
            return False

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
                    pyautogui.press('enter')
                    print("Match Accepted!")
                    # Send Bluetooth notification
                    self.send_bluetooth_notification("Match Accepted!")
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

        # Bluetooth status
        bluetooth_frame = tk.Frame(main_frame, bg='#2c3e50')
        bluetooth_frame.pack(fill=tk.X, pady=(0, 10))
        
        bluetooth_status = "Enabled" if self.enable_bluetooth_notifications else "Disabled"
        bluetooth_color = "#2ecc71" if self.enable_bluetooth_notifications else "#e74c3c"
        device_info = self.phone_bluetooth_address[:17] if self.phone_bluetooth_address else "Not configured"
        
        self.bluetooth_status_label = tk.Label(bluetooth_frame, 
                                              text=f"Bluetooth: {device_info}", 
                                              fg=bluetooth_color, bg='#2c3e50', 
                                              font=("Arial", 10))
        self.bluetooth_status_label.pack(anchor=tk.W)        # Bluetooth configuration button
        bluetooth_config_button = tk.Button(bluetooth_frame, 
                                           text="Configure Bluetooth", 
                                           command=self.open_device_discovery_window,
                                           bg="#9b59b6", fg="white", 
                                           font=("Arial", 10, "bold"))
        bluetooth_config_button.pack(anchor=tk.E, pady=(5, 0))

        # Start/Stop buttons
        self.button_frame = tk.Frame(main_frame, bg='#2c3e50')
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(
            self.button_frame, text="Start", command=self.start_script, 
            bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), width=10)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_script, 
            bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), width=10)

        info_label = tk.Label(main_frame, text="Auto-accepting matches", 
                             fg="#f1c40f", bg='#2c3e50', font=("Arial", 10))
        info_label.pack(side=tk.BOTTOM, pady=(10, 0))

def main():
    root = tk.Tk()
    app = DotaAutoAccept(root)
    app.start_script()
    root.mainloop()

if __name__ == "__main__":
    main()