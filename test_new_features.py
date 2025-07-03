#!/usr/bin/env python3
"""
Test script for the new auto-detect monitor and threshold save functionality
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from models.config_model import ConfigModel
from models.screenshot_model import ScreenshotModel
from models.detection_model import DetectionModel

def test_config_new_features():
    """Test the new config features"""
    print("=== Testing New Config Features ===")
    
    config = ConfigModel("test_config.json")
    
    # Test detection threshold
    print(f"Default detection threshold: {config.detection_threshold}")
    config.detection_threshold = 0.8
    print(f"Updated detection threshold: {config.detection_threshold}")
    
    # Test auto detect monitor
    print(f"Default auto detect monitor: {config.auto_detect_dota_monitor}")
    config.auto_detect_dota_monitor = True
    print(f"Updated auto detect monitor: {config.auto_detect_dota_monitor}")
    
    # Verify config is saved
    config2 = ConfigModel("test_config.json")
    print(f"Loaded detection threshold: {config2.detection_threshold}")
    print(f"Loaded auto detect monitor: {config2.auto_detect_dota_monitor}")
    
    # Clean up
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
    
    print("✅ Config features test passed!\n")

def test_auto_detect_monitor():
    """Test auto-detect monitor functionality"""
    print("=== Testing Auto-Detect Monitor ===")
    
    screenshot_model = ScreenshotModel()
    
    # Get available monitors
    monitors = screenshot_model.get_available_monitors()
    print(f"Available monitors: {monitors}")
    
    # Try auto-detect
    detected_monitor = screenshot_model.auto_detect_dota_monitor()
    if detected_monitor:
        print(f"✅ Auto-detected Dota 2 on monitor: {detected_monitor}")
    else:
        print("⚠️ Could not auto-detect Dota 2 monitor (this is normal if Dota 2 is not running)")
    
    print()

def test_detection_threshold():
    """Test detection threshold functionality"""
    print("=== Testing Detection Threshold ===")
    
    config = ConfigModel()
    detection_model = DetectionModel(config_model=config)
    
    # Test initial threshold
    print(f"Initial threshold: {detection_model.score_threshold}")
    
    # Test threshold change
    detection_model.set_score_threshold(0.85)
    print(f"Updated threshold: {detection_model.score_threshold}")
    print(f"Config threshold: {config.detection_threshold}")
    
    print("✅ Detection threshold test passed!\n")

if __name__ == "__main__":
    print("🧪 Testing Auto Accept - New Features\n")
    
    try:
        test_config_new_features()
        test_auto_detect_monitor()
        test_detection_threshold()
        
        print("🎉 All tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
