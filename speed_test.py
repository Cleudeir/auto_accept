#!/usr/bin/env python3
"""
Quick speed test to measure detection performance
"""
import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.screenshot_model import ScreenshotModel

def speed_test():
    """Test detection speed multiple times"""
    print("Screenshot Model Speed Test (No Logging)")
    print("=" * 50)
    
    screenshot_model = ScreenshotModel()
    
    # Test multiple runs
    times = []
    for i in range(5):
        start = time.time()
        monitor = screenshot_model.auto_detect_dota_monitor()
        end = time.time()
        elapsed = end - start
        times.append(elapsed)
        print(f"Run {i+1}: {elapsed:.3f}s -> Monitor {monitor}")
    
    avg_time = sum(times) / len(times)
    print(f"\nAverage detection time: {avg_time:.3f}s")
    print(f"Min: {min(times):.3f}s, Max: {max(times):.3f}s")
    
    if avg_time < 0.1:
        print("✅ EXCELLENT - Very fast detection")
    elif avg_time < 0.2:
        print("✅ GOOD - Fast detection")
    elif avg_time < 0.5:
        print("⚠️  MODERATE - Acceptable detection")
    else:
        print("❌ SLOW - Needs more optimization")

if __name__ == "__main__":
    speed_test()
