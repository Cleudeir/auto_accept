import pyautogui
import cv2
import numpy as np
import time
import pygetwindow as gw
from PIL import ImageGrab
import mss

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

def main():
    filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
    if not save_dota2_monitor_screenshot(filename):
        # fallback to fullscreen screenshot
        filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
        save_fullscreen_screenshot(filename)

if __name__ == "__main__":
    main()