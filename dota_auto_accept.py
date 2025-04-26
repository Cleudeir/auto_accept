import pyautogui
import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import messagebox
import os
import sys
import requests
import re
from dotenv import load_dotenv
import win32gui
from screeninfo import get_monitors

class DotaAutoAccept:
    def __init__(self, root):
        # Determine the path to the .env file
        try:
            # If running as a bundled app, find the .env file in the temp directory
            base_path = sys._MEIPASS
            env_path = os.path.join(base_path, '.env')
        except Exception:
            # If running as a script, find the .env file in the current directory
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))

        # Load environment variables from the determined path
        load_dotenv(dotenv_path=env_path)

        self.root = root
        self.root.title("Dota 2 Auto Accept")
        self.root.geometry("450x230")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c3e50')

        self.reference_image_path = self.resource_path("dota.png")
        self.reference_image = cv2.imread(self.reference_image_path, cv2.IMREAD_COLOR)

        self.reference_image_plus_path = self.resource_path("dota2-plus.jpeg")
        self.reference_image_plus = cv2.imread(self.reference_image_plus_path, cv2.IMREAD_COLOR)

        if self.reference_image is None and self.reference_image_plus is None:
            messagebox.showerror("Error", f"Reference images not found: {self.reference_image_path} and {self.reference_image_plus_path}")
            sys.exit(1)

        # Load environment variables
        self.phone_number = os.getenv("PHONE_NUMBER")
        self.api_base_url = os.getenv("API_BASE_URL")
        self.api_password = os.getenv("API_PASSWORD")
        self.with_nine = os.getenv("NUMBER_WITH_NINE", False)

        if not self.phone_number or not self.api_base_url or not self.api_password:
            missing_vars = []
            if not self.phone_number: missing_vars.append("PHONE_NUMBER")
            if not self.api_base_url: missing_vars.append("API_BASE_URL")
            if not self.api_password: missing_vars.append("API_PASSWORD")
            messagebox.showerror("Error", f"Missing environment variables in .env file: {', '.join(missing_vars)}")
            sys.exit(1)

        self.running = False
        self.start_button = None
        self.stop_button = None
        self.phone_label = None
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

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(main_frame, text="Not Running", fg="white", bg='#2c3e50', font=("Arial", 16, "bold"))
        self.status_label.pack(pady=(0, 10))

        self.button_frame = tk.Frame(main_frame, bg='#2c3e50')
        self.button_frame.pack(pady=10)

        self.phone_label = tk.Label(main_frame, text=f"Phone Number: {self.phone_number}", fg="white", bg='#2c3e50', font=("Arial", 11))
        self.phone_label.pack(pady=(0, 10))

        self.start_button = tk.Button(
            self.button_frame, text="Start", command=self.start_script, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), width=10)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(
            self.button_frame, text="Stop", command=self.stop_script, bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), width=10)

        info_label = tk.Label(main_frame, text="Auto-accepting matches and sending notifications", fg="#f1c40f", bg='#2c3e50', font=("Arial", 10))
        info_label.pack(side=tk.BOTTOM, pady=(10, 0))

    def send_notification(self):
        parsed_encode_phone = re.sub(r'\D', '', self.phone_number)
        message = "Match Accepted in Dota 2 and stopped the script."
        
        url = f"{self.api_base_url}/enviar-mensagem?phone={parsed_encode_phone}&password={self.api_password}&message={message}&withNine={self.with_nine}"
        try:
            response = requests.get(url)
            print(f"Notification sent! Status: {response.status_code}")
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def find_and_press_enter(self):
        confidence = 0.6
        phone = self.phone_number

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
                    self.send_notification()
                    print(f"Match Accepted, WhatsApp notification sent to: {phone}")
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

def main():
    root = tk.Tk()
    app = DotaAutoAccept(root)
    app.start_script()
    root.mainloop()

if __name__ == "__main__":
    main()