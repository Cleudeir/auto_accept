#!/usr/bin/env python3
"""
Test the cleaned up screenshot_model_old.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.screenshot_model_old import ScreenshotModel

def test_cleaned_model():
    """Test the cleaned up screenshot model"""
    print("Testing Cleaned Screenshot Model")
    print("=" * 40)
    
    # Test initialization
    start = time.time()
    model = ScreenshotModel()
    init_time = time.time() - start
    print(f"✅ Initialization: {init_time:.3f}s")
    
    # Test monitor detection
    start = time.time()
    monitor = model.auto_detect_dota_monitor()
    detect_time = time.time() - start
    print(f"✅ Detection: {detect_time:.3f}s -> Monitor {monitor}")
    
    # Test monitor list
    start = time.time()
    monitors = model.get_available_monitors()
    list_time = time.time() - start
    print(f"✅ Monitor list: {list_time:.3f}s -> {len(monitors)} monitors")
    
    # Test screenshot capture
    start = time.time()
    screenshot = model.capture_monitor_screenshot()
    capture_time = time.time() - start
    print(f"✅ Screenshot: {capture_time:.3f}s -> {'Success' if screenshot else 'Failed'}")
    
    total_time = init_time + detect_time + list_time + capture_time
    print(f"\n📊 Total time: {total_time:.3f}s")
    
    if total_time < 0.5:
        print("🚀 FAST - Unnecessary code removed successfully!")
    else:
        print("⚠️  Still has room for optimization")

if __name__ == "__main__":
    test_cleaned_model()
