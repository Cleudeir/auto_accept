#!/usr/bin/env python3
"""
Test script to verify monitor detection and debug output
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from models.screenshot_model import ScreenshotModel

def test_monitor_detection():
    """Test monitor detection with debug output"""
    print("🚀 Starting monitor detection test...")
    print("=" * 50)
    
    # Create screenshot model
    screenshot_model = ScreenshotModel()
    
    # Test monitor detection
    print("\n1. Testing monitor detection:")
    monitor_index = screenshot_model.auto_detect_dota_monitor(show_debug=True)
    print(f"📋 Final result: Monitor {monitor_index}")
    
    # Test screenshot capture
    print("\n2. Testing screenshot capture:")
    print("=" * 50)
    img = screenshot_model.capture_monitor_screenshot(show_debug=True)
    if img:
        print(f"📏 Screenshot dimensions: {img.size}")
        print("✅ Test completed successfully!")
    else:
        print("❌ Screenshot capture failed!")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_monitor_detection()
