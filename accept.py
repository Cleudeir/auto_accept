import pyautogui
import cv2
import numpy as np
import time
import pygetwindow as gw
from PIL import ImageGrab
import mss
import os
from skimage.metrics import structural_similarity as ssim

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
            print("Detected match! Pressing Enter.")
            pyautogui.press('enter')
        time.sleep(1)  # Adjust interval as needed

def main():
    filename = f"dota2_monitor_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
    if not save_dota2_monitor_screenshot(filename):
        # fallback to fullscreen screenshot
        filename = f"fullscreen_screenshot_{time.strftime('%Y%m%d-%H%M%S')}.png"
        save_fullscreen_screenshot(filename)

if __name__ == "__main__":
    main_loop()
    
    