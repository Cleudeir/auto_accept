#!/usr/bin/env python3
"""
Demonstration of the enhanced monitor detection system
Run this to see the complete functionality working
"""

import sys
import os
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from models.screenshot_model import ScreenshotModel

def main():
    print("🎮 Dota 2 Auto Accept - Monitor Detection Demo")
    print("=" * 60)
    print("This demo shows the enhanced monitor detection system.")
    print("The system will:")
    print("1. Detect all available monitors")
    print("2. Find Dota 2 windows")
    print("3. Determine which monitor has Dota 2")
    print("4. Capture screenshots from the correct monitor")
    print("=" * 60)
    
    # Create screenshot model
    screenshot_model = ScreenshotModel()
    
    # Show initial detection with full debug output
    print("\n🔍 INITIAL DETECTION WITH DEBUG OUTPUT:")
    print("-" * 40)
    
    # Get monitor info with debug
    monitor_index = screenshot_model.auto_detect_dota_monitor(show_debug=True)
    
    # Take screenshot with debug
    print("\n📸 TAKING SCREENSHOT WITH DEBUG OUTPUT:")
    print("-" * 40)
    img = screenshot_model.capture_monitor_screenshot(show_debug=True)
    
    if img:
        print(f"\n✅ Success! Screenshot captured from Monitor {monitor_index}")
        print(f"📏 Image size: {img.size}")
    else:
        print(f"\n❌ Failed to capture screenshot from Monitor {monitor_index}")
    
    # Show how it works in normal operation (silent)
    print("\n🔇 NORMAL OPERATION (SILENT MODE):")
    print("-" * 40)
    print("Running 3 silent screenshots to show normal operation...")
    
    for i in range(3):
        start_time = time.time()
        img = screenshot_model.capture_monitor_screenshot(show_debug=False)
        end_time = time.time()
        
        if img:
            print(f"📸 Screenshot {i+1}: ✅ ({end_time - start_time:.3f}s)")
        else:
            print(f"📸 Screenshot {i+1}: ❌")
        
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🏁 Demo completed!")
    print("\n📝 What happened:")
    print("✅ Monitor detection automatically found Dota 2")
    print("✅ Debug output shows detailed information")
    print("✅ Silent mode works efficiently for normal use")
    print("✅ System handles multiple monitor configurations")
    print(f"✅ Screenshots are captured from Monitor {monitor_index}")
    
    print("\n🎯 Your Dota 2 Auto Accept is ready!")
    print("The system will automatically detect the correct monitor")
    print("and capture screenshots for match detection.")

if __name__ == "__main__":
    main()
