#!/usr/bin/env python3
"""
Test script to verify screenshot model performance improvements
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.screenshot_model_new import ScreenshotModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_screenshot_performance():
    """Test screenshot model performance"""
    print("Testing Screenshot Model Performance...")
    
    # Create screenshot model (this should clean up old files)
    start_time = time.time()
    screenshot_model = ScreenshotModel()
    init_time = time.time() - start_time
    print(f"Screenshot model initialization time: {init_time:.3f} seconds")
    
    # Test monitor detection speed
    start_time = time.time()
    detected_monitor = screenshot_model.auto_detect_dota_monitor()
    detection_time = time.time() - start_time
    print(f"Monitor detection time: {detection_time:.3f} seconds")
    print(f"Detected monitor: {detected_monitor}")
    
    # Test screenshot capture speed
    start_time = time.time()
    screenshot = screenshot_model.capture_monitor_screenshot()
    capture_time = time.time() - start_time
    print(f"Screenshot capture time: {capture_time:.3f} seconds")
    print(f"Screenshot captured: {screenshot is not None}")
    
    # Test monitor list
    start_time = time.time()
    monitors = screenshot_model.get_available_monitors()
    monitor_list_time = time.time() - start_time
    print(f"Monitor list time: {monitor_list_time:.3f} seconds")
    print(f"Available monitors: {len(monitors)}")
    for i, (name, idx) in enumerate(monitors):
        print(f"  {i+1}: {name}")
    
    # Test cleanup method
    start_time = time.time()
    screenshot_model.cleanup_old_screenshots(1)  # Clean files older than 1 hour
    cleanup_time = time.time() - start_time
    print(f"Cleanup time: {cleanup_time:.3f} seconds")
    
    total_time = init_time + detection_time + capture_time + monitor_list_time + cleanup_time
    print(f"Total test time: {total_time:.3f} seconds")
    
    # Performance benchmarks
    print("\nPerformance Analysis:")
    if detection_time < 0.1:
        print("✅ Monitor detection is FAST (< 0.1s)")
    elif detection_time < 0.5:
        print("⚠️  Monitor detection is MODERATE (< 0.5s)")
    else:
        print("❌ Monitor detection is SLOW (> 0.5s)")
    
    if capture_time < 0.1:
        print("✅ Screenshot capture is FAST (< 0.1s)")
    elif capture_time < 0.5:
        print("⚠️  Screenshot capture is MODERATE (< 0.5s)")
    else:
        print("❌ Screenshot capture is SLOW (> 0.5s)")
    
    if init_time < 0.1:
        print("✅ Initialization is FAST (< 0.1s)")
    elif init_time < 0.5:
        print("⚠️  Initialization is MODERATE (< 0.5s)")
    else:
        print("❌ Initialization is SLOW (> 0.5s)")
    
    print("\nScreenshot performance test completed!")

if __name__ == "__main__":
    try:
        test_screenshot_performance()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
